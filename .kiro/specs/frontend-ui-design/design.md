# 设计文档 - 前端 UI/UX 设计

## 概述

本设计文档描述了 UHotRank 系统的前端 Web 应用架构和实现方案。该应用将提供一个现代化、响应式的用户界面，用于展示和管理热门文章数据、技术内容检测结果和内容分析信息。

### 设计目标

- 提供直观、易用的用户界面
- 支持高效的数据检索和可视化
- 确保跨设备的响应式体验
- 实现实时数据更新和交互
- 保持良好的性能和可扩展性

### 技术栈选择

基于现代 Web 开发最佳实践和项目需求，我们选择以下技术栈：

**前端框架**: React 18+
- 理由：React 拥有成熟的生态系统、强大的社区支持，适合构建大规模应用。其组件化架构和虚拟 DOM 机制能够提供优秀的性能和开发体验。

**UI 组件库**: shadcn/ui + Radix UI + Tailwind CSS
- 理由：shadcn/ui 提供了现代化、可定制的组件集合，基于 Radix UI 的无障碍原语和 Tailwind CSS 的实用优先样式。这种组合提供了完全的设计控制权和优秀的开发体验。

**数据可视化**: Apache ECharts (echarts-for-react)
- 理由：ECharts 是功能强大的开源可视化库，支持丰富的图表类型、交互功能和主题定制，特别适合展示复杂的数据统计和分析结果。

**状态管理**: Zustand
- 理由：轻量级、简单易用的状态管理库，相比 Redux 更加简洁，适合中小型应用。

**HTTP 客户端**: Axios
- 理由：功能完善的 HTTP 客户端，支持请求拦截、响应转换、错误处理等特性。

**路由**: React Router v6
- 理由：React 官方推荐的路由解决方案，支持嵌套路由、懒加载等特性。

**构建工具**: Vite
- 理由：快速的开发服务器和构建工具，提供优秀的开发体验和生产构建性能。

## 架构设计

### 整体架构

系统采用前后端分离的架构模式：

```
┌─────────────────────────────────────────────────────────┐
│                    前端应用 (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  UI 组件层   │  │  状态管理层  │  │  服务层      │  │
│  │  (shadcn/ui) │  │  (Zustand)   │  │  (API)       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                  后端 API (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  路由层      │  │  业务逻辑层  │  │  数据访问层  │  │
│  │  (Endpoints) │  │  (Services)  │  │  (Repository)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Elasticsearch 数据存储                      │
└─────────────────────────────────────────────────────────┘
```

### 前端分层架构

```
src/
├── components/          # UI 组件
│   ├── ui/             # shadcn/ui 基础组件
│   ├── layout/         # 布局组件
│   ├── article/        # 文章相关组件
│   ├── search/         # 搜索相关组件
│   ├── stats/          # 统计相关组件
│   └── crawler/        # 爬虫管理组件
├── pages/              # 页面组件
│   ├── ArticleList.tsx
│   ├── ArticleDetail.tsx
│   ├── Statistics.tsx
│   ├── CrawlerManagement.tsx
│   └── Settings.tsx
├── services/           # API 服务
│   ├── api.ts          # API 客户端配置
│   ├── articleService.ts
│   ├── searchService.ts
│   ├── statsService.ts
│   └── crawlerService.ts
├── stores/             # 状态管理
│   ├── articleStore.ts
│   ├── searchStore.ts
│   ├── uiStore.ts
│   └── settingsStore.ts
├── hooks/              # 自定义 Hooks
│   ├── useArticles.ts
│   ├── useSearch.ts
│   └── useInfiniteScroll.ts
├── types/              # TypeScript 类型定义
│   ├── article.ts
│   ├── search.ts
│   └── api.ts
├── utils/              # 工具函数
│   ├── format.ts
│   ├── date.ts
│   └── export.ts
└── lib/                # 第三方库配置
    └── echarts.ts
```

## 组件设计

### 核心组件

#### 1. 布局组件

**AppLayout**
- 职责：应用主布局容器
- 包含：顶部导航栏、侧边栏（可选）、主内容区、底部信息
- 响应式：桌面端显示侧边栏，移动端使用抽屉式菜单

