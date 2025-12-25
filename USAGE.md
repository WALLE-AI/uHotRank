# 使用说明

## 核心功能

系统现在支持**自动将爬取的数据保存到 Elasticsearch**，无需手动导入。

## 快速使用

### 1. 一键运行（最简单）

```bash
python main.py
```

这会：
- ✅ 自动连接 Elasticsearch
- ✅ 创建索引（如果不存在）
- ✅ 爬取所有文章
- ✅ 批量保存到 ES（每 10 条一批）
- ✅ 显示统计信息

### 2. 交互式运行（更多选项）

```bash
python run_crawler.py
```

选择运行模式：
- **模式 1**：批量爬取所有文章（推荐，性能最好）
- **模式 2**：爬取并筛选技术文章（同时保存到 ES 和 JSONL）
- **模式 3**：只爬取技术文章到 ES（不保存 JSONL）

### 3. 搜索文章

```bash
python search_example.py
```

演示各种搜索功能：
- 关键词搜索
- 技术文章筛选
- 分类搜索
- 自定义查询

## 编程接口

### 函数 1：`scrape_all_articles_to_es()`

批量爬取所有文章并保存到 ES（推荐）

```python
from backend.agent.agent_today_data import scrape_all_articles_to_es

result = scrape_all_articles_to_es(
    es_index_name="tophub_articles",  # 索引名称
    batch_size=10                      # 批量大小
)

print(f"成功: {result['success']}, 失败: {result['failed']}")
```

**特点：**
- 批量插入，性能最好
- 自动创建索引
- 自动去重（基于 URL）
- 实时显示进度

### 函数 2：`scrape_and_filter_tech_articles()`

爬取并筛选技术文章

```python
from backend.agent.agent_today_data import scrape_and_filter_tech_articles

# 同时保存到 ES 和 JSONL
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=True,
    save_to_jsonl=True,
    es_index_name="tophub_articles"
)

# 只保存到 ES
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=True,
    save_to_jsonl=False
)

# 只保存到 JSONL（不使用 ES）
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=False,
    save_to_jsonl=True
)
```

**特点：**
- 实时检测技术内容
- 逐条插入 ES
- 可选保存 JSONL
- 返回技术文章列表

## 搜索接口

### 关键词搜索

```python
from backend.db import ElasticsearchClient, ArticleRepository

es_client = ElasticsearchClient()
repo = ArticleRepository(es_client, index_name="tophub_articles")

# 搜索关键词
results = repo.search_by_keyword("GPT", size=10)

for doc in results:
    print(f"{doc['title']} - 评分: {doc['_score']}")

es_client.close()
```

### 技术文章搜索

```python
# 搜索所有技术文章
tech_articles = repo.search_tech_articles(
    min_confidence=0.5,  # 最小置信度
    size=10
)

# 搜索特定分类
llm_articles = repo.search_tech_articles(
    categories=["大模型", "RAG技术"],
    min_confidence=0.5,
    size=10
)

for doc in llm_articles:
    tech_info = doc['tech_detection']
    print(f"{doc['title']}")
    print(f"  分类: {', '.join(tech_info['categories'])}")
    print(f"  置信度: {tech_info['confidence']}")
```

### 自定义搜索

```python
# 使用 Elasticsearch DSL
query = {
    "bool": {
        "must": [
            {"match": {"title": "开源"}},
            {"term": {"category": "开源中国"}}
        ]
    }
}

result = repo.search(query=query, size=10)
hits = result["hits"]["hits"]

for hit in hits:
    doc = hit["_source"]
    print(doc['title'])
```

### 统计查询

```python
# 总文档数
total = repo.count()

# 技术文章数
tech_count = repo.count(
    query={"term": {"tech_detection.is_tech_related": True}}
)

print(f"总文档: {total}, 技术文章: {tech_count}")
```

## 数据流程

```
1. 爬取文章列表
   ↓
2. 逐个爬取文章内容
   ↓
3. 提取正文（过滤网页元素）
   ↓
4. 检测技术相关性
   ↓
5. 保存到 Elasticsearch
   ↓
6. 可选：保存到 JSONL
```

## 配置说明

### 环境变量（.env）

```env
# Elasticsearch 连接
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password

# 可选：API Key 认证
ELASTICSEARCH_API_KEY=your_api_key

# 可选：Jina AI（用于网页爬取）
JINA_API_KEY=your_jina_key
```

### 爬虫配置（agent_today_data.py）

```python
# 等待时间（秒）
MIN_SLEEP = 3
MAX_SLEEP = 8

# 输出文件
OUTPUT_FILE = "tophub_articles.jsonl"

# 批量大小
batch_size = 10  # 在 scrape_all_articles_to_es() 中设置
```

### 技术关键词（agent_today_data.py）

```python
TECH_KEYWORDS = {
    "开源项目": ["开源", "github", ...],
    "大模型": ["LLM", "GPT", ...],
    "RAG技术": ["RAG", "向量数据库", ...],
    # ... 可自定义添加
}
```

## 常见问题

### Q: 如何只爬取技术文章？

```python
tech_articles = scrape_and_filter_tech_articles(
    save_to_es=True,
    save_to_jsonl=False
)
```

### Q: 如何避免重复数据？

系统自动使用 URL 作为文档 ID，相同 URL 会自动覆盖。

### Q: 如何修改批量大小？

```python
scrape_all_articles_to_es(batch_size=20)  # 改为 20
```

### Q: 如何使用不同的索引？

```python
scrape_all_articles_to_es(es_index_name="my_articles")
```

### Q: 爬虫太慢怎么办？

1. 减少等待时间（修改 `MIN_SLEEP` 和 `MAX_SLEEP`）
2. 增加批量大小（`batch_size`）
3. 注意：太快可能被封 IP

### Q: 如何只保存 JSONL 不用 ES？

```python
scrape_and_filter_tech_articles(
    save_to_es=False,
    save_to_jsonl=True
)
```

## 性能建议

1. **批量模式**：使用 `scrape_all_articles_to_es()` 性能最好
2. **批量大小**：建议 10-50 条，太大可能超时
3. **等待时间**：建议 3-8 秒，避免被封
4. **索引优化**：生产环境建议调整 ES 的 `refresh_interval`

## 下一步

- 查看 [ELASTICSEARCH_GUIDE.md](ELASTICSEARCH_GUIDE.md) 了解更多 API
- 查看 [TECH_DETECTION_README.md](TECH_DETECTION_README.md) 了解检测原理
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始指南
