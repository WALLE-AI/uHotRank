"""
LLM 提供商统一接口
支持多个模型提供商的异步流式调用
"""
import os
import logging
from typing import AsyncIterator, Dict, Any, Optional, List
from abc import ABC, abstractmethod
from enum import Enum

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""
    OPENAI = "openai"
    SILICONFLOW = "siliconflow"
    ALIBABA = "alibaba"
    LOCAL = "local"


class BaseLLMProvider(ABC):
    """LLM 提供商基类"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60
    ):
        """
        初始化 LLM 提供商
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 默认模型名称
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        聊天补全接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称（可选，使用默认模型）
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式输出
            **kwargs: 其他参数
        
        Yields:
            str: 生成的文本片段
        """
        pass
    
    async def close(self):
        """关闭客户端连接"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 提供商（使用 OpenAI Python SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        timeout: int = 60
    ):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if base_url is None:
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        super().__init__(api_key, base_url, model, timeout)
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # 初始化 OpenAI 客户端
        try:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout
            )
            logger.info("OpenAI SDK 初始化成功")
        except ImportError:
            logger.warning("OpenAI SDK 未安装，将使用 httpx 客户端")
            self.openai_client = None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """OpenAI 聊天补全"""
        model = model or self.model
        
        # 优先使用 OpenAI SDK
        if self.openai_client:
            try:
                if stream:
                    stream_response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                        **kwargs
                    )
                    
                    async for chunk in stream_response:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if delta.content:
                                yield delta.content
                else:
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False,
                        **kwargs
                    )
                    
                    if response.choices:
                        content = response.choices[0].message.content
                        if content:
                            yield content
                
                return
                
            except Exception as e:
                logger.error(f"OpenAI SDK 调用失败: {e}")
                raise
        
        # 回退到 httpx 客户端
        logger.info("使用 httpx 客户端调用 OpenAI API")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            if stream:
                async with self.client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                yield content
                
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        await super().close()
        if self.openai_client:
            await self.openai_client.close()


