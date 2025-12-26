# Implementation Plan: Backend API Service

## Overview

本实现计划将基于 FastAPI 框架构建完整的后端 API 服务层，为前端应用提供文章管理、搜索、爬虫控制和统计分析等功能。实现将采用分层架构，确保代码的可维护性和可扩展性。

## Tasks

- [ ] 1. 项目结构重组和基础配置
  - 重命名 `backend/models/` 为 `backend/llm/`
  - 创建 `backend/schemas/`、`backend/api/`、`backend/service/` 目录
  - 创建配置文件 `backend/config/settings.py`
  - 在 `pyproject.toml` 中添加 FastAPI 相关依赖
  - _Requirements: 9.1, 10.1_

- [ ] 2. 实现 Pydantic 数据模型
  - [ ] 2.1 实现通用模型 (schemas/common.py)
    - 实现 PaginationParams、PaginatedResponse、ErrorResponse 模型
    - _Requirements: 7.1, 7.2_
  
  - [ ] 2.2 实现文章模型 (schemas/article.py)
    - 实现 Entity、ContentAnalysis、TechDetection 模型
    - 实现 ArticleBase、ArticleDetail、ArticleListItem 模型
    - 实现 SearchFilters、SearchRequest、SearchResponse 模型
    - _Requirements: 1.1, 2.1, 7.2, 7.4_
  
  - [ ] 2.3 实现爬虫模型 (schemas/crawler.py)
    - 实现 StartCrawlerRequest、StartCrawlerResponse 模型
    - 实现 CrawlerStatus、CrawlerHistoryItem、CrawlerHistoryResponse 模型
    - _Requirements: 4.1, 4.3, 5.2, 7.2_
  
  - [ ] 2.4 实现统计模型 (schemas/statistics.py)
    - 实现 OverallStatistics、KeywordStat、KeywordStats 模型
    - 实现 CategoryStats、SentimentStats、SourceStats 模型
    - 实现 TrendDataPoint、TrendStats 模型
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 7.2_

- [ ]* 2.5 编写数据模型单元测试
  - 测试模型验证逻辑
  - 测试模型序列化和反序列化
  - _Requirements: 7.3_

- [ ] 3. 实现服务层
  - [ ] 3.1 实现 ArticleService (service/article_service.py)
    - 实现 get_articles 方法（分页查询）
    - 实现 get_article_by_id 方法
    - 实现 search_articles 方法（支持关键词和过滤器）
    - 实现 export_articles 方法（JSON/CSV/Excel）
    - _Requirements: 1.1, 1.2, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 3.2 实现 CrawlerService (service/crawler_service.py)
    - 实现爬虫任务状态管理（单例模式）
    - 实现 start_crawler 方法（异步任务启动）
    - 实现 get_status 方法
    - 实现 stop_crawler 方法
    - 实现 get_history 方法（内存存储历史记录）
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 3.3 实现 StatsService (service/stats_service.py)
    - 实现 get_overall_statistics 方法
    - 实现 get_keyword_stats 方法
    - 实现 get_category_stats 方法
    - 实现 get_sentiment_stats 方法
    - 实现 get_source_stats 方法
    - 实现 get_trend_stats 方法（按日期聚合）
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ]* 3.4 编写服务层单元测试
  - 使用 mock 隔离数据库依赖
  - 测试业务逻辑和边界条件
  - _Requirements: 8.1, 8.2_

- [ ] 4. 实现导出功能
  - [ ] 4.1 实现导出工具 (utils/export.py)
    - 实现 export_to_json 函数
    - 实现 export_to_csv 函数
    - 实现 export_to_excel 函数（使用 openpyxl）
    - 实现字段选择和过滤逻辑
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 4.2 编写导出功能单元测试
  - 测试各种导出格式
  - 测试字段选择和过滤
  - _Requirements: 3.2, 3.4_

- [ ] 5. 实现 API 路由层
  - [ ] 5.1 实现文章路由 (api/articles.py)
    - 实现 GET /api/articles 端点（分页列表）
    - 实现 GET /api/articles/{id} 端点（详情）
    - 实现 POST /api/articles/search 端点（搜索）
    - 实现 GET /api/articles/export 端点（导出）
    - 添加依赖注入和参数验证
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 5.2 实现爬虫路由 (api/crawler.py)
    - 实现 POST /api/crawler/start 端点
    - 实现 GET /api/crawler/status 端点
    - 实现 POST /api/crawler/stop 端点
    - 实现 GET /api/crawler/history 端点
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 5.3 实现统计路由 (api/statistics.py)
    - 实现 GET /api/statistics 端点（总体统计）
    - 实现 GET /api/statistics/keywords 端点
    - 实现 GET /api/statistics/categories 端点
    - 实现 GET /api/statistics/sentiments 端点
    - 实现 GET /api/statistics/sources 端点
    - 实现 GET /api/statistics/trends 端点
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [ ] 5.4 实现健康检查路由 (api/health.py)
    - 实现 GET /health 端点（服务健康状态）
    - 实现 GET /version 端点（API 版本信息）
    - 检查 Elasticsearch 连接状态
    - _Requirements: 10.4, 10.5_

