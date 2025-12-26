# Design Document

## Overview

本设计文档描述了基于 FastAPI 框架的后端 API 服务层的技术架构和实现方案。该服务将为前端 React 应用提供完整的 RESTful API 接口，包括文章管理、搜索、爬虫控制和统计分析等功能。

服务采用分层架构设计：
- **API 层**：FastAPI 路由和端点定义
- **服务层**：业务逻辑封装
- **数据访问层**：Elasticsearch 数据操作
- **模型层**：Pydantic 数据模型定义

## Architecture

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│                   TypeScript + Axios                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Router Layer                         │  │
│  │  /api/articles  /api/crawler  /api/statistics        │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  ArticleService  CrawlerService  StatsService        │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │           Data Access Layer                           │  │
│  │         ArticleRepository (existing)                  │  │
│  └────────────────────┬─────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Elasticsearch   │
              │   tophub_articles│
              └──────────────────┘
```

### 目录结构

```
backend/
├── api/                    # API 路由层
│   ├── __init__.py
│   ├── articles.py        # 文章相关接口
│   ├── crawler.py         # 爬虫相关接口
│   ├── statistics.py      # 统计相关接口
│   └── health.py          # 健康检查接口
├── service/               # 服务层
│   ├── __init__.py
│   ├── article_service.py
│   ├── crawler_service.py
│   └── stats_service.py
├── schemas/               # Pydantic 数据模型（新建）
│   ├── __init__.py
│   ├── article.py         # 文章模型
│   ├── crawler.py         # 爬虫模型
│   ├── statistics.py      # 统计模型
│   └── common.py          # 通用模型
├── llm/                   # LLM 服务（重命名自 models/）
│   ├── __init__.py
│   └── llm_provider.py    # LLM 提供者（已存在，保留）
├── db/                    # 数据访问层（已存在）
│   ├── elasticsearch_client.py
│   └── __init__.py
├── agent/                 # 爬虫和分析（已存在）
│   ├── agent_today_data.py
│   └── agent_content_keyword_analysis.py
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── url_to_markdown.py # URL转Markdown（已存在，保留）
│   └── export.py          # 导出功能
├── config/                # 配置
│   ├── __init__.py
│   └── settings.py        # 应用配置
└── main.py                # FastAPI 应用入口（新建）
```

## Components and Interfaces

### 1. FastAPI Application (main.py)

FastAPI 应用主入口，负责应用初始化、中间件配置和路由注册。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import articles, crawler, statistics, health
from backend.config.settings import settings

app = FastAPI(
    title="TopHub Article API",
    description="API for TopHub article management and analysis",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["crawler"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(health.router, tags=["health"])
```

### 2. API Router Layer

#### Articles Router (api/articles.py)

```python
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from backend.schemas.article import ArticleListResponse, ArticleDetail, SearchRequest, SearchResponse
from backend.schemas.common import PaginationParams
from backend.service.article_service import ArticleService

router = APIRouter()

@router.get("", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    service: ArticleService = Depends()
):
    """获取文章列表"""
    pass

@router.get("/{article_id}", response_model=ArticleDetail)
async def get_article_by_id(
    article_id: str,
    service: ArticleService = Depends()
):
    """获取文章详情"""
    pass

@router.post("/search", response_model=SearchResponse)
async def search_articles(
    request: SearchRequest,
    service: ArticleService = Depends()
):
    """搜索文章"""
    pass

@router.get("/export")
async def export_articles(
    format: str = Query(..., regex="^(json|csv|excel)$"),
    fields: str = Query(...),
    filters: Optional[str] = Query(None),
    service: ArticleService = Depends()
):
    """导出文章"""
    pass
```

#### Crawler Router (api/crawler.py)

