# LLM 提供商集成指南

## 功能概述

统一的 LLM 提供商接口，支持多个模型提供商的异步流式调用：

- ✅ **OpenAI** - GPT-3.5, GPT-4 等
- ✅ **SiliconFlow** - Qwen, DeepSeek 等开源模型
- ✅ **阿里百炼** - Qwen-Turbo, Qwen-Plus 等
- ✅ **本地部署** - 兼容 OpenAI 格式的本地模型

## 快速开始

### 1. 安装依赖

```bash
pip install httpx python-dotenv openai
```

**注意：** OpenAI SDK 是可选的，如果未安装会自动回退到 httpx 客户端。但推荐安装以获得更好的性能和稳定性。

### 2. 配置环境变量

编辑 `.env` 文件：

```env
# 默认提供商
DEFAULT_LLM_PROVIDER=siliconflow

# SiliconFlow 配置
SILICONFLOW_API_KEY=your_api_key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# OpenAI 配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 阿里百炼配置
ALIBABA_API_KEY=your_api_key

# 本地部署配置
LOCAL_LLM_BASE_URL=http://localhost:8000/v1
```

### 3. 基础使用

```python
import asyncio
from backend.models import chat_completion, chat_completion_stream

async def main():
    messages = [{"role": "user", "content": "你好"}]
    
    # 非流式
    response = await chat_completion(messages)
    print(response)
    
    # 流式
    async for chunk in chat_completion_stream(messages):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## 支持的提供商

### OpenAI SDK 支持

所有兼容 OpenAI 格式的提供商（OpenAI、SiliconFlow、LocalProvider）都支持使用 OpenAI Python SDK：

**优点：**
- ✅ 更好的性能和稳定性
- ✅ 自动重试和错误处理
- ✅ 完整的类型提示
- ✅ 官方维护和更新

**自动回退：**
- 如果未安装 OpenAI SDK，会自动使用 httpx 客户端
- 无需修改代码，完全透明

**安装：**
```bash
pip install openai
```

### 1. OpenAI

```python
from backend.models import LLMProvider, LLMFactory

llm = LLMFactory.create(
    provider=LLMProvider.OPENAI,
    api_key="your_api_key",
    model="gpt-3.5-turbo"
)

async with llm:
    async for chunk in llm.chat_completion(messages, stream=True):
        print(chunk, end="")
```

**支持的模型：**
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`

### 2. SiliconFlow

```python
llm = LLMFactory.create(
    provider=LLMProvider.SILICONFLOW,
    api_key="your_api_key",
    model="Qwen/Qwen2.5-7B-Instruct"
)
```

**支持的模型：**
- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-72B-Instruct`
- `deepseek-ai/DeepSeek-V2.5`
- `THUDM/glm-4-9b-chat`
- 更多模型见 [SiliconFlow 文档](https://siliconflow.cn/models)

### 3. 阿里百炼

```python
llm = LLMFactory.create(
    provider=LLMProvider.ALIBABA,
    api_key="your_api_key",
    model="qwen-turbo"
)
```

**支持的模型：**
- `qwen-turbo`
- `qwen-plus`
- `qwen-max`
- `qwen-max-longcontext`

### 4. 本地部署

```python
llm = LLMFactory.create(
    provider=LLMProvider.LOCAL,
    base_url="http://localhost:8000/v1",
    model="local-model"
)
```

**兼容的部署方式：**
- vLLM
- Text Generation Inference (TGI)
- Ollama (需要 OpenAI 兼容层)
- FastChat
- LocalAI

**使用 OpenAI SDK：**

LocalProvider 优先使用 OpenAI Python SDK（如果已安装），这提供了：
- 更好的性能和稳定性
- 自动重试和错误处理
- 类型提示和代码补全

如果未安装 OpenAI SDK，会自动回退到 httpx 客户端。

**示例：使用 vLLM 本地部署**

```bash
# 启动 vLLM 服务
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000
```

然后在代码中使用：

```python
from backend.models import LLMProvider, LLMFactory

