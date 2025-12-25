"""
测试 LLM 提供商
"""
import asyncio
import logging
from backend.models import (
    LLMProvider,
    LLMFactory,
    chat_completion,
    chat_completion_stream,
)

logging.basicConfig(level=logging.INFO)


async def test_provider(provider: LLMProvider, model: str = None):
    """测试单个提供商"""
    print("=" * 80)
    print(f"测试提供商: {provider.value}")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "你好，请用一句话介绍你自己。"}
    ]
    
    try:
        # 测试流式输出
        print("\n1️⃣ 流式输出测试:")
        print("-" * 80)
        
        llm = LLMFactory.create(provider, model=model)
        
        async with llm:
            print("回复: ", end="", flush=True)
            async for chunk in llm.chat_completion(
                messages=messages,
                temperature=0.7,
                stream=True
            ):
                print(chunk, end="", flush=True)
            print("\n")
        
        # 测试非流式输出
        print("2️⃣ 非流式输出测试:")
        print("-" * 80)
        
        response = await chat_completion(
            messages=messages,
            provider=provider,
            model=model,
            temperature=0.7
        )
        print(f"回复: {response}\n")
        
        print("✅ 测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()


async def test_all_providers():
    """测试所有提供商"""
    print("=" * 80)
    print("LLM 提供商测试")
    print("=" * 80)
    print()
    
    # 测试配置
    test_configs = [
        {
            "provider": LLMProvider.SILICONFLOW,
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "name": "SiliconFlow (Qwen2.5-7B)"
        },
        {
            "provider": LLMProvider.OPENAI,
            "model": "gpt-3.5-turbo",
            "name": "OpenAI (GPT-3.5)"
        },
        {
            "provider": LLMProvider.ALIBABA,
            "model": "qwen-turbo",
            "name": "阿里百炼 (Qwen-Turbo)"
        },
        {
            "provider": LLMProvider.LOCAL,
            "model": "Qwen3-30B-A3B-Instruct-2507",
            "name": "本地部署"
        },
    ]
    
    for config in test_configs:
        print(f"\n{'=' * 80}")
        print(f"测试: {config['name']}")
        print(f"{'=' * 80}\n")
        
        try:
            await test_provider(config["provider"], config["model"])
        except Exception as e:
            print(f"⚠️  跳过 {config['name']}: {e}\n")
            continue


async def test_convenience_functions():
    """测试便捷函数"""
    print("=" * 80)
    print("测试便捷函数")
    print("=" * 80)
    print()
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "请用一句话解释什么是大语言模型。"}
    ]
    
    try:
        # 测试流式便捷函数
        print("1️⃣ 流式便捷函数:")
        print("-" * 80)
        print("回复: ", end="", flush=True)
        
        async for chunk in chat_completion_stream(messages):
            print(chunk, end="", flush=True)
        print("\n")
        
        # 测试非流式便捷函数
        print("2️⃣ 非流式便捷函数:")
        print("-" * 80)
        
        response = await chat_completion(messages)
        print(f"回复: {response}\n")
        
        print("✅ 测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()


async def test_multi_turn_conversation():
    """测试多轮对话"""
    print("=" * 80)
    print("测试多轮对话")
    print("=" * 80)
    print()
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "我叫小明。"},
    ]
    
    try:
        llm = LLMFactory.get_default_provider()
        
        async with llm:
            # 第一轮
            print("用户: 我叫小明。")
            print("助手: ", end="", flush=True)
            
            response1 = []
            async for chunk in llm.chat_completion(messages, stream=True):
                print(chunk, end="", flush=True)
                response1.append(chunk)
            print("\n")
            
            # 添加助手回复到消息历史
            messages.append({"role": "assistant", "content": "".join(response1)})
            
            # 第二轮
            messages.append({"role": "user", "content": "我叫什么名字？"})
            print("用户: 我叫什么名字？")
            print("助手: ", end="", flush=True)
            
            async for chunk in llm.chat_completion(messages, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
        
        print("✅ 多轮对话测试通过\n")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("LLM 提供商测试套件")
    print("=" * 80)
    print()
    
    # 选择测试模式
    print("选择测试模式:")
    print("1. 测试所有提供商")
    print("2. 测试便捷函数")
    print("3. 测试多轮对话")
    print("4. 测试默认提供商")
    
    choice = input("\n请输入选项 (1/2/3/4，默认 4): ").strip() or "4"
    print()
    
    if choice == "1":
        await test_all_providers()
    elif choice == "2":
        await test_convenience_functions()
    elif choice == "3":
        await test_multi_turn_conversation()
    elif choice == "4":
        # 测试默认提供商
        llm = LLMFactory.get_default_provider()

        print(f"默认提供商: {llm.__class__.__name__}")
        print(f"默认模型: {llm.model}\n")
        
        messages = [{"role": "user", "content": "你是谁"}]
        
        async with llm:
            print("回复: ", end="", flush=True)
            async for chunk in llm.chat_completion(messages, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
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