**Navigation**
- 职责：主导航栏
- 功能：页面导航、主题切换、用户设置入口
- 响应式：移动端显示汉堡菜单

#### 2. 文章组件

**ArticleCard**
- 职责：文章卡片展示
- 显示内容：
  - 标题
  - 来源和发布时间
  - 摘要（截断）
  - 技术标签（如果是技术文章）
  - 关键词标签
- 交互：点击跳转到详情页

**ArticleList**
- 职责：文章列表容器
- 功能：
  - 网格或列表布局切换
  - 无限滚动加载
  - 加载状态和空状态处理
- 性能优化：虚拟滚动（react-window）

**ArticleDetail**
- 职责：文章详情展示
- 显示内容：
  - 完整文章信息
  - 技术检测结果（分类、置信度、关键词）
  - 内容分析结果（关键词、主题、摘要、情感、实体）
  - 原文链接
- 布局：左侧内容，右侧分析结果侧边栏

#### 3. 搜索组件

**SearchBar**
- 职责：搜索输入框
- 功能：
  - 关键词搜索
  - 搜索建议（防抖）
  - 搜索历史
- 交互：支持键盘快捷键（Ctrl/Cmd + K）

**FilterPanel**
- 职责：筛选条件面板
- 筛选项：
  - 技术分类（多选）
  - 文章来源（多选）
  - 情感类型（单选）
  - 日期范围（日期选择器）
- 功能：
  - 显示当前筛选条件
  - 快速清除筛选
  - 保存筛选预设

**SearchResults**
- 职责：搜索结果展示
- 功能：
  - 结果数量统计
  - 排序选项（相关度、时间、热度）
  - 高亮搜索关键词

#### 4. 统计组件

**StatsOverview**
- 职责：统计概览卡片
- 显示内容：
  - 文章总数
  - 技术文章数量
  - 今日新增
  - 平均情感分数
- 样式：卡片式布局，带图标和趋势指示

**KeywordCloud**
- 职责：关键词云图
- 技术：ECharts 词云图
- 交互：点击关键词进行搜索

**CategoryChart**
- 职责：技术分类分布图
- 图表类型：饼图或环形图
- 交互：点击分类进行筛选

**SentimentChart**
- 职责：情感分析分布图
- 图表类型：柱状图或饼图
- 显示：positive、neutral、negative 的数量和占比

**SourceChart**
- 职责：文章来源分布图
- 图表类型：柱状图
- 交互：点击来源进行筛选

**TrendChart**
- 职责：时间趋势图
- 图表类型：折线图
- 显示：文章发布量随时间的变化

#### 5. 爬虫管理组件

**CrawlerControl**
- 职责：爬虫控制面板
- 功能：
  - 启动/停止爬虫
  - 选择爬取模式（全部/技术/带分析）
  - 配置爬取参数
- 状态显示：空闲、运行中、已完成、错误

**CrawlerProgress**
- 职责：爬虫进度展示
- 显示内容：
  - 进度条
  - 已爬取/总数
  - 成功/失败数量
  - 预计剩余时间
- 实时更新：WebSocket 或轮询

**CrawlerHistory**
- 职责：爬虫历史记录
- 显示内容：
  - 任务列表（时间、模式、结果）
  - 任务详情（日志、统计）
- 功能：查看历史任务详情

#### 6. 通用组件

**LoadingSpinner**
- 职责：加载动画
- 样式：旋转图标或骨架屏

**EmptyState**
- 职责：空状态展示
- 显示：图标、提示文字、操作按钮

**ErrorBoundary**
- 职责：错误边界
- 功能：捕获组件错误，显示友好提示

**Toast**
- 职责：消息提示
- 类型：成功、错误、警告、信息
- 位置：右上角或顶部中央

## 数据模型

### TypeScript 类型定义