llm = LLMFactory.create(
    provider=LLMProvider.LOCAL,
    base_url="http://localhost:8000/v1",
    model="Qwen/Qwen2.5-7B-Instruct"
)

async with llm:
    async for chunk in llm.chat_completion(messages, stream=True):
        print(chunk, end="")
```

## API 参考

### 便捷函数

#### chat_completion()

非流式聊天补全。

```python
response = await chat_completion(
    messages: List[Dict[str, str]],      # 消息列表
    provider: Optional[LLMProvider] = None,  # 提供商（可选）
    model: Optional[str] = None,         # 模型名称（可选）
    temperature: float = 0.7,            # 温度参数
    max_tokens: Optional[int] = None,    # 最大 token 数
    **kwargs                             # 其他参数
) -> str
```

#### chat_completion_stream()

流式聊天补全。

```python
async for chunk in chat_completion_stream(
    messages: List[Dict[str, str]],
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
):
    print(chunk, end="")
```

### 工厂类

#### LLMFactory.create()

创建提供商实例。

```python
llm = LLMFactory.create(
    provider: LLMProvider,               # 提供商类型
    api_key: Optional[str] = None,       # API 密钥
    base_url: Optional[str] = None,      # API 基础 URL
    model: Optional[str] = None,         # 模型名称
    timeout: int = 60                    # 超时时间（秒）
) -> BaseLLMProvider
```

#### LLMFactory.get_default_provider()

获取默认提供商（从环境变量读取）。

```python
llm = LLMFactory.get_default_provider()
```

### 提供商类

#### BaseLLMProvider.chat_completion()

聊天补全方法。

```python
async for chunk in llm.chat_completion(
    messages: List[Dict[str, str]],      # 消息列表
    model: Optional[str] = None,         # 模型名称
    temperature: float = 0.7,            # 温度参数
    max_tokens: Optional[int] = None,    # 最大 token 数
    stream: bool = True,                 # 是否流式输出
    **kwargs                             # 其他参数
):
    yield chunk
```

## 使用示例

### 示例 1：简单对话

```python
import asyncio
from backend.models import chat_completion

async def main():
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ]
    
    response = await chat_completion(messages)
    print(response)

asyncio.run(main())
```

### 示例 2：流式对话

```python
from backend.models import chat_completion_stream

async def main():
    messages = [
        {"role": "user", "content": "请写一首关于春天的诗。"}
    ]
    
    async for chunk in chat_completion_stream(messages):
        print(chunk, end="", flush=True)
    print()

asyncio.run(main())
```

### 示例 3：多轮对话

```python
from backend.models import LLMFactory

async def main():
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"}
    ]
    
    llm = LLMFactory.get_default_provider()
    
    async with llm:
        # 第一轮
        messages.append({"role": "user", "content": "我叫小明。"})
        
        response1 = []
        async for chunk in llm.chat_completion(messages, stream=True):
            print(chunk, end="")
            response1.append(chunk)
        print()
        
        messages.append({"role": "assistant", "content": "".join(response1)})
        
        # 第二轮
        messages.append({"role": "user", "content": "我叫什么名字？"})
        
        async for chunk in llm.chat_completion(messages, stream=True):
            print(chunk, end="")
        print()

asyncio.run(main())
```

### 示例 4：使用特定提供商

```python
from backend.models import LLMProvider, chat_completion

async def main():
    messages = [
        {"role": "user", "content": "什么是大语言模型？"}
    ]
    
    # 使用 SiliconFlow
    response = await chat_completion(
        messages,
        provider=LLMProvider.SILICONFLOW,
        model="Qwen/Qwen2.5-7B-Instruct"
    )
    print(response)

asyncio.run(main())
```

### 示例 5：参数控制

```python
async def main():
    messages = [
        {"role": "user", "content": "生成 3 个创意的产品名称。"}
    ]
    
    # 高温度（更有创意）
    response1 = await chat_completion(
        messages,
        temperature=1.0,
        max_tokens=100
    )
    
    # 低温度（更确定性）
    response2 = await chat_completion(
        messages,
        temperature=0.3,
        max_tokens=100
    )

