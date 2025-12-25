# 快速开始指南

## 前置要求

1. Python 3.11+
2. Elasticsearch 9.2.1+（已启动并运行）
3. uv 或 pip 包管理器

## 安装步骤

### 1. 克隆项目并安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置 Elasticsearch

#### 方式 A：使用 Docker 快速启动 ES

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ELASTIC_PASSWORD=your_password" \
  -e "xpack.security.enabled=true" \
  docker.elastic.co/elasticsearch/elasticsearch:9.2.1
```

#### 方式 B：本地安装

从 [Elasticsearch 官网](https://www.elastic.co/downloads/elasticsearch) 下载并安装。

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_password
```

### 4. 测试连接

```bash
python test_elasticsearch.py
```

如果看到 "✅ 连接成功！" 说明配置正确。

## 使用流程

### 场景 1：测试技术检测功能

```bash
python test_tech_detection.py
```

这会运行 4 个测试用例，展示技术内容检测的效果。

### 场景 2：爬取文章并导入 ES

#### 步骤 1：爬取文章

创建一个脚本 `run_crawler.py`：

```python
from backend.agent.agent_today_data import scrape_and_filter_tech_articles

# 爬取并筛选技术文章
tech_articles = scrape_and_filter_tech_articles()

print(f"共爬取 {len(tech_articles)} 篇技术文章")
# 结果会自动保存到 tech_articles.jsonl
```

运行：

```bash
python run_crawler.py
```

#### 步骤 2：导入到 ES

```bash
# 导入技术文章
python import_to_elasticsearch.py --file tech_articles.jsonl --index tech_articles

# 或导入所有文章
python import_to_elasticsearch.py --file tophub_articles.jsonl --index tophub_articles
```

#### 步骤 3：测试搜索

```bash
python import_to_elasticsearch.py --test
```

### 场景 3：使用 API 进行搜索

创建脚本 `search_articles.py`：

```python
from backend.db import ElasticsearchClient, ArticleRepository

# 连接 ES
es_client = ElasticsearchClient()
repo = ArticleRepository(es_client, index_name="tech_articles")

# 1. 关键词搜索
print("搜索关键词: LLM")
results = repo.search_by_keyword("LLM", size=5)
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc['title']}")
    print(f"   评分: {doc['_score']:.2f}")
    print()

# 2. 搜索特定分类的技术文章
print("\n搜索大模型相关文章:")
tech_articles = repo.search_tech_articles(
    categories=["大模型"],
    min_confidence=0.5,
    size=5
)
for i, doc in enumerate(tech_articles, 1):
    tech_info = doc['tech_detection']
    print(f"{i}. {doc['title']}")
    print(f"   分类: {', '.join(tech_info['categories'])}")
    print(f"   置信度: {tech_info['confidence']}")
    print()

# 3. 统计
total = repo.count()
tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
print(f"\n总文档: {total} 条")
print(f"技术文章: {tech_count} 条")

es_client.close()
```

运行：

```bash
python search_articles.py
```

## 常见问题

### Q1: 连接 ES 失败

**错误信息：** `ConnectionError` 或 `AuthenticationException`

**解决方案：**
1. 确认 ES 已启动：`curl http://localhost:9200`
2. 检查 `.env` 文件配置
3. 确认用户名密码正确
4. 如果使用 Docker，确认端口映射正确

### Q2: 中文搜索效果不好

**原因：** 未安装中文分词插件

**解决方案：** 安装 IK 分词插件

```bash
# 进入 ES 安装目录
cd /path/to/elasticsearch

# 安装 IK 插件
bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v9.2.1/elasticsearch-analysis-ik-9.2.1.zip

# 重启 ES
```

或者修改 `backend/db/elasticsearch_client.py` 中的 `create_index` 方法，将 `analyzer` 从 `ik_max_word` 改为 `standard`。

### Q3: 爬虫被拦截

**错误信息：** `403 Forbidden` 或 `下载失败`

**解决方案：**
1. 增加等待时间：修改 `MIN_SLEEP` 和 `MAX_SLEEP`
2. 使用代理
3. 检查 `curl_cffi` 是否正确安装

### Q4: 导入数据时出现重复

**说明：** 这是正常的，系统使用 URL 作为文档 ID，相同 URL 会自动覆盖，避免真正的重复。

### Q5: 内存不足

**场景：** 批量导入大量数据时

**解决方案：**
1. 分批导入：修改 `bulk_create_documents` 的批次大小
2. 增加 ES 的堆内存：修改 `jvm.options`

## 下一步

- 查看 [Elasticsearch 集成指南](ELASTICSEARCH_GUIDE.md) 了解更多 API
- 查看 [技术内容检测说明](TECH_DETECTION_README.md) 了解检测原理
- 自定义技术关键词：编辑 `backend/agent/agent_today_data.py` 中的 `TECH_KEYWORDS`
- 自定义内容过滤规则：编辑 `backend/utils/url_to_markdown.py` 中的 `_filter_markdown`

## 获取帮助

如有问题，请查看：
1. 项目文档
2. Elasticsearch 官方文档
3. 提交 Issue
