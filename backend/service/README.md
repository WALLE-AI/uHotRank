# Service Layer Implementation

本目录包含后端 API 服务的业务逻辑层实现。

## 服务列表

### 1. ArticleService (article_service.py)

文章服务层，提供文章管理相关的业务逻辑。

**主要功能：**
- `get_articles()` - 获取文章列表（支持分页和排序）
- `get_article_by_id()` - 根据 ID 获取文章详情
- `search_articles()` - 搜索文章（支持关键词搜索和多条件过滤）
- `export_articles()` - 导出文章数据（支持 JSON、CSV、Excel 格式）

**使用示例：**
```python
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository
from backend.service.article_service import ArticleService

# 初始化
es_client = ElasticsearchClient()
repo = ArticleRepository(es_client, index_name="tophub_articles")
service = ArticleService(repo)

# 获取文章列表
result = service.get_articles(page=1, size=20, sort_by="-publish_date")

# 搜索文章
from backend.schemas.article import SearchRequest, SearchFilters
request = SearchRequest(
    query="人工智能",
    filters=SearchFilters(
        categories=["科技"],
        sentiments=["positive"],
        tech_only=True
    ),
    page=1,
    size=20
)
result = service.search_articles(request)
```

### 2. CrawlerService (crawler_service.py)

爬虫服务层，管理爬虫任务的生命周期（单例模式）。

**主要功能：**
- `start_crawler()` - 启动爬虫任务（异步）
- `get_status()` - 获取当前爬虫状态
- `stop_crawler()` - 停止当前运行的爬虫任务
- `get_history()` - 获取爬虫历史记录（分页）

**使用示例：**
```python
import asyncio
from backend.service.crawler_service import CrawlerService
from backend.schemas.crawler import StartCrawlerRequest

# 初始化（单例）
service = CrawlerService()

# 启动爬虫
async def start():
    request = StartCrawlerRequest(
        mode="with_analysis",  # all, tech_only, with_analysis
        batch_size=10
    )
    response = await service.start_crawler(request)
    print(f"任务 ID: {response.task_id}")

# 获取状态
async def check_status():
    status = await service.get_status()
    print(f"运行中: {status.is_running}")
    print(f"已爬取: {status.total_crawled}")

asyncio.run(start())
```

### 3. StatsService (stats_service.py)

统计服务层，提供数据分析和统计功能。

**主要功能：**
- `get_overall_statistics()` - 获取总体统计信息
- `get_keyword_stats()` - 获取关键词统计（Top N）
- `get_category_stats()` - 获取分类统计
- `get_sentiment_stats()` - 获取情感统计
- `get_source_stats()` - 获取来源统计
- `get_trend_stats()` - 获取趋势统计（按日期聚合）

**使用示例：**
```python
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository
from backend.service.stats_service import StatsService

# 初始化
es_client = ElasticsearchClient()
repo = ArticleRepository(es_client, index_name="tophub_articles")
service = StatsService(repo)

# 获取总体统计
overall = service.get_overall_statistics()
print(f"文章总数: {overall.total_articles}")
print(f"技术文章: {overall.tech_articles}")

# 获取关键词统计
keywords = service.get_keyword_stats(top_n=50)
for kw in keywords.keywords[:10]:
    print(f"{kw.keyword}: {kw.count}")

# 获取趋势统计（带日期过滤）
trends = service.get_trend_stats(
    date_from="2024-01-01",
    date_to="2024-12-31"
)
```

## 架构说明

### 分层设计

```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Elasticsearch
```

### 依赖注入

服务层通过构造函数接收依赖（Repository），便于测试和解耦：

```python
class ArticleService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
```

### 错误处理

所有服务方法都包含异常处理，记录详细日志并向上抛出异常：

```python
try:
    # 业务逻辑
    pass
except Exception as e:
    logger.error(f"操作失败: {e}")
    raise
```

## 测试

运行测试脚本验证服务层实现：

```bash
python test_services.py
```

## 注意事项

1. **Elasticsearch 字段类型**：
   - 聚合查询需要使用 `.keyword` 后缀（如 `content_analysis.category.keyword`）
   - 文本字段默认不支持聚合，需要使用 keyword 子字段

2. **异步操作**：
   - CrawlerService 的所有方法都是异步的，需要使用 `await` 调用
   - 爬虫任务在后台运行，不会阻塞 API 请求

3. **单例模式**：
   - CrawlerService 使用单例模式，确保全局只有一个实例
   - 避免多个爬虫任务同时运行

4. **分页限制**：
   - 文章列表和搜索结果默认每页最多 100 条
   - 导出功能最多导出 10000 条记录

5. **日期格式**：
   - 日期过滤使用 ISO 格式字符串（如 "2024-01-01"）
   - Elasticsearch 会自动解析日期格式

## 下一步

完成服务层实现后，下一步是：
1. 实现 API 路由层（task 5）
2. 创建 FastAPI 应用主入口（task 6）
3. 编写单元测试和属性测试（task 3.4, 8）