```python
from fastapi import APIRouter, Depends
from backend.schemas.crawler import StartCrawlerRequest, StartCrawlerResponse, CrawlerStatus, CrawlerHistoryResponse
from backend.service.crawler_service import CrawlerService

router = APIRouter()

@router.post("/start", response_model=StartCrawlerResponse)
async def start_crawler(
    request: StartCrawlerRequest,
    service: CrawlerService = Depends()
):
    """启动爬虫任务"""
    pass

@router.get("/status", response_model=CrawlerStatus)
async def get_crawler_status(
    service: CrawlerService = Depends()
):
    """获取爬虫状态"""
    pass

@router.post("/stop")
async def stop_crawler(
    service: CrawlerService = Depends()
):
    """停止爬虫任务"""
    pass

@router.get("/history", response_model=CrawlerHistoryResponse)
async def get_crawler_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: CrawlerService = Depends()
):
    """获取爬虫历史"""
    pass
```

#### Statistics Router (api/statistics.py)

```python
from fastapi import APIRouter, Query, Depends
from typing import Optional
from backend.schemas.statistics import (
    OverallStatistics, KeywordStats, CategoryStats,
    SentimentStats, SourceStats, TrendStats
)
from backend.service.stats_service import StatsService

router = APIRouter()

@router.get("", response_model=OverallStatistics)
async def get_statistics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    service: StatsService = Depends()
):
    """获取总体统计"""
    pass

@router.get("/keywords", response_model=KeywordStats)
async def get_keyword_stats(
    top_n: int = Query(50, ge=1, le=200),
    service: StatsService = Depends()
):
    """获取关键词统计"""
    pass

@router.get("/categories", response_model=CategoryStats)
async def get_category_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    service: StatsService = Depends()
):
    """获取分类统计"""
    pass

@router.get("/sentiments", response_model=SentimentStats)
async def get_sentiment_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    service: StatsService = Depends()
):
    """获取情感统计"""
    pass

@router.get("/sources", response_model=SourceStats)
async def get_source_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    service: StatsService = Depends()
):
    """获取来源统计"""
    pass

@router.get("/trends", response_model=TrendStats)
async def get_trend_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    service: StatsService = Depends()
):
    """获取趋势统计"""
    pass
```

### 3. Service Layer

#### ArticleService (service/article_service.py)

封装文章相关的业务逻辑。

```python
from typing import List, Optional, Dict, Any
from backend.db.elasticsearch_client import ArticleRepository
from backend.schemas.article import ArticleListResponse, ArticleDetail, SearchRequest, SearchResponse

class ArticleService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
    
    async def get_articles(
        self, page: int, size: int, sort_by: Optional[str]
    ) -> ArticleListResponse:
        """获取文章列表"""
        pass
    
    async def get_article_by_id(self, article_id: str) -> ArticleDetail:
        """获取文章详情"""
        pass
    
    async def search_articles(self, request: SearchRequest) -> SearchResponse:
        """搜索文章"""
        pass
    
    async def export_articles(
        self, format: str, fields: List[str], filters: Dict[str, Any]
    ) -> bytes:
        """导出文章"""
        pass
```

#### CrawlerService (service/crawler_service.py)

封装爬虫相关的业务逻辑，管理爬虫任务的生命周期。

```python
from typing import Optional
import asyncio
from backend.schemas.crawler import StartCrawlerRequest, StartCrawlerResponse, CrawlerStatus
from backend.agent.agent_today_data import scrape_all_articles_to_es

class CrawlerService:
    def __init__(self):
        self.current_task: Optional[asyncio.Task] = None
        self.task_status: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
    
    async def start_crawler(self, request: StartCrawlerRequest) -> StartCrawlerResponse:
        """启动爬虫任务"""
        pass
    
    async def get_status(self) -> CrawlerStatus:
        """获取当前爬虫状态"""
        pass
    
    async def stop_crawler(self) -> None:
        """停止爬虫任务"""
        pass
    
    async def get_history(self, page: int, size: int) -> Dict[str, Any]:
        """获取爬虫历史"""
        pass
```

#### StatsService (service/stats_service.py)

封装统计相关的业务逻辑。