```typescript
// 文章类型
interface Article {
  id: string;
  url: string;
  title: string;
  category: string;
  published_time: string;
  content: string;
  tech_detection?: TechDetection;
  content_analysis?: ContentAnalysis;
  created_at: string;
}

// 技术检测结果
interface TechDetection {
  is_tech_related: boolean;
  categories: string[];
  confidence: number;
  matched_keywords: string[];
}

// 内容分析结果
interface ContentAnalysis {
  keywords: string[];
  topics: string[];
  summary: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  category: string;
  entities: Entity[];
}

// 实体
interface Entity {
  name: string;
  type: string;
}

// 搜索参数
interface SearchParams {
  keyword?: string;
  tech_categories?: string[];
  sources?: string[];
  sentiment?: string;
  date_from?: string;
  date_to?: string;
  page: number;
  size: number;
  sort_by?: 'relevance' | 'time' | 'popularity';
}

// 搜索结果
interface SearchResult {
  total: number;
  articles: Article[];
  aggregations?: {
    categories: Record<string, number>;
    sources: Record<string, number>;
    sentiments: Record<string, number>;
  };
}

// 统计数据
interface Statistics {
  total_articles: number;
  tech_articles: number;
  today_new: number;
  top_keywords: Array<{ keyword: string; count: number }>;
  category_distribution: Record<string, number>;
  sentiment_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  time_series: Array<{ date: string; count: number }>;
}

// 爬虫任务
interface CrawlerTask {
  id: string;
  mode: 'all' | 'tech_only' | 'with_analysis';
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: {
    total: number;
    crawled: number;
    success: number;
    failed: number;
  };
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}
```

## 接口设计

### API 端点

#### 文章相关

```
GET    /api/articles              # 获取文章列表
GET    /api/articles/:id          # 获取文章详情
POST   /api/articles/search       # 搜索文章
GET    /api/articles/export       # 导出文章
```

#### 统计相关

```
GET    /api/statistics            # 获取统计数据
GET    /api/statistics/keywords   # 获取关键词统计
GET    /api/statistics/categories # 获取分类统计
GET    /api/statistics/sentiments # 获取情感统计
GET    /api/statistics/sources    # 获取来源统计
GET    /api/statistics/trends     # 获取趋势数据
```

#### 爬虫相关

```
POST   /api/crawler/start         # 启动爬虫
POST   /api/crawler/stop          # 停止爬虫
GET    /api/crawler/status        # 获取爬虫状态
GET    /api/crawler/history       # 获取爬虫历史
```

#### 设置相关

```
GET    /api/settings              # 获取设置
PUT    /api/settings              # 更新设置
POST   /api/settings/test-connection  # 测试 ES 连接
```

### API 服务实现

```typescript
// articleService.ts
export const articleService = {
  // 获取文章列表
  async getArticles(params: {
    page: number;
    size: number;
    sort_by?: string;
  }): Promise<{ articles: Article[]; total: number }> {
    const response = await api.get('/articles', { params });
    return response.data;
  },

  // 获取文章详情
  async getArticleById(id: string): Promise<Article> {
    const response = await api.get(`/articles/${id}`);
    return response.data;
  },

  // 搜索文章
  async searchArticles(params: SearchParams): Promise<SearchResult> {
    const response = await api.post('/articles/search', params);
    return response.data;
  },

  // 导出文章
  async exportArticles(params: {
    format: 'json' | 'csv' | 'excel';
    fields: string[];
    filters: SearchParams;
  }): Promise<Blob> {
    const response = await api.get('/articles/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

// statsService.ts
export const statsService = {
  // 获取统计数据
  async getStatistics(params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<Statistics> {
    const response = await api.get('/statistics', { params });
    return response.data;
  },

  // 获取关键词统计
  async getKeywordStats(top_n: number = 50): Promise<Array<{ keyword: string; count: number }>> {
    const response = await api.get('/statistics/keywords', {
      params: { top_n },
    });
    return response.data;
  },
};

// crawlerService.ts
export const crawlerService = {
  // 启动爬虫
  async startCrawler(config: {
    mode: 'all' | 'tech_only' | 'with_analysis';
    batch_size?: number;
  }): Promise<{ task_id: string }> {
    const response = await api.post('/crawler/start', config);
    return response.data;
  },

  // 获取爬虫状态
  async getCrawlerStatus(): Promise<CrawlerTask> {
    const response = await api.get('/crawler/status');
    return response.data;
  },

  // 停止爬虫
  async stopCrawler(): Promise<void> {
    await api.post('/crawler/stop');
  },
};
```

## 状态管理

### Zustand Store 设计

