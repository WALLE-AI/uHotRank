# Requirements Document

## Introduction

本文档定义了基于 FastAPI 框架的后端 API 服务层需求，该服务层将为前端应用提供完整的数据接口支持，包括文章管理、搜索、爬虫控制和统计分析等功能。

## Glossary

- **API_Service**: FastAPI 应用服务，提供 RESTful API 接口
- **Article_Repository**: 文章数据仓库，封装 Elasticsearch 数据访问
- **Crawler_Manager**: 爬虫管理器，控制爬虫任务的启动、停止和状态监控
- **Statistics_Aggregator**: 统计聚合器，提供数据分析和统计功能
- **Request_Model**: Pydantic 请求数据模型
- **Response_Model**: Pydantic 响应数据模型
- **CORS_Middleware**: 跨域资源共享中间件

## Requirements

### Requirement 1: 文章列表和详情接口

**User Story:** 作为前端开发者，我希望能够获取文章列表和单篇文章详情，以便在界面上展示文章内容。

#### Acceptance Criteria

1. WHEN 请求文章列表时，THE API_Service SHALL 返回分页的文章数据，包含 articles 数组、total 总数、page 页码和 size 每页数量
2. WHEN 请求单篇文章详情时，THE API_Service SHALL 根据文章 ID 返回完整的文章数据
3. WHEN 文章不存在时，THE API_Service SHALL 返回 404 状态码和错误信息
4. THE API_Service SHALL 支持按发布时间、创建时间等字段排序文章列表
5. WHEN 请求参数无效时，THE API_Service SHALL 返回 400 状态码和参数验证错误信息

### Requirement 2: 文章搜索接口

**User Story:** 作为前端开发者，我希望能够根据关键词、分类、情感等条件搜索文章，以便用户能够快速找到感兴趣的内容。

#### Acceptance Criteria

1. WHEN 提交搜索请求时，THE API_Service SHALL 接受包含 query、filters、page、size 等参数的搜索条件
2. THE API_Service SHALL 支持按关键词在标题和内容中进行全文搜索
3. THE API_Service SHALL 支持按分类、情感倾向、日期范围等条件过滤文章
4. WHEN 搜索完成时，THE API_Service SHALL 返回匹配的文章列表、总数和分页信息
5. THE API_Service SHALL 支持按相关性、时间等维度排序搜索结果

### Requirement 3: 文章导出接口

**User Story:** 作为前端开发者，我希望能够导出文章数据为不同格式的文件，以便用户可以离线查看或进行数据分析。

#### Acceptance Criteria

1. THE API_Service SHALL 支持导出文章为 JSON、CSV、Excel 三种格式
2. WHEN 请求导出时，THE API_Service SHALL 接受 format、fields、filters 参数
3. WHEN 导出完成时，THE API_Service SHALL 返回对应格式的文件流，设置正确的 Content-Type 和 Content-Disposition 响应头
4. THE API_Service SHALL 支持选择性导出指定字段
5. THE API_Service SHALL 支持按搜索条件过滤后导出

### Requirement 4: 爬虫控制接口

**User Story:** 作为前端开发者，我希望能够启动、停止爬虫任务并查看爬虫状态，以便用户可以管理数据采集过程。

#### Acceptance Criteria

1. WHEN 启动爬虫时，THE API_Service SHALL 接受 mode 和 batch_size 参数，并返回 task_id
2. THE API_Service SHALL 支持三种爬虫模式：all（全部）、tech_only（仅技术）、with_analysis（带分析）
3. WHEN 查询爬虫状态时，THE API_Service SHALL 返回当前任务的运行状态、进度、已爬取数量等信息
4. WHEN 停止爬虫时，THE API_Service SHALL 终止当前运行的爬虫任务
5. WHEN 没有运行中的爬虫任务时，THE API_Service SHALL 返回空闲状态

### Requirement 5: 爬虫历史记录接口

**User Story:** 作为前端开发者，我希望能够查看历史爬虫任务记录，以便用户了解数据采集历史。

