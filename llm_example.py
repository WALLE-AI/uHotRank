"""
LLM 使用示例
"""
import asyncio
from backend.llm import (
    LLMProvider,
    LLMFactory,
    chat_completion,
    chat_completion_stream,
)


async def example_1_simple_chat():
    """示例 1: 简单对话"""
    print("=" * 80)
    print("示例 1: 简单对话")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ]
    
    # 使用默认提供商
    response = await chat_completion(messages)
    print(f"\n回复: {response}\n")


async def example_2_stream_chat():
    """示例 2: 流式对话"""
    print("=" * 80)
    print("示例 2: 流式对话")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "请写一首关于春天的诗。"}
    ]
    
    print("\n回复: ", end="", flush=True)
    async for chunk in chat_completion_stream(messages):
        print(chunk, end="", flush=True)
    print("\n")


async def example_3_specific_provider():
    """示例 3: 使用特定提供商"""
    print("=" * 80)
    print("示例 3: 使用特定提供商")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "什么是大语言模型？"}
    ]
    
    # 使用 SiliconFlow
    print("\n使用 SiliconFlow:")
    response = await chat_completion(
        messages,
        provider=LLMProvider.SILICONFLOW,
        model="Qwen/Qwen2.5-7B-Instruct"
    )
    print(f"回复: {response}\n")


async def example_4_multi_turn():
    """示例 4: 多轮对话"""
    print("=" * 80)
    print("示例 4: 多轮对话")
    print("=" * 80)
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"}
    ]
    
    # 创建提供商实例
    llm = LLMFactory.get_default_provider()
    
    async with llm:
        # 第一轮
        messages.append({"role": "user", "content": "我想学习 Python，从哪里开始？"})
        print("\n用户: 我想学习 Python，从哪里开始？")
        print("助手: ", end="", flush=True)
        
        response1 = []
        async for chunk in llm.chat_completion(messages, stream=True):
            print(chunk, end="", flush=True)
            response1.append(chunk)
        print("\n")
        
        messages.append({"role": "assistant", "content": "".join(response1)})
        
        # 第二轮
        messages.append({"role": "user", "content": "有什么好的学习资源推荐吗？"})
        print("用户: 有什么好的学习资源推荐吗？")
        print("助手: ", end="", flush=True)
        
        async for chunk in llm.chat_completion(messages, stream=True):
            print(chunk, end="", flush=True)
        print("\n")


async def example_5_with_parameters():
    """示例 5: 使用参数控制"""
    print("=" * 80)
    print("示例 5: 使用参数控制")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "生成 3 个创意的产品名称。"}
    ]
    
    # 高温度（更有创意）
    print("\n高温度 (temperature=1.0):")
    response1 = await chat_completion(
        messages,
        temperature=1.0,
        max_tokens=100
    )
    print(f"回复: {response1}\n")
    
    # 低温度（更确定性）
    print("低温度 (temperature=0.3):")
    response2 = await chat_completion(
        messages,
        temperature=0.3,
        max_tokens=100
    )
    print(f"回复: {response2}\n")


async def example_6_tech_article_summary():
    """示例 6: 技术文章摘要"""
    print("=" * 80)
    print("示例 6: 技术文章摘要")
    print("=" * 80)
    
    article = """
    GPT-4 是 OpenAI 开发的大型多模态模型，能够接受图像和文本输入，并输出文本。
    在各种专业和学术基准测试中，GPT-4 展现了人类水平的性能。
    例如，它在模拟的律师资格考试中取得了前 10% 的成绩。
    GPT-4 是一个基于 Transformer 的模型，经过预训练以预测文档中的下一个 token。
    """
    
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的技术文章摘要助手。请用简洁的语言总结文章要点。"
        },
        {
            "role": "user",
            "content": f"请总结以下文章的要点：\n\n{article}"
        }
    ]
    
    print("\n文章摘要:")
    async for chunk in chat_completion_stream(messages, temperature=0.5):
        print(chunk, end="", flush=True)
    print("\n")


async def example_7_tech_detection():
    """示例 7: 技术内容检测"""
    print("=" * 80)
    print("示例 7: 技术内容检测")
    print("=" * 80)
    
    article_title = "LangChain 0.1.0 正式发布"
    article_content = """
    流行的 LLM 应用开发框架 LangChain 发布了 0.1.0 版本。
    这个版本引入了全新的 Multi-Agent 系统，支持多个 AI Agent 之间的协作。
    同时还改进了 RAG（检索增强生成）的性能。
    """
    
    messages = [
        {
            "role": "system",
            "content": "你是一个技术内容分析助手。请分析文章是否与以下技术领域相关：开源项目、大模型、RAG技术、Agent技术、AI框架。"
        },
        {
            "role": "user",
            "content": f"标题：{article_title}\n\n内容：{article_content}\n\n请分析这篇文章涉及哪些技术领域，并给出置信度评分（0-1）。"
        }
    ]
    
    print("\n分析结果:")
    response = await chat_completion(messages, temperature=0.3)
    print(response)
    print()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("LLM 使用示例")
    print("=" * 80)
    print()
    
    examples = [
        ("简单对话", example_1_simple_chat),
        ("流式对话", example_2_stream_chat),
        ("使用特定提供商", example_3_specific_provider),
        ("多轮对话", example_4_multi_turn),
        ("参数控制", example_5_with_parameters),
        ("技术文章摘要", example_6_tech_article_summary),
        ("技术内容检测", example_7_tech_detection),
    ]
    
    print("选择示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. 运行所有示例")
    
    choice = input("\n请输入选项 (0-7，默认 1): ").strip() or "1"
    print()
    
    try:
        choice_num = int(choice)
        
        if choice_num == 0:
            # 运行所有示例
            for name, func in examples:
                await func()
                print()
        elif 1 <= choice_num <= len(examples):
            # 运行选定的示例
            await examples[choice_num - 1][1]()
        else:
            print("无效的选项")
    except ValueError:
        print("无效的输入")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