class SiliconFlowProvider(BaseLLMProvider):
    """SiliconFlow 提供商（使用 OpenAI Python SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "Qwen/Qwen2.5-7B-Instruct",
        timeout: int = 60
    ):
        if api_key is None:
            api_key = os.getenv("SILICONFLOW_API_KEY")
        if base_url is None:
            base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        
        super().__init__(api_key, base_url, model, timeout)
        
        if not self.api_key:
            raise ValueError("SiliconFlow API key is required")
        
        # 初始化 OpenAI 客户端（SiliconFlow 兼容 OpenAI 格式）
        try:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout
            )
            logger.info("SiliconFlow 使用 OpenAI SDK 初始化成功")
        except ImportError:
            logger.warning("OpenAI SDK 未安装，将使用 httpx 客户端")
            self.openai_client = None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """SiliconFlow 聊天补全（兼容 OpenAI 格式）"""
        model = model or self.model
        
        # 优先使用 OpenAI SDK
        if self.openai_client:
            try:
                if stream:
                    stream_response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                        **kwargs
                    )
                    
                    async for chunk in stream_response:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if delta.content:
                                yield delta.content
                else:
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False,
                        **kwargs
                    )
                    
                    if response.choices:
                        content = response.choices[0].message.content
                        if content:
                            yield content
                
                return
                
            except Exception as e:
                logger.error(f"SiliconFlow SDK 调用失败: {e}")
                raise
        
        # 回退到 httpx 客户端
        logger.info("使用 httpx 客户端调用 SiliconFlow API")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            if stream:
                async with self.client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                yield content
                
        except Exception as e:
            logger.error(f"SiliconFlow API 调用失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        await super().close()
        if self.openai_client:
            await self.openai_client.close()


class AlibabaProvider(BaseLLMProvider):
    """阿里百炼提供商"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "qwen-turbo",
        timeout: int = 60
    ):
        if api_key is None:
            api_key = os.getenv("ALIBABA_API_KEY")
        if base_url is None:
            base_url = os.getenv("ALIBABA_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        
        super().__init__(api_key, base_url, model, timeout)
        
        if not self.api_key:
            raise ValueError("Alibaba API key is required")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """阿里百炼聊天补全"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable" if stream else "disable"
        }
        
        payload = {
            "model": model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "result_format": "message",
                **kwargs
            }
        }
        
        if max_tokens:
            payload["parameters"]["max_tokens"] = max_tokens
        
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        try:
            if stream:
                async with self.client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            
                            if not data:
                                continue
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                output = chunk.get("output", {})
                                choices = output.get("choices", [])
                                
                                if choices:
                                    message = choices[0].get("message", {})
                                    content = message.get("content", "")
                                    
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                output = result.get("output", {})
                choices = output.get("choices", [])
                
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    yield content
                
        except Exception as e:
            logger.error(f"Alibaba API 调用失败: {e}")
            raise


class LocalProvider(BaseLLMProvider):
    """本地私有化部署提供商（使用 OpenAI Python SDK）"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "local-model",
        timeout: int = 60
    ):
        if base_url is None:
            base_url = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:8000/v1")
        if api_key is None:
            api_key = os.getenv("LOCAL_LLM_API_KEY", "dummy")  # 本地可能不需要 key
        
        super().__init__(api_key, base_url, model, timeout)
        
        # 初始化 OpenAI 客户端
        try:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout
            )
            logger.info(f"LocalProvider 使用 OpenAI SDK 初始化成功: {self.base_url}")
        except ImportError:
            logger.warning("OpenAI SDK 未安装，将使用 httpx 客户端")
            self.openai_client = None
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """本地模型聊天补全（使用 OpenAI SDK）"""
        model = model or self.model
        
        # 如果有 OpenAI SDK，使用 SDK
        if self.openai_client:
            try:
                if stream:
                    # 流式调用
                    stream_response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                        **kwargs
                    )
                    
                    async for chunk in stream_response:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if delta.content:
                                yield delta.content
                else:
                    # 非流式调用
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False,
                        **kwargs
                    )
                    
                    if response.choices:
                        content = response.choices[0].message.content
                        if content:
                            yield content
                
                return
                
            except Exception as e:
                logger.error(f"OpenAI SDK 调用失败: {e}")
                raise
        
        # 如果没有 OpenAI SDK，使用 httpx 客户端（回退方案）
        logger.info("使用 httpx 客户端调用本地 LLM")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key and self.api_key != "dummy":
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            if stream:
                async with self.client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await self.client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                yield content
                
        except Exception as e:
            logger.error(f"Local LLM API 调用失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        await super().close()
        if self.openai_client:
            await self.openai_client.close()


class LLMFactory:
    """LLM 提供商工厂类"""
    
    _providers = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.SILICONFLOW: SiliconFlowProvider,
        LLMProvider.ALIBABA: AlibabaProvider,
        LLMProvider.LOCAL: LocalProvider,
    }
    
    @classmethod
    def create(
        cls,
        provider: LLMProvider,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60
    ) -> BaseLLMProvider:
        """
        创建 LLM 提供商实例
        
        Args:
            provider: 提供商类型
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
            timeout: 超时时间
        
        Returns:
            BaseLLMProvider: 提供商实例
        """
        if provider not in cls._providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_class = cls._providers[provider]
        kwargs = {"timeout": timeout}
        
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        if model:
            kwargs["model"] = model
        
        return provider_class(**kwargs)
    
    @classmethod
    def get_default_provider(cls) -> BaseLLMProvider:
        """
        获取默认提供商（从环境变量读取）
        
        Returns:
            BaseLLMProvider: 默认提供商实例
        """
        provider_name = os.getenv("DEFAULT_LLM_PROVIDER", "siliconflow").lower()
        
        try:
            provider = LLMProvider(provider_name)
            return cls.create(provider)
        except ValueError:
            logger.warning(f"Unknown provider: {provider_name}, using SiliconFlow")
            return cls.create(LLMProvider.SILICONFLOW)


# 便捷函数
async def chat_completion_stream(
    messages: List[Dict[str, str]],
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> AsyncIterator[str]:
    """
    便捷的流式聊天补全函数
    
    Args:
        messages: 消息列表
        provider: 提供商类型（可选，使用默认）
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        **kwargs: 其他参数
    
    Yields:
        str: 生成的文本片段
    
    Example:
        messages = [{"role": "user", "content": "你好"}]
        async for chunk in chat_completion_stream(messages):
            print(chunk, end="", flush=True)
    """
    if provider:
        llm = LLMFactory.create(provider)
    else:
        llm = LLMFactory.get_default_provider()
    
    try:
        async for chunk in llm.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        ):
            yield chunk
    finally:
        await llm.close()


async def chat_completion(
    messages: List[Dict[str, str]],
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str:
    """
    便捷的非流式聊天补全函数
    
    Args:
        messages: 消息列表
        provider: 提供商类型（可选，使用默认）
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        **kwargs: 其他参数
    
    Returns:
        str: 完整的生成文本
    
    Example:
        messages = [{"role": "user", "content": "你好"}]
        response = await chat_completion(messages)
        print(response)
    """
    result = []
    async for chunk in chat_completion_stream(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    ):
        result.append(chunk)
    
    return "".join(result)