```typescript
// articleStore.ts
interface ArticleStore {
  articles: Article[];
  currentArticle: Article | null;
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    size: number;
    total: number;
  };
  
  // Actions
  fetchArticles: (page: number) => Promise<void>;
  fetchArticleById: (id: string) => Promise<void>;
  setArticles: (articles: Article[]) => void;
  clearError: () => void;
}

// searchStore.ts
interface SearchStore {
  searchParams: SearchParams;
  searchResults: SearchResult | null;
  searchHistory: string[];
  loading: boolean;
  
  // Actions
  search: (params: SearchParams) => Promise<void>;
  updateSearchParams: (params: Partial<SearchParams>) => void;
  clearFilters: () => void;
  addToHistory: (keyword: string) => void;
}

// uiStore.ts
interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  viewMode: 'grid' | 'list';
  
  // Actions
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setViewMode: (mode: 'grid' | 'list') => void;
}

// settingsStore.ts
interface SettingsStore {
  settings: {
    elasticsearch: {
      host: string;
      username: string;
      password: string;
    };
    display: {
      articlesPerPage: number;
      defaultSort: string;
    };
    theme: {
      primaryColor: string;
      mode: 'light' | 'dark';
    };
  };
  
  // Actions
  updateSettings: (settings: Partial<SettingsStore['settings']>) => void;
  testConnection: () => Promise<boolean>;
  loadSettings: () => void;
  saveSettings: () => void;
}
```

## 正确性属性

*属性是系统在所有有效执行中应该保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

基于需求文档中的验收标准，我们定义以下正确性属性：

### 属性 1: 文章卡片完整性
*对于任何*文章数据，渲染的文章卡片应该包含标题、来源、发布时间、摘要和技术标签（如果是技术文章）这些必需字段。

**验证: 需求 1.2, 1.5**

### 属性 2: 文章详情完整性
*对于任何*文章数据，文章详情页应该显示标题、来源、发布时间、原文链接和正文内容这些必需字段。

**验证: 需求 2.1**

### 属性 3: 技术检测结果显示
*对于任何*包含技术检测结果的文章，详情页应该显示技术分类、置信度和匹配的关键词。

**验证: 需求 2.2**

### 属性 4: 内容分析结果显示
*对于任何*包含内容分析结果的文章，详情页应该显示关键词、主题、摘要、情感分析和实体识别结果。

**验证: 需求 2.3**

### 属性 5: 外部链接行为
*对于任何*文章的原文链接，点击后应该在新标签页打开（target="_blank"）。

**验证: 需求 2.4**

### 属性 6: 搜索结果匹配
*对于任何*搜索关键词，返回的所有文章应该在标题或内容中包含该关键词。

**验证: 需求 3.1**

### 属性 7: 分类筛选准确性
*对于任何*选择的技术分类，返回的所有文章应该属于该分类。

**验证: 需求 3.2**

### 属性 8: 来源筛选准确性
*对于任何*选择的文章来源，返回的所有文章应该来自该来源。

**验证: 需求 3.3**

### 属性 9: 情感筛选准确性
*对于任何*选择的情感类型，返回的所有文章应该匹配该情感类型。

**验证: 需求 3.4**

### 属性 10: 日期范围筛选准确性
*对于任何*选择的日期范围，返回的所有文章的发布时间应该在该范围内。

**验证: 需求 3.5**

### 属性 11: 组合筛选准确性
*对于任何*组合的筛选条件，返回的所有文章应该同时满足所有筛选条件。

**验证: 需求 3.6**

### 属性 12: 筛选结果计数准确性
*对于任何*筛选条件，显示的文章数量应该等于实际返回的文章数量。

**验证: 需求 3.7**

### 属性 13: 统计时间范围筛选
*对于任何*选择的时间范围，统计数据应该只包含该时间范围内的文章。

**验证: 需求 4.6**

### 属性 14: 爬虫任务状态更新
*对于任何*爬虫任务，当任务状态变化时，UI 应该实时反映这些变化（已爬取数量、成功数量、失败数量）。

**验证: 需求 5.3**

### 属性 15: 任务完成状态显示
*对于任何*完成的爬虫任务，应该显示任务摘要和统计信息。

**验证: 需求 5.5**