asyncio.run(main())
```

### 示例 6：技术文章摘要

```python
async def main():
    article = """
    GPT-4 是 OpenAI 开发的大型多模态模型...
    """
    
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的技术文章摘要助手。"
        },
        {
            "role": "user",
            "content": f"请总结以下文章：\n\n{article}"
        }
    ]
    
    async for chunk in chat_completion_stream(messages, temperature=0.5):
        print(chunk, end="")

asyncio.run(main())
```

## 参数说明

### temperature

控制输出的随机性：
- **0.0-0.3**: 更确定性，适合事实性任务
- **0.7**: 平衡（默认）
- **1.0-2.0**: 更有创意，适合创作任务

### max_tokens

限制输出的最大 token 数：
- 不设置：使用模型默认值
- 设置较小值：控制成本和响应长度
- 设置较大值：允许更长的输出

### stream

是否使用流式输出：
- **True**: 逐字输出，用户体验更好
- **False**: 一次性返回完整结果

## 测试

### 运行测试

```bash
# 测试所有提供商
python test_llm_provider.py

# 运行示例
python llm_example.py
```

### 测试选项

1. 测试所有提供商
2. 测试便捷函数
3. 测试多轮对话
4. 测试默认提供商

## 最佳实践

### 1. 使用上下文管理器

```python
async with llm:
    # 使用 llm
    pass
# 自动关闭连接
```

### 2. 错误处理

```python
try:
    response = await chat_completion(messages)
except Exception as e:
    logger.error(f"LLM 调用失败: {e}")
    # 处理错误
```

### 3. 流式输出

对于用户交互场景，优先使用流式输出：

```python
async for chunk in chat_completion_stream(messages):
    print(chunk, end="", flush=True)
```

### 4. 多轮对话

保持消息历史：

```python
messages = [{"role": "system", "content": "..."}]

# 添加用户消息
messages.append({"role": "user", "content": "..."})

# 获取回复
response = await chat_completion(messages)

# 添加助手回复
messages.append({"role": "assistant", "content": response})
```

### 5. 成本控制

- 使用 `max_tokens` 限制输出长度
- 选择合适的模型（小模型更便宜）
- 使用本地部署（零成本）

## 常见问题

### Q1: 如何切换提供商？

修改 `.env` 文件中的 `DEFAULT_LLM_PROVIDER`，或在代码中指定：

```python
response = await chat_completion(
    messages,
    provider=LLMProvider.OPENAI
)
```

### Q2: 如何使用本地部署的模型？

配置 `LOCAL_LLM_BASE_URL`，然后：

```python
llm = LLMFactory.create(
    provider=LLMProvider.LOCAL,
    base_url="http://localhost:8000/v1"
)
```

### Q3: 流式输出卡住了怎么办？

检查：
1. 网络连接是否正常
2. API 密钥是否正确
3. 模型名称是否正确
4. 增加 `timeout` 参数

### Q4: 如何添加新的提供商？

1. 继承 `BaseLLMProvider`
2. 实现 `chat_completion` 方法
3. 在 `LLMFactory._providers` 中注册

### Q5: 支持哪些消息角色？

- `system`: 系统提示
- `user`: 用户消息
- `assistant`: 助手回复

## 性能优化

### 1. 连接复用

```python
llm = LLMFactory.get_default_provider()

async with llm:
    # 多次调用复用连接
    response1 = await llm.chat_completion(messages1)
    response2 = await llm.chat_completion(messages2)
```

### 2. 并发调用

```python
import asyncio

tasks = [
    chat_completion(messages1),
    chat_completion(messages2),
    chat_completion(messages3)
]

results = await asyncio.gather(*tasks)
```

### 3. 超时控制

```python
llm = LLMFactory.create(
    provider=LLMProvider.OPENAI,
    timeout=30  # 30 秒超时
)
```

## 下一步

- 查看 [test_llm_provider.py](test_llm_provider.py) 了解测试用例
- 查看 [llm_example.py](llm_example.py) 了解更多示例
- 集成到爬虫系统进行技术内容分析
