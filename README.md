# UHotRank

热门文章爬取与技术内容检测系统

## 功能特性

- 🕷️ 爬取 TopHub 热门文章
- 🧹 智能内容过滤（去除网页元素，只保留正文）
- 🤖 AI 技术内容检测（识别开源项目、大模型、RAG、Agent 等技术）
- 🧠 LLM 内容分析（关键词提取、主题识别、情感分析、实体识别）
- 📊 Elasticsearch 9.2.1 集成（全文搜索、数据存储）
- 🔍 中文分词支持（需安装 IK 插件）
- 🔄 智能去重检测（URL、标题、内容相似度）
- 🚀 统一 LLM 接口（支持 OpenAI、SiliconFlow、阿里百炼、本地部署）

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置 Elasticsearch 连接信息：

```env
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password
```

### 3. 测试 Elasticsearch 连接

```bash
python test_elasticsearch.py
```

### 4. 运行爬虫（自动保存到 ES）

```bash
# 方式 1：直接运行（批量模式）
python main.py

# 方式 2：交互式选择模式
python run_crawler.py
```

### 5. 搜索文章

```bash
python search_example.py
```

## 使用方式

### 方式 1：一键运行（推荐）

```bash
python main.py
```

这会自动：
- 爬取 TopHub 所有文章
- 提取正文内容
- 检测技术相关性
- 批量保存到 Elasticsearch

### 方式 2：交互式运行

```bash
python run_crawler.py
```

提供 3 种模式：
1. 批量爬取所有文章（推荐，性能最好）
2. 爬取并筛选技术文章（同时保存到 ES 和 JSONL）
3. 只爬取技术文章到 ES（不保存 JSONL）

### 方式 3：编程方式

```python
from backend.agent.agent_today_data import scrape_all_articles_to_es

# 爬取并保存到 ES
result = scrape_all_articles_to_es(
    es_index_name="tophub_articles",
    batch_size=10
)

print(f"成功: {result['success']} 条")
```

## 项目结构

```
.
├── backend/
│   ├── agent/              # 爬虫和数据处理
│   │   └── agent_today_data.py  # 爬虫主逻辑、技术检测、ES 集成
│   ├── db/                 # 数据库操作
│   │   ├── __init__.py
│   │   └── elasticsearch_client.py  # ES 客户端和 CRUD 封装
│   └── utils/              # 工具函数
│       └── url_to_markdown.py  # 网页转 Markdown、内容过滤
├── main.py                 # 主程序（一键运行）
├── run_crawler.py          # 交互式爬虫（多种模式）
├── search_example.py       # 搜索示例
├── test_tech_detection.py  # 技术检测测试
├── test_elasticsearch.py   # ES 连接和 CRUD 测试
├── import_to_elasticsearch.py  # 从 JSONL 导入工具（可选）
├── USAGE.md                # 详细使用说明
├── ELASTICSEARCH_GUIDE.md  # ES 使用指南
├── TECH_DETECTION_README.md  # 技术检测说明
├── QUICKSTART.md           # 快速开始指南
├── .env.example            # 环境变量示例
└── pyproject.toml          # 项目依赖
```

## 核心功能

### 1. 网页内容过滤

`backend/utils/url_to_markdown.py` 中的 `Article._filter_markdown()` 方法：
- 移除所有图片和链接
- 过滤导航、广告、版权等网页元素
- 智能识别并移除噪音行
- 只保留正文内容

### 2. 技术内容检测

`backend/agent/agent_today_data.py` 中的检测功能：
- `detect_tech_content()` - 检测单篇文章
- `filter_tech_articles()` - 批量筛选技术文章
- `scrape_and_filter_tech_articles()` - 完整流程

支持检测的技术领域：
- 开源项目
- 大模型（GPT、Claude、LLM 等）
- RAG 技术
- Agent 技术
- AI 框架（LangChain、LlamaIndex 等）
- 模型训练（微调、LoRA、RLHF 等）
- 推理优化（vLLM、TensorRT 等）

### 3. 智能去重检测

`backend/db/elasticsearch_client.py` 中的去重功能：
- `check_duplicate()` - 综合检查文档是否重复
- `find_duplicate_by_url()` - URL 精确匹配
- `find_duplicate_by_title()` - 标题精确匹配
- `find_similar_documents()` - 内容相似度检测

支持三种检测方式：
- URL 匹配（最快，推荐）
- 标题匹配（快速）
- 内容相似度（可选，适合严格去重）

### 4. Elasticsearch 集成

`backend/db/elasticsearch_client.py` 提供：
- `ElasticsearchClient` - ES 客户端封装
- `ArticleRepository` - 文章数据仓库（CRUD 操作）

主要功能：
- 创建索引（支持中文分词）
- 单个/批量文档操作
- 关键词搜索
- 技术文章筛选
- 自动去重（基于 URL）

### 6. 内容分析

`backend/agent/agent_content_keyword_analysis.py` 使用 LLM 进行内容分析：
- 关键词提取（最多 10 个）
- 主题识别（最多 5 个）
- 文章摘要生成
- 情感分析（positive/neutral/negative）
- 分类识别
- 实体识别（人物、组织、地点、产品、技术等）