### 属性 16: 加载状态指示
*对于任何*数据加载操作，在加载期间应该显示加载动画或骨架屏。

**验证: 需求 7.1**

### 属性 17: 错误状态显示
*对于任何*操作失败的情况，应该显示清晰的错误提示信息。

**验证: 需求 7.2**

### 属性 18: 成功反馈显示
*对于任何*成功的操作，应该显示成功反馈提示。

**验证: 需求 7.3**

### 属性 19: 键盘快捷键响应
*对于任何*配置的键盘快捷键，按下时应该触发相应的操作。

**验证: 需求 7.5**

### 属性 20: 主题切换持久化
*对于任何*主题切换操作，新主题应该立即应用并持久化到本地存储。

**验证: 需求 7.6**

### 属性 21: 当前页面导航高亮
*对于任何*当前访问的页面，对应的导航项应该被高亮显示。

**验证: 需求 8.3**

### 属性 22: 面包屑导航准确性
*对于任何*适用面包屑导航的页面，面包屑应该准确反映当前页面的层级路径。

**验证: 需求 8.5**

### 属性 23: 导出数据匹配筛选条件
*对于任何*导出操作，导出的数据应该匹配当前应用的筛选条件。

**验证: 需求 9.2**

### 属性 24: 导出进度显示
*对于任何*大量数据的导出操作，应该显示导出进度指示器。

**验证: 需求 9.3**

### 属性 25: 文件下载触发
*对于任何*完成的导出操作，应该自动触发文件下载。

**验证: 需求 9.5**

### 属性 26: 配置验证
*对于任何*配置修改操作，应该进行有效性验证。

**验证: 需求 10.2**

### 属性 27: 配置持久化
*对于任何*保存的设置，应该持久化到本地存储（localStorage）。

**验证: 需求 10.6**



## 错误处理

### 错误类型

系统需要处理以下类型的错误：

1. **网络错误**
   - 连接超时
   - 网络中断
   - DNS 解析失败

2. **API 错误**
   - 4xx 客户端错误（400, 401, 403, 404）
   - 5xx 服务器错误（500, 502, 503）
   - 请求超时

3. **数据错误**
   - 数据格式不正确
   - 必需字段缺失
   - 数据验证失败

4. **业务逻辑错误**
   - 爬虫任务冲突
   - 导出数据过大
   - 配置无效

5. **客户端错误**
   - 组件渲染错误
   - 状态管理错误
   - 本地存储错误

### 错误处理策略

#### 1. API 错误处理

```typescript
// api.ts - Axios 拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          toast.error('请求参数错误');
          break;
        case 401:
          toast.error('未授权，请重新登录');
          // 跳转到登录页
          break;
        case 403:
          toast.error('没有权限访问');
          break;
        case 404:
          toast.error('请求的资源不存在');
          break;
        case 500:
          toast.error('服务器内部错误');
          break;
        case 503:
          toast.error('服务暂时不可用');
          break;
        default:
          toast.error(data.message || '请求失败');
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      toast.error('网络连接失败，请检查网络');
    } else {
      // 请求配置错误
      toast.error('请求配置错误');
    }
    
    return Promise.reject(error);
  }
);
```

#### 2. 组件错误边界

```typescript
// ErrorBoundary.tsx
class ErrorBoundary extends React.Component<Props, State> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // 记录错误到日志服务
    console.error('Component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>出错了</h2>
          <p>页面加载失败，请刷新重试</p>
          <button onClick={() => window.location.reload()}>
            刷新页面
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

#### 3. 异步操作错误处理

```typescript
// 在 Store 中处理异步错误
const useArticleStore = create<ArticleStore>((set) => ({
  articles: [],
  loading: false,
  error: null,
  
  fetchArticles: async (page: number) => {
    set({ loading: true, error: null });
    try {
      const data = await articleService.getArticles({ page, size: 20 });
      set({ articles: data.articles, loading: false });
    } catch (error) {
      set({ 
        loading: false, 
        error: error instanceof Error ? error.message : '加载失败' 
      });
      toast.error('加载文章失败');
    }
  },
}));
```

#### 4. 表单验证错误

```typescript
// 使用 react-hook-form 进行表单验证
const {
  register,
  handleSubmit,
  formState: { errors },
} = useForm<FormData>({
  resolver: zodResolver(schema),
});