- [ ]* 5.5 编写 API 端点单元测试
  - 使用 FastAPI TestClient 测试端点
  - 测试正常流程和异常流程
  - 验证响应状态码和数据格式
  - _Requirements: 1.5, 7.3, 8.2_

- [ ] 6. 实现 FastAPI 应用主入口
  - [ ] 6.1 创建应用配置 (config/settings.py)
    - 定义配置类（使用 pydantic-settings）
    - 配置 CORS 允许的源
    - 配置 Elasticsearch 连接参数
    - 配置日志级别和格式
    - _Requirements: 9.1, 9.2, 9.3, 8.3_
  
  - [ ] 6.2 创建 FastAPI 应用 (backend/main.py)
    - 初始化 FastAPI 应用
    - 配置 CORS 中间件
    - 配置请求超时中间件
    - 配置请求大小限制中间件
    - 注册所有路由
    - 添加全局异常处理器
    - 配置日志记录
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3_

- [ ] 7. Checkpoint - 基础功能测试
  - 启动 FastAPI 应用
  - 访问 /docs 查看 API 文档
  - 测试健康检查端点
  - 测试文章列表和详情端点
  - 确保所有端点正常响应

- [ ]* 8. 编写属性测试
  - [ ]* 8.1 分页一致性属性测试
    - **Property 1: 分页一致性**
    - **Validates: Requirements 1.1**
  
  - [ ]* 8.2 文章 ID 唯一性属性测试
    - **Property 2: 文章 ID 唯一性**
    - **Validates: Requirements 1.2**
  
  - [ ]* 8.3 搜索结果相关性属性测试
    - **Property 3: 搜索结果相关性**
    - **Validates: Requirements 2.2**
  
  - [ ]* 8.4 过滤条件有效性属性测试
    - **Property 4: 过滤条件有效性**
    - **Validates: Requirements 2.3**
  
  - [ ]* 8.5 导出数据完整性属性测试
    - **Property 5: 导出数据完整性**
    - **Validates: Requirements 3.2, 3.4**
  
  - [ ]* 8.6 爬虫任务唯一性属性测试
    - **Property 6: 爬虫任务唯一性**
    - **Validates: Requirements 4.1, 4.4**
  
  - [ ]* 8.7 爬虫状态一致性属性测试
    - **Property 7: 爬虫状态一致性**
    - **Validates: Requirements 4.3, 4.5**
  
  - [ ]* 8.8 统计数据准确性属性测试
    - **Property 8: 统计数据准确性**
    - **Validates: Requirements 6.1, 6.3, 6.4**
  
  - [ ]* 8.9 日期范围过滤有效性属性测试
    - **Property 9: 日期范围过滤有效性**
    - **Validates: Requirements 6.7**
  
  - [ ]* 8.10 请求参数验证属性测试
    - **Property 10: 请求参数验证**
    - **Validates: Requirements 1.5, 7.3**
  
  - [ ]* 8.11 错误响应格式一致性属性测试
    - **Property 11: 错误响应格式一致性**
    - **Validates: Requirements 8.2, 8.5**

- [ ] 9. 集成测试和文档完善
  - [ ] 9.1 编写集成测试
    - 测试完整的请求-响应流程
    - 使用真实的 Elasticsearch 测试实例
    - 测试并发请求处理
    - _Requirements: 4.1, 4.4, 6.1, 6.7_
  
  - [ ] 9.2 完善 API 文档
    - 为所有端点添加详细的文档字符串
    - 添加请求和响应示例
    - 验证 OpenAPI schema 的完整性
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ] 9.3 创建 README 和部署文档
    - 编写 API 使用说明
    - 编写部署和配置指南
    - 添加环境变量说明
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 10. Final Checkpoint - 完整测试
  - 运行所有单元测试和属性测试
  - 运行集成测试
  - 测试所有 API 端点
  - 验证前端集成
  - 确保所有测试通过

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求编号，确保可追溯性
- Checkpoint 任务用于增量验证，确保每个阶段的功能正常
- 属性测试应该运行至少 100 次迭代
- 单元测试和属性测试是互补的，都很重要