```python
from typing import Optional, Dict, Any, List
from backend.db.elasticsearch_client import ArticleRepository
from backend.schemas.statistics import *

class StatsService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
    
    async def get_overall_statistics(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> OverallStatistics:
        """获取总体统计"""
        pass
    
    async def get_keyword_stats(self, top_n: int) -> List[KeywordStat]:
        """获取关键词统计"""
        pass
    
    async def get_category_stats(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> Dict[str, int]:
        """获取分类统计"""
        pass
    
    async def get_sentiment_stats(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> Dict[str, int]:
        """获取情感统计"""
        pass
    
    async def get_source_stats(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> Dict[str, int]:
        """获取来源统计"""
        pass
    
    async def get_trend_stats(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> List[TrendDataPoint]:
        """获取趋势统计"""
        pass
```

## Data Models

### Article Models (schemas/article.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Entity(BaseModel):
    name: str
    type: str

class ContentAnalysis(BaseModel):
    keywords: List[str] = []
    topics: List[str] = []
    summary: str = ""
    sentiment: str = "neutral"
    category: str = ""
    entities: List[Entity] = []

class TechDetection(BaseModel):
    is_tech_related: bool = False
    categories: List[str] = []
    confidence: float = 0.0
    matched_keywords: List[str] = []

class ArticleBase(BaseModel):
    id: str
    url: str
    title: str
    category: str
    published_time: str
    content: str
    tech_detection: Optional[TechDetection] = None
    content_analysis: Optional[ContentAnalysis] = None
    created_at: str

class ArticleDetail(ArticleBase):
    """文章详情模型"""
    pass

class ArticleListItem(BaseModel):
    """文章列表项模型（简化版）"""
    id: str
    title: str
    category: str
    published_time: str
    summary: Optional[str] = None
    sentiment: Optional[str] = None

class ArticleListResponse(BaseModel):
    articles: List[ArticleListItem]
    total: int
    page: int
    size: int

class SearchFilters(BaseModel):
    categories: Optional[List[str]] = None
    sentiments: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    tech_only: Optional[bool] = None

class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None

class SearchResponse(BaseModel):
    articles: List[ArticleListItem]
    total: int
    page: int
    size: int
```

### Crawler Models (schemas/crawler.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class StartCrawlerRequest(BaseModel):
    mode: Literal["all", "tech_only", "with_analysis"] = "all"
    batch_size: int = Field(10, ge=1, le=100)

class StartCrawlerResponse(BaseModel):
    task_id: str
    message: str = "Crawler task started successfully"

class CrawlerStatus(BaseModel):
    is_running: bool
    task_id: Optional[str] = None
    mode: Optional[str] = None
    progress: Optional[int] = None
    total_crawled: int = 0
    success_count: int = 0
    failed_count: int = 0
    started_at: Optional[str] = None
    current_status: str = "idle"

class CrawlerHistoryItem(BaseModel):
    id: str
    mode: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    total_crawled: int
    success_count: int
    failed_count: int

class CrawlerHistoryResponse(BaseModel):
    items: List[CrawlerHistoryItem]
    total: int
    page: int
    size: int
```

### Statistics Models (schemas/statistics.py)

```python
from pydantic import BaseModel
from typing import Dict, List

class OverallStatistics(BaseModel):
    total_articles: int
    today_new: int
    tech_articles: int
    analyzed_articles: int
    categories_count: int
    avg_sentiment_score: float

class KeywordStat(BaseModel):
    keyword: str
    count: int

class KeywordStats(BaseModel):
    keywords: List[KeywordStat]

class CategoryStats(BaseModel):
    categories: Dict[str, int]

class SentimentStats(BaseModel):
    positive: int
    neutral: int
    negative: int

class SourceStats(BaseModel):
    sources: Dict[str, int]

class TrendDataPoint(BaseModel):
    date: str
    count: int

class TrendStats(BaseModel):
    trends: List[TrendDataPoint]
```

### Common Models (schemas/common.py)

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int

class ErrorResponse(BaseModel):
    message: str
    code: Optional[str] = None
    details: Optional[dict] = None