// 显示验证错误
{errors.keyword && (
  <span className="error-message">{errors.keyword.message}</span>
)}
```

### 错误恢复机制

1. **自动重试**: 对于网络错误，自动重试 3 次
2. **降级处理**: 当某个功能不可用时，提供基础功能
3. **缓存回退**: 使用缓存数据作为备选
4. **用户引导**: 提供明确的错误信息和解决建议



## 测试策略

### 测试方法

系统将采用双重测试方法，结合单元测试和基于属性的测试，以确保全面的代码覆盖和正确性验证。

**单元测试**用于验证特定示例、边缘情况和错误条件。
**基于属性的测试**用于验证跨所有输入的通用属性。
两者是互补的，对于全面覆盖都是必需的。

### 测试框架和工具

- **测试框架**: Vitest
- **React 测试**: React Testing Library
- **基于属性的测试**: fast-check
- **E2E 测试**: Playwright
- **覆盖率工具**: Vitest Coverage

### 单元测试

单元测试专注于：
- 特定示例，展示正确行为
- 组件之间的集成点
- 边缘情况和错误条件

**示例：组件渲染测试**

```typescript
// ArticleCard.test.tsx
describe('ArticleCard', () => {
  it('should render article with all required fields', () => {
    const article = {
      id: '1',
      title: 'Test Article',
      category: 'Tech',
      published_time: '2024-01-01',
      content: 'Test content',
    };
    
    render(<ArticleCard article={article} />);
    
    expect(screen.getByText('Test Article')).toBeInTheDocument();
    expect(screen.getByText('Tech')).toBeInTheDocument();
  });
  
  it('should show tech badge for tech articles', () => {
    const article = {
      ...baseArticle,
      tech_detection: {
        is_tech_related: true,
        categories: ['AI'],
        confidence: 0.9,
        matched_keywords: ['GPT'],
      },
    };
    
    render(<ArticleCard article={article} />);
    
    expect(screen.getByText('技术')).toBeInTheDocument();
  });
});
```

**示例：API 服务测试**

```typescript
// articleService.test.ts
describe('articleService', () => {
  it('should fetch articles with pagination', async () => {
    const mockData = { articles: [], total: 0 };
    vi.spyOn(api, 'get').mockResolvedValue({ data: mockData });
    
    const result = await articleService.getArticles({ page: 1, size: 20 });
    
    expect(api.get).toHaveBeenCalledWith('/articles', {
      params: { page: 1, size: 20 },
    });
    expect(result).toEqual(mockData);
  });
  
  it('should handle API errors', async () => {
    vi.spyOn(api, 'get').mockRejectedValue(new Error('Network error'));
    
    await expect(
      articleService.getArticles({ page: 1, size: 20 })
    ).rejects.toThrow('Network error');
  });
});
```

### 基于属性的测试

基于属性的测试验证跨许多生成输入的通用属性。每个属性测试必须引用其设计文档属性。

**配置要求**:
- 每个属性测试最少运行 100 次迭代
- 使用注释标记属性：`// Feature: frontend-ui-design, Property N: [property text]`

**示例：属性测试**

