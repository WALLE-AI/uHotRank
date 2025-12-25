"""
测试内容分析功能
"""
import asyncio
import logging
from backend.agent.agent_content_keyword_analysis import (
    analyze_article_keywords,
    batch_analyze_articles,
    get_article_statistics
)
from backend.models import LLMProvider
import os

logging.basicConfig(level=logging.INFO)


async def test_single_article():
    """测试单篇文章分析"""
    print("=" * 80)
    print("测试单篇文章分析")
    print("=" * 80)
    print()
    
    title = "OpenAI 发布 GPT-4 Turbo：性能提升，成本降低"
    content = """
    OpenAI 今天宣布推出 GPT-4 Turbo，这是 GPT-4 的最新版本。
    新版本在多个方面都有显著提升：
    
    1. 上下文长度：支持 128K token 的上下文窗口，相当于 300 页文本
    2. 性能提升：推理速度提升 40%，响应更快
    3. 成本降低：API 价格相比之前降低 50%
    4. 知识更新：训练数据更新到 2024 年 4 月
    
    GPT-4 Turbo 还引入了新的功能，包括 JSON 模式、改进的函数调用等。
    开发者可以通过 OpenAI API 访问这个新模型。
    
    业界专家认为，这次更新将进一步推动 AI 应用的普及。
    """
    
    print(f"标题: {title}")
    print(f"内容长度: {len(content)} 字符\n")
    
    print("正在分析...")
    result = await analyze_article_keywords(title, content,provider=LLMProvider.LOCAL)
    
    print("\n分析结果:")
    print("-" * 80)
    print(f"✅ 分析成功: {result['analysis_success']}")
    print(f"\n🔑 关键词: {', '.join(result['keywords'])}")
    print(f"\n📚 主题: {', '.join(result['topics'])}")
    print(f"\n📝 摘要: {result['summary']}")
    print(f"\n😊 情感: {result['sentiment']}")
    print(f"\n📂 分类: {result['category']}")
    print(f"\n🏷️  实体:")
    for entity in result['entities']:
        print(f"   - {entity['name']} ({entity['type']})")
    print()


async def test_batch_analysis():
    """测试批量分析"""
    print("=" * 80)
    print("测试批量文章分析")
    print("=" * 80)
    print()
    
    articles = [
        {
            "title": "LangChain 0.1.0 正式发布",
            "content": "流行的 LLM 应用开发框架 LangChain 发布了 0.1.0 版本。这个版本引入了全新的 Multi-Agent 系统，支持多个 AI Agent 之间的协作。同时还改进了 RAG（检索增强生成）的性能。"
        },
        {
            "title": "A股今日收涨，科技股领涨",
            "content": "今天 A 股市场整体表现强劲，上证指数收涨 1.5%。科技股表现尤为突出，半导体板块领涨。分析师认为，在当前经济环境下，科技股仍有上涨空间。"
        },
        {
            "title": "新研究：AI 可以预测蛋白质结构",
            "content": "DeepMind 的 AlphaFold 3 在蛋白质结构预测方面取得了突破性进展。新模型可以预测蛋白质、DNA、RNA 等生物分子的结构，准确率达到 95%。这项技术将加速新药研发。"
        }
    ]
    
    print(f"待分析文章数: {len(articles)}\n")
    print("正在批量分析...")
    
    analyzed_articles = await batch_analyze_articles(articles, max_concurrent=2)
    
    print("\n分析结果:")
    print("=" * 80)
    
    for i, article in enumerate(analyzed_articles, 1):
        analysis = article.get('content_analysis', {})
        print(f"\n{i}. {article['title']}")
        print(f"   分类: {analysis.get('category', 'N/A')}")
        print(f"   关键词: {', '.join(analysis.get('keywords', [])[:5])}")
        print(f"   情感: {analysis.get('sentiment', 'N/A')}")
        print(f"   成功: {'✅' if analysis.get('analysis_success') else '❌'}")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("统计信息:")
    print("=" * 80)
    
    stats = get_article_statistics(analyzed_articles)
    
    print(f"\n总文章数: {stats['total_articles']}")
    print(f"已分析: {stats['analyzed_articles']}")
    print(f"分析率: {stats['analysis_rate']}")
    
    print(f"\n热门关键词:")
    for item in stats['top_keywords'][:10]:
        print(f"  - {item['keyword']}: {item['count']} 次")
    
    print(f"\n主题分布:")
    for item in stats['top_topics'][:5]:
        print(f"  - {item['topic']}: {item['count']} 次")
    
    print(f"\n分类统计:")
    for category, count in stats['categories'].items():
        print(f"  - {category}: {count} 篇")
    
    print(f"\n情感统计:")
    for sentiment, count in stats['sentiments'].items():
        print(f"  - {sentiment}: {count} 篇")
    print()


async def test_different_content_types():
    """测试不同类型的内容"""
    print("=" * 80)
    print("测试不同类型的内容")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "name": "技术文章",
            "title": "vLLM 实现 LLM 推理加速",
            "content": "UC Berkeley 研究团队开源了 vLLM 项目，这是一个高性能的大语言模型推理引擎。vLLM 使用 PagedAttention 技术，可以将推理吞吐量提升 24 倍。"
        },
        {
            "name": "新闻报道",
            "title": "某公司宣布裁员计划",
            "content": "某科技公司今天宣布将裁员 10%，涉及约 1000 名员工。公司表示这是为了应对经济下行压力。员工对此表示不满和担忧。"
        },
        {
            "name": "产品评测",
            "title": "iPhone 15 Pro 评测",
            "content": "iPhone 15 Pro 采用了全新的钛金属边框，重量更轻。A17 Pro 芯片性能强劲，相机系统也有显著提升。总体来说是一款优秀的旗舰手机。"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print("-" * 80)
        
        result = await analyze_article_keywords(
            test_case['title'],
            test_case['content']
        )
        
        print(f"标题: {test_case['title']}")
        print(f"分类: {result['category']}")
        print(f"情感: {result['sentiment']}")
        print(f"关键词: {', '.join(result['keywords'][:5])}")
        print(f"摘要: {result['summary']}")
    
    print()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("内容分析功能测试")
    print("=" * 80)
    print()
    
    print("选择测试:")
    print("1. 测试单篇文章分析")
    print("2. 测试批量分析")
    print("3. 测试不同类型内容")
    print("4. 运行所有测试")
    
    choice = input("\n请输入选项 (1/2/3/4，默认 1): ").strip() or "1"
    print()
    
    if choice == "1":
        await test_single_article()
    elif choice == "2":
        await test_batch_analysis()
    elif choice == "3":
        await test_different_content_types()
    elif choice == "4":
        await test_single_article()
        await test_batch_analysis()
        await test_different_content_types()
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
