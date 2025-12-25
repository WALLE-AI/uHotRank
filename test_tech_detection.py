"""
测试技术内容检测功能
"""
from backend.agent.agent_today_data import detect_tech_content, filter_tech_articles

# 测试用例
test_cases = [
    {
        "title": "OpenAI 发布新版 GPT-4 Turbo 模型",
        "content": """
        OpenAI 今天宣布推出 GPT-4 Turbo 的最新版本，该模型在推理能力和上下文长度方面都有显著提升。
        新版本支持 128K token 的上下文窗口，并且推理速度提升了 40%。
        开发者可以通过 API 访问这个新模型，价格相比之前降低了 50%。
        """
    },
    {
        "title": "LangChain 0.1.0 正式发布，支持多智能体协作",
        "content": """
        流行的 LLM 应用开发框架 LangChain 发布了 0.1.0 版本。
        这个版本引入了全新的 Multi-Agent 系统，支持多个 AI Agent 之间的协作。
        同时还改进了 RAG（检索增强生成）的性能，新增了对向量数据库的原生支持。
        开发者可以通过 pip install langchain==0.1.0 进行升级。
        """
    },
    {
        "title": "今日股市行情分析",
        "content": """
        今天 A 股市场整体表现平稳，上证指数收涨 0.5%。
        科技股表现强劲，半导体板块领涨。
        分析师认为，在当前经济环境下，投资者应该保持谨慎。
        """
    },
    {
        "title": "新开源项目：vLLM 实现 LLM 推理加速",
        "content": """
        UC Berkeley 研究团队开源了 vLLM 项目，这是一个高性能的大语言模型推理引擎。
        vLLM 使用 PagedAttention 技术，可以将推理吞吐量提升 24 倍。
        项目已在 GitHub 上开源，支持 GPT、LLaMA、Falcon 等主流模型。
        该项目还支持量化和 LoRA 微调模型的部署。
        """
    }
]

print("=" * 80)
print("技术内容检测测试")
print("=" * 80)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n测试用例 {i}:")
    print(f"标题: {test_case['title']}")
    print("-" * 80)
    
    result = detect_tech_content(test_case['content'], test_case['title'])
    
    print(f"是否技术相关: {'✅ 是' if result['is_tech_related'] else '❌ 否'}")
    print(f"置信度: {result['confidence']}")
    print(f"匹配分类: {', '.join(result['categories']) if result['categories'] else '无'}")
    print(f"关键词: {', '.join(result['keywords'][:5]) if result['keywords'] else '无'}")
    print(f"摘要: {result['summary']}")
    print("=" * 80)

# 测试批量筛选
print("\n\n批量筛选测试:")
print("=" * 80)
tech_articles = filter_tech_articles(test_cases)
print(f"\n从 {len(test_cases)} 篇文章中筛选出 {len(tech_articles)} 篇技术相关文章")