#### Acceptance Criteria

1. WHEN 请求爬虫历史时，THE API_Service SHALL 返回分页的历史任务列表
2. THE API_Service SHALL 为每个历史任务提供 id、mode、status、started_at、completed_at、total_crawled、success_count、failed_count 等信息
3. THE API_Service SHALL 按任务开始时间倒序排列历史记录
4. THE API_Service SHALL 支持分页查询历史记录

### Requirement 6: 统计数据接口

**User Story:** 作为前端开发者，我希望能够获取各类统计数据，以便在界面上展示数据分析图表。

#### Acceptance Criteria

1. WHEN 请求总体统计时，THE API_Service SHALL 返回文章总数、今日新增、技术文章数、分析完成数等统计信息
2. WHEN 请求关键词统计时，THE API_Service SHALL 返回 top N 关键词及其出现次数
3. WHEN 请求分类统计时，THE API_Service SHALL 返回各分类的文章数量分布
4. WHEN 请求情感统计时，THE API_Service SHALL 返回正面、中性、负面文章的数量分布
5. WHEN 请求来源统计时，THE API_Service SHALL 返回各来源网站的文章数量分布
6. WHEN 请求趋势统计时，THE API_Service SHALL 返回按日期聚合的文章数量时间序列数据
7. THE API_Service SHALL 支持按日期范围过滤统计数据

### Requirement 7: 数据模型验证

**User Story:** 作为后端开发者，我希望使用 Pydantic 模型验证请求和响应数据，以确保数据类型正确和接口规范。

#### Acceptance Criteria

1. THE API_Service SHALL 为所有请求参数定义 Pydantic Request_Model
2. THE API_Service SHALL 为所有响应数据定义 Pydantic Response_Model
3. WHEN 请求数据不符合模型定义时，THE API_Service SHALL 自动返回 422 状态码和验证错误详情
4. THE Response_Model SHALL 与前端 TypeScript 类型定义保持一致
5. THE API_Service SHALL 在 OpenAPI 文档中自动生成模型 schema

### Requirement 8: 错误处理和日志

**User Story:** 作为后端开发者，我希望有统一的错误处理机制和日志记录，以便快速定位和解决问题。

#### Acceptance Criteria

1. THE API_Service SHALL 捕获所有未处理的异常并返回 500 状态码和错误信息
2. THE API_Service SHALL 为不同类型的错误返回相应的 HTTP 状态码（400、404、422、500 等）
3. THE API_Service SHALL 记录所有请求的访问日志，包含时间戳、请求路径、方法、状态码、响应时间
4. THE API_Service SHALL 记录所有错误的详细日志，包含异常堆栈信息
5. THE API_Service SHALL 在生产环境中隐藏敏感的错误详情

### Requirement 9: CORS 和中间件配置

**User Story:** 作为后端开发者，我希望配置 CORS 和其他中间件，以支持前端跨域访问和请求处理。

#### Acceptance Criteria

1. THE API_Service SHALL 配置 CORS_Middleware 允许前端域名跨域访问
2. THE API_Service SHALL 支持 GET、POST、PUT、DELETE 等 HTTP 方法
3. THE API_Service SHALL 允许前端发送自定义请求头
4. THE API_Service SHALL 配置请求超时中间件，防止长时间阻塞
5. THE API_Service SHALL 配置请求大小限制中间件，防止过大的请求

### Requirement 10: API 文档和健康检查

**User Story:** 作为开发者，我希望有自动生成的 API 文档和健康检查接口，以便了解接口规范和监控服务状态。

#### Acceptance Criteria

1. THE API_Service SHALL 在 /docs 路径提供 Swagger UI 交互式文档
2. THE API_Service SHALL 在 /redoc 路径提供 ReDoc 文档
3. THE API_Service SHALL 在 /openapi.json 路径提供 OpenAPI schema
4. THE API_Service SHALL 提供 /health 健康检查接口，返回服务状态和依赖项状态
5. THE API_Service SHALL 提供 /version 接口，返回 API 版本信息
