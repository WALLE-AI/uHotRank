"""
测试 OpenAI SDK 集成
"""
import asyncio
import logging
from backend.models import LLMProvider, LLMFactory

logging.basicConfig(level=logging.INFO)


async def test_openai_sdk():
    """测试 OpenAI SDK 是否正常工作"""
    print("=" * 80)
    print("测试 OpenAI SDK 集成")
    print("=" * 80)
    print()
    
    # 检查 OpenAI SDK 是否已安装
    try:
        import openai
        print(f"✅ OpenAI SDK 已安装: {openai.__version__}")
    except ImportError:
        print("⚠️  OpenAI SDK 未安装，将使用 httpx 客户端")
        print("   安装命令: pip install openai")
    print()
    
    # 测试提供商
    test_configs = [
        {
            "provider": LLMProvider.LOCAL,
            "name": "本地部署 (LocalProvider)",
            "model": "Qwen3-30B-A3B-Instruct-2507"
        },
        {
            "provider": LLMProvider.SILICONFLOW,
            "name": "SiliconFlow",
            "model": "Qwen/Qwen2.5-7B-Instruct"
        },
        {
            "provider": LLMProvider.OPENAI,
            "name": "OpenAI",
            "model": "gpt-3.5-turbo"
        },
    ]
    
    messages = [
        {"role": "user", "content": "你好，请用一句话介绍你自己。"}
    ]
    
    for config in test_configs:
        print("=" * 80)
        print(f"测试: {config['name']}")
        print("=" * 80)
        
        try:
            llm = LLMFactory.create(
                provider=config["provider"],
                model=config["model"]
            )
            
            # 检查是否使用 OpenAI SDK
            has_sdk = hasattr(llm, 'openai_client') and llm.openai_client is not None
            print(f"使用 OpenAI SDK: {'✅ 是' if has_sdk else '❌ 否 (使用 httpx)'}")
            print()
            
            # 测试流式调用
            print("流式输出:")
            print("-" * 80)
            print("回复: ", end="", flush=True)
            
            async with llm:
                async for chunk in llm.chat_completion(messages, stream=True):
                    print(chunk, end="", flush=True)
            
            print("\n")
            print("✅ 测试通过\n")
            
        except Exception as e:
            print(f"⚠️  跳过: {e}\n")
            continue


async def test_local_vllm():
    """测试本地 vLLM 部署"""
    print("=" * 80)
    print("测试本地 vLLM 部署")
    print("=" * 80)
    
    input("按 Enter 继续测试...")
    print()
    
    try:
        llm = LLMFactory.create(
            provider=LLMProvider.LOCAL,
            base_url="http://118.196.10.206:443/qwen3_instruct/v1",
            model="Qwen3-30B-A3B-Instruct-2507"
        )
        
        messages = [
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ]
        
        print("测试连接...")
        async with llm:
            print("回复: ", end="", flush=True)
            async for chunk in llm.chat_completion(messages, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
        
        print("✅ 本地 vLLM 测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n请检查:")
        print("1. vLLM 服务是否已启动")
        print("2. 端口是否正确 (默认 8000)")
        print("3. 模型是否已加载")


async def test_sdk_features():
    """测试 OpenAI SDK 的特性"""
    print("=" * 80)
    print("测试 OpenAI SDK 特性")
    print("=" * 80)
    print()
    
    try:
        import openai
        print(f"OpenAI SDK 版本: {openai.__version__}\n")
    except ImportError:
        print("⚠️  OpenAI SDK 未安装，跳过测试")
        return
    
    try:
        llm = LLMFactory.get_default_provider()
        
        if not hasattr(llm, 'openai_client') or llm.openai_client is None:
            print("⚠️  当前提供商不支持 OpenAI SDK")
            return
        
        messages = [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "请列举 3 个 Python 的优点。"}
        ]
        
        async with llm:
            # 测试流式输出
            print("1️⃣ 流式输出测试:")
            print("-" * 80)
            print("回复: ", end="", flush=True)
            
            async for chunk in llm.chat_completion(messages, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
            
            # 测试非流式输出
            print("2️⃣ 非流式输出测试:")
            print("-" * 80)
            
            response = []
            async for chunk in llm.chat_completion(messages, stream=False):
                response.append(chunk)
            
            print(f"回复: {''.join(response)}\n")
            
            # 测试参数控制
            print("3️⃣ 参数控制测试 (temperature=0.3, max_tokens=50):")
            print("-" * 80)
            print("回复: ", end="", flush=True)
            
            async for chunk in llm.chat_completion(
                messages,
                stream=True,
                temperature=0.3,
                max_tokens=50
            ):
                print(chunk, end="", flush=True)
            print("\n")
        
        print("✅ 所有特性测试通过")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("OpenAI SDK 集成测试")
    print("=" * 80)
    print()
    
    print("选择测试:")
    print("1. 测试所有提供商的 SDK 支持")
    print("2. 测试本地 vLLM 部署")
    print("3. 测试 SDK 特性")
    
    choice = input("\n请输入选项 (1/2/3，默认 1): ").strip() or "1"
    print()
    
    if choice == "1":
        await test_openai_sdk()
    elif choice == "2":
        await test_local_vllm()
    elif choice == "3":
        await test_sdk_features()
    else:
        print("无效的选项")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
