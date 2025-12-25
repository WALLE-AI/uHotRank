# Elasticsearch 集成指南

## 功能概述

已完成 Elasticsearch 9.2.1 的集成，支持：
- 文章数据的 CRUD 操作
- 批量导入 JSONL 数据
- 全文搜索（支持中文分词）
- 技术文章筛选和搜索
- 自动去重（基于 URL）

## 快速开始

### 1. 安装依赖

```bash
pip install elasticsearch python-dotenv
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password
```

### 3. 导入数据

```bash
# 基础导入
python import_to_elasticsearch.py

# 重新创建索引并导入（会删除旧数据）
python import_to_elasticsearch.py --recreate

# 导入后运行搜索测试
python import_to_elasticsearch.py --test

# 指定文件和索引名
python import_to_elasticsearch.py --file tech_articles.jsonl --index tech_articles
```

## 核心类说明

### ElasticsearchClient

Elasticsearch 客户端封装，支持多种认证方式。

```python
from backend.db import ElasticsearchClient

# 使用环境变量配置
es_client = ElasticsearchClient()

# 或手动指定配置
es_client = ElasticsearchClient(
    hosts=["http://localhost:9200"],
    username="elastic",
    password="password"
)

# 测试连接
if es_client.ping():
    print("连接成功")

# 获取集群信息
info = es_client.get_info()
print(f"ES 版本: {info['version']['number']}")
```

### ArticleRepository

文章数据仓库，封装所有 CRUD 操作。

#### 创建索引

```python
from backend.db import ElasticsearchClient, ArticleRepository

es_client = ElasticsearchClient()
repo = ArticleRepository(es_client, index_name="tophub_articles")

# 创建索引
repo.create_index()

# 重新创建索引（删除旧数据）
repo.create_index(delete_if_exists=True)
```

#### 单个文档操作

```python
# 创建文档
article = {
    "title": "GPT-4 发布",
    "category": "AI",
    "content": "OpenAI 发布了 GPT-4...",
    "original_url": "https://example.com/article1"
}
result = repo.create_document(article)

# 获取文档
doc = repo.get_document(doc_id="https://example.com/article1")

# 更新文档
repo.update_document(
    doc_id="https://example.com/article1",
    updates={"category": "大模型"}
)

# 删除文档
repo.delete_document(doc_id="https://example.com/article1")
```

#### 批量操作

```python
# 批量创建文档
articles = [
    {"title": "文章1", "content": "内容1", "original_url": "url1"},
    {"title": "文章2", "content": "内容2", "original_url": "url2"}
]

result = repo.bulk_create_documents(articles)
print(f"成功: {result['success']}, 失败: {result['failed']}")
```

#### 搜索操作

```python
# 1. 关键词搜索
results = repo.search_by_keyword("GPT", size=10)
for doc in results:
    print(f"{doc['title']} - 评分: {doc['_score']}")

# 2. 搜索技术文章
tech_articles = repo.search_tech_articles(
    categories=["大模型", "RAG技术"],  # 可选：指定分类
    min_confidence=0.5,                # 最小置信度
    size=10
)

# 3. 自定义搜索（ES DSL）
query = {
    "bool": {
        "must": [
            {"match": {"title": "开源"}},
            {"term": {"category": "开源中国"}}
        ]
    }
}
result = repo.search(query=query, size=10)

# 4. 统计文档数量
total = repo.count()
tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
print(f"总文档: {total}, 技术文章: {tech_count}")
```

## 索引结构

### 字段映射

```json
{
  "title": "文章标题（支持中文分词）",
  "category": "分类（keyword）",
  "original_url": "原始 URL（keyword，用作文档 ID）",
  "tophub_url": "TopHub URL（keyword）",
  "publish_date": "发布日期（date）",
  "content": "正文内容（支持中文分词）",
  "images": "图片列表（keyword 数组）",
  "scraped_at": "爬取时间（date）",
  "tech_detection": {
    "is_tech_related": "是否技术相关（boolean）",
    "categories": "技术分类（keyword 数组）",
    "keywords": "关键词（keyword 数组）",
    "confidence": "置信度（float）",
    "summary": "摘要（text）"
  },
  "status": "状态（keyword）",
  "error": "错误信息（text）"
}
```

### 中文分词

索引使用 `ik_max_word` 分词器（需要安装 IK 插件）：

```bash
# Elasticsearch 9.x 安装 IK 插件
bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v9.2.1/elasticsearch-analysis-ik-9.2.1.zip
```

如果没有安装 IK 插件，可以修改 `elasticsearch_client.py` 中的 `create_index` 方法，将 `analyzer` 改为 `standard`。

## 完整示例

### 爬取并保存到 ES

```python
from backend.agent.agent_today_data import scrape_and_filter_tech_articles
from backend.db import ElasticsearchClient, ArticleRepository

# 1. 爬取技术文章
tech_articles = scrape_and_filter_tech_articles()

# 2. 连接 ES
es_client = ElasticsearchClient()
repo = ArticleRepository(es_client)

# 3. 创建索引
repo.create_index()

# 4. 批量导入
result = repo.bulk_create_documents(tech_articles)
print(f"导入完成: {result['success']} 条")

# 5. 搜索验证
results = repo.search_by_keyword("LLM", size=5)
for doc in results:
    print(doc['title'])

# 6. 关闭连接
es_client.close()
```

### 从 JSONL 导入

```python
import json
from backend.db import ElasticsearchClient, ArticleRepository

# 读取 JSONL
documents = []
with open("tophub_articles.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        documents.append(json.loads(line))

# 导入到 ES
es_client = ElasticsearchClient()
repo = ArticleRepository(es_client)
repo.create_index()
result = repo.bulk_create_documents(documents)

print(f"导入 {result['success']} 条数据")
es_client.close()
```

## 常见问题

### 1. 连接失败

检查：
- Elasticsearch 是否已启动
- `.env` 文件配置是否正确
- 防火墙是否允许访问 9200 端口

### 2. 认证失败

Elasticsearch 9.x 默认启用安全认证，需要配置用户名密码或 API Key。

### 3. 中文搜索不准确

需要安装 IK 中文分词插件，或使用其他中文分词方案。

### 4. 重复数据

系统使用 `original_url` 或 `tophub_url` 作为文档 ID，相同 URL 的文档会自动覆盖，避免重复。

## API 参考

### ElasticsearchClient

- `__init__(hosts, api_key, username, password, ...)` - 初始化客户端
- `ping()` - 测试连接
- `get_info()` - 获取集群信息
- `close()` - 关闭连接

### ArticleRepository

- `create_index(delete_if_exists)` - 创建索引
- `index_exists()` - 检查索引是否存在
- `create_document(document, doc_id)` - 创建单个文档
- `bulk_create_documents(documents)` - 批量创建文档
- `get_document(doc_id)` - 获取文档
- `update_document(doc_id, updates)` - 更新文档
- `delete_document(doc_id)` - 删除文档
- `search(query, size, from_, sort)` - 自定义搜索
- `search_by_keyword(keyword, fields, size)` - 关键词搜索
- `search_tech_articles(categories, min_confidence, size)` - 搜索技术文章
- `count(query)` - 统计文档数量
- `delete_index()` - 删除索引

## 下一步

- 添加更多搜索功能（聚合、高亮等）
- 实现增量更新
- 添加数据同步任务
- 集成到 Web API