**分析结果存储在 Elasticsearch：**
```json
{
  "content_analysis": {
    "keywords": ["AI", "GPT-4", "OpenAI"],
    "topics": ["人工智能", "大语言模型"],
    "summary": "OpenAI 发布 GPT-4 Turbo...",
    "sentiment": "positive",
    "category": "科技",
    "entities": [
      {"name": "OpenAI", "type": "组织"},
      {"name": "GPT-4", "type": "产品"}
    ]
  }
}
```

**支持的搜索和统计：**
- 按关键词搜索
- 按主题搜索
- 按分类搜索
- 按情感搜索
- 关键词统计
- 主题统计
- 分类统计
- 情感统计

`backend/models/llm_provider.py` 提供统一的 LLM 接口：
- 支持多个提供商（OpenAI、SiliconFlow、阿里百炼、本地部署）
- 异步流式调用
- 使用 OpenAI Python SDK（自动回退到 httpx）
- 自动连接管理
- 便捷的 API 接口

支持的提供商：
- **OpenAI**: GPT-3.5, GPT-4 等（使用 OpenAI SDK）
- **SiliconFlow**: Qwen, DeepSeek 等开源模型（使用 OpenAI SDK）
- **阿里百炼**: Qwen-Turbo, Qwen-Plus 等
- **本地部署**: 兼容 OpenAI 格式的本地模型（使用 OpenAI SDK）

**OpenAI SDK 优势：**
- ✅ 更好的性能和稳定性
- ✅ 自动重试和错误处理
- ✅ 完整的类型提示
- ✅ 如果未安装会自动回退到 httpx

## 使用示例

### 示例 1：带内容分析的爬取

```bash
# 运行带内容分析的爬虫
python scrape_with_analysis.py
```

或编程方式：

```python
import asyncio
from scrape_with_analysis import scrape_with_content_analysis

async def main():
    result = await scrape_with_content_analysis(
        es_index_name="tophub_articles",
        enable_analysis=True,      # 启用内容分析
        check_duplicate=True,
        skip_duplicate=True
    )
    
    print(f"成功: {result['success']}")
    print(f"已分析: {result['analyzed']}")

asyncio.run(main())
```

### 示例 2：测试内容分析

```bash
# 测试内容分析功能
python test_content_analysis.py
```

### 示例 3：基于分析结果搜索

```bash
# 搜索和统计
python search_by_analysis.py
```

或编程方式：

```python
from backend.db import ElasticsearchClient, ArticleRepository

es_client = ElasticsearchClient()
repo = ArticleRepository(es_client)

# 按关键词搜索
results = repo.search_by_keywords(["AI", "GPT"], size=10)

# 按主题搜索
results = repo.search_by_topic("人工智能", size=10)

# 按分类搜索
results = repo.search_by_category("科技", size=10)

# 按情感搜索
results = repo.search_by_sentiment("positive", size=10)

# 获取统计信息
keywords = repo.get_keyword_statistics(top_n=20)
topics = repo.get_topic_statistics(top_n=10)
categories = repo.get_category_statistics()
sentiments = repo.get_sentiment_statistics()

es_client.close()
```

### 示例 4：一键爬取并保存

```python
# main.py
from backend.agent.agent_today_data import scrape_all_articles_to_es

result = scrape_all_articles_to_es(
    es_index_name="tophub_articles",
    batch_size=10
)
```

### 示例 5：爬取技术文章

```python
from backend.agent.agent_today_data import scrape_and_filter_tech_articles

# 同时保存到 ES 和 JSONL
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=True,
    save_to_jsonl=True
)

# 只保存到 ES
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=True,
    save_to_jsonl=False
)
```

### 示例 6：搜索文章

```python
from backend.db import ElasticsearchClient, ArticleRepository

es_client = ElasticsearchClient()
repo = ArticleRepository(es_client)

# 关键词搜索
results = repo.search_by_keyword("GPT", size=10)

# 搜索技术文章
tech_articles = repo.search_tech_articles(
    categories=["大模型", "RAG技术"],
    min_confidence=0.5,
    size=10
)

es_client.close()
```

### 示例 7：使用 LLM

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

## 文档

- [使用说明](USAGE.md) - 详细的使用指南和 API 文档
- [去重检测](DUPLICATE_DETECTION.md) - 文档去重功能说明
- [LLM 集成指南](LLM_GUIDE.md) - LLM 提供商使用指南
- [快速开始](QUICKSTART.md) - 快速安装和配置指南
- [Elasticsearch 集成指南](ELASTICSEARCH_GUIDE.md) - 详细的 API 文档和使用示例
- [技术内容检测说明](TECH_DETECTION_README.md) - 检测功能的详细说明

## 依赖

- Python >= 3.11
- Elasticsearch >= 9.2.1
- OpenAI SDK >= 1.0.0 (可选，推荐安装)
- 其他依赖见 `pyproject.toml`

**安装所有依赖：**
```bash
pip install -e .
```

**或使用 uv：**
```bash
uv sync
```

## 注意事项

1. **中文分词**：建议安装 Elasticsearch IK 插件以获得更好的中文搜索效果
2. **认证配置**：Elasticsearch 9.x 默认启用安全认证，需要配置用户名密码
3. **数据去重**：系统使用 URL 作为文档 ID，相同 URL 会自动覆盖

## License

MIT