```typescript
// ArticleCard.property.test.tsx
import fc from 'fast-check';

describe('ArticleCard Properties', () => {
  // Feature: frontend-ui-design, Property 1: 文章卡片完整性
  it('should always render required fields for any article', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string(),
          title: fc.string({ minLength: 1 }),
          category: fc.string({ minLength: 1 }),
          published_time: fc.date().map(d => d.toISOString()),
          content: fc.string(),
        }),
        (article) => {
          const { container } = render(<ArticleCard article={article} />);
          
          // 验证所有必需字段都存在
          expect(container.textContent).toContain(article.title);
          expect(container.textContent).toContain(article.category);
        }
      ),
      { numRuns: 100 }
    );
  });
  
  // Feature: frontend-ui-design, Property 5: 外部链接行为
  it('should always open external links in new tab', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string(),
          url: fc.webUrl(),
          title: fc.string({ minLength: 1 }),
          category: fc.string(),
          published_time: fc.date().map(d => d.toISOString()),
          content: fc.string(),
        }),
        (article) => {
          render(<ArticleDetail article={article} />);
          
          const link = screen.getByRole('link', { name: /查看原文/i });
          expect(link).toHaveAttribute('target', '_blank');
          expect(link).toHaveAttribute('rel', 'noopener noreferrer');
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

```typescript
// searchFilter.property.test.ts
describe('Search Filter Properties', () => {
  // Feature: frontend-ui-design, Property 6: 搜索结果匹配
  it('should return only articles matching search keyword', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string(),
            title: fc.string(),
            content: fc.string(),
          })
        ),
        fc.string({ minLength: 1 }),
        (articles, keyword) => {
          const results = filterArticlesByKeyword(articles, keyword);
          
          // 所有结果都应该包含关键词
          results.forEach(article => {
            const matchesTitle = article.title.includes(keyword);
            const matchesContent = article.content.includes(keyword);
            expect(matchesTitle || matchesContent).toBe(true);
          });
        }
      ),
      { numRuns: 100 }
    );
  });
  
  // Feature: frontend-ui-design, Property 11: 组合筛选准确性
  it('should return articles matching all filter conditions', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string(),
            category: fc.constantFrom('Tech', 'News', 'Blog'),
            sentiment: fc.constantFrom('positive', 'neutral', 'negative'),
            published_time: fc.date().map(d => d.toISOString()),
          })
        ),
        fc.record({
          category: fc.constantFrom('Tech', 'News', 'Blog'),
          sentiment: fc.constantFrom('positive', 'neutral', 'negative'),
        }),
        (articles, filters) => {
          const results = applyFilters(articles, filters);
          
          // 所有结果都应该匹配所有筛选条件
          results.forEach(article => {
            expect(article.category).toBe(filters.category);
            expect(article.sentiment).toBe(filters.sentiment);
          });
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### 集成测试

测试组件之间的交互和数据流：

```typescript
// ArticleListPage.integration.test.tsx
describe('Article List Page Integration', () => {
  it('should load and display articles', async () => {
    const mockArticles = [
      { id: '1', title: 'Article 1', category: 'Tech' },
      { id: '2', title: 'Article 2', category: 'News' },
    ];
    
    vi.spyOn(articleService, 'getArticles').mockResolvedValue({
      articles: mockArticles,
      total: 2,
    });
    
    render(<ArticleListPage />);
    
    // 应该显示加载状态
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // 等待数据加载
    await waitFor(() => {
      expect(screen.getByText('Article 1')).toBeInTheDocument();
      expect(screen.getByText('Article 2')).toBeInTheDocument();
    });
  });
  
  it('should filter articles by category', async () => {
    render(<ArticleListPage />);
    
    // 选择分类筛选
    const categoryFilter = screen.getByLabelText('技术分类');
    fireEvent.change(categoryFilter, { target: { value: 'AI' } });
    
    // 应该调用搜索 API
    await waitFor(() => {
      expect(articleService.searchArticles).toHaveBeenCalledWith(
        expect.objectContaining({
          tech_categories: ['AI'],
        })
      );
    });
  });
});
```

### E2E 测试

使用 Playwright 进行端到端测试：

```typescript
// e2e/article-workflow.spec.ts
test('complete article browsing workflow', async ({ page }) => {
  // 访问首页
  await page.goto('/');
  
  // 等待文章列表加载
  await page.waitForSelector('[data-testid="article-card"]');
  
  // 点击第一篇文章
  await page.click('[data-testid="article-card"]:first-child');
  
  // 验证详情页加载
  await expect(page.locator('h1')).toBeVisible();
  
  // 验证技术检测结果显示
  await expect(page.locator('[data-testid="tech-detection"]')).toBeVisible();
  
  // 点击返回按钮
  await page.click('[data-testid="back-button"]');
  
  // 验证返回到列表页
  await expect(page).toHaveURL('/');
});
```

### 测试覆盖率目标

- **语句覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 75%
- **函数覆盖率**: ≥ 80%
- **行覆盖率**: ≥ 80%

### 持续集成

所有测试将在 CI/CD 流程中自动运行：

1. 提交代码时运行单元测试和属性测试
2. Pull Request 时运行完整测试套件
3. 部署前运行 E2E 测试
4. 生成测试覆盖率报告