```

## Correctness Properties

*属性（Property）是指在所有有效执行中都应该成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 分页一致性
*对于任意*有效的分页参数（page, size），返回的文章数量应该小于等于 size，且 total 应该等于数据库中符合条件的文章总数
**Validates: Requirements 1.1**

### Property 2: 文章 ID 唯一性
*对于任意*文章 ID，通过 ID 查询应该返回唯一的文章或 404 错误，不应该返回多个文章
**Validates: Requirements 1.2**

### Property 3: 搜索结果相关性
*对于任意*搜索关键词，返回的所有文章应该在标题或内容中包含该关键词（或其分词结果）
**Validates: Requirements 2.2**

### Property 4: 过滤条件有效性
*对于任意*过滤条件组合，返回的所有文章都应该满足所有指定的过滤条件
**Validates: Requirements 2.3**

### Property 5: 导出数据完整性
*对于任意*导出请求，导出文件中的数据应该与搜索结果中的数据一致，且包含所有指定的字段
**Validates: Requirements 3.2, 3.4**

### Property 6: 爬虫任务唯一性
*对于任意*时刻，系统中最多只能有一个正在运行的爬虫任务
**Validates: Requirements 4.1, 4.4**

### Property 7: 爬虫状态一致性
*对于任意*爬虫任务，如果状态为 running，则 task_id 不应为空；如果状态为 idle，则 task_id 应为空
**Validates: Requirements 4.3, 4.5**

### Property 8: 统计数据准确性
*对于任意*统计查询，返回的各项统计数值之和应该等于符合条件的文章总数
**Validates: Requirements 6.1, 6.3, 6.4**

### Property 9: 日期范围过滤有效性
*对于任意*日期范围过滤，返回的所有数据的日期都应该在指定的范围内
**Validates: Requirements 6.7**

### Property 10: 请求参数验证
*对于任意*无效的请求参数，API 应该返回 400 或 422 状态码，而不是 500 错误
**Validates: Requirements 1.5, 7.3**

### Property 11: 错误响应格式一致性
*对于任意*错误情况，API 应该返回统一格式的错误响应，包含 message 字段
**Validates: Requirements 8.2, 8.5**

## Error Handling

### 错误类型和处理策略

1. **参数验证错误 (400/422)**
   - Pydantic 自动验证请求参数
   - 返回详细的验证错误信息
   - 示例：缺少必需字段、类型不匹配、值超出范围

2. **资源不存在错误 (404)**
   - 文章 ID 不存在
   - 返回友好的错误消息

3. **业务逻辑错误 (400)**
   - 爬虫已在运行时尝试启动新任务
   - 没有运行中的任务时尝试停止
   - 返回具体的业务错误信息

4. **服务器内部错误 (500)**
   - Elasticsearch 连接失败
   - 未预期的异常
   - 记录详细日志，返回通用错误消息

### 全局异常处理器

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"}
    )
```

## Testing Strategy

### 单元测试

使用 pytest 进行单元测试，覆盖以下内容：

1. **Service 层测试**
   - 测试各个 Service 方法的业务逻辑
   - 使用 mock 隔离数据库依赖
   - 测试边界条件和错误处理

2. **API 端点测试**
   - 使用 FastAPI TestClient 测试 API 端点
   - 测试正常流程和异常流程
   - 验证响应状态码和数据格式

3. **数据模型测试**
   - 测试 Pydantic 模型的验证逻辑
   - 测试模型序列化和反序列化

### 属性测试

使用 Hypothesis 进行属性测试，验证正确性属性：

1. **分页属性测试**
   - 生成随机的 page 和 size 参数
   - 验证返回结果符合分页一致性属性

2. **搜索过滤属性测试**
   - 生成随机的搜索条件和过滤器
   - 验证所有返回结果都满足过滤条件

3. **统计准确性属性测试**
   - 生成随机的日期范围
   - 验证统计数据的准确性

### 集成测试

1. **端到端测试**
   - 测试完整的请求-响应流程
   - 使用真实的 Elasticsearch 测试实例
   - 验证数据持久化和查询

2. **并发测试**
   - 测试多个并发请求的处理
   - 验证爬虫任务的并发控制

### 测试配置

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def es_client():
    return ElasticsearchClient()

@pytest.fixture
def article_repository(es_client):
    return ArticleRepository(es_client, index_name="test_articles")
```

每个属性测试应该运行至少 100 次迭代，并使用以下标签格式：
**Feature: backend-api-service, Property {number}: {property_text}**
