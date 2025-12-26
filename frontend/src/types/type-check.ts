// Type checking file to verify all types are properly defined and exported
// This file is not meant to be executed, only type-checked

import type {
  // Article types
  Article,
  TechDetection,
  ContentAnalysis,
  Entity,

  // Search types
  SearchParams,
  SearchResult,
  Statistics,
  CrawlerTask,

  // API types
  ApiResponse,
  ApiError,
  PaginationParams,
  PaginatedResponse,
} from './index';

// Verify Article type
const article: Article = {
  id: '1',
  url: 'https://example.com',
  title: 'Test Article',
  category: 'Tech',
  published_time: '2024-01-01T00:00:00Z',
  content: 'Test content',
  created_at: '2024-01-01T00:00:00Z',
};

// Verify Article with optional fields
const articleWithAnalysis: Article = {
  ...article,
  tech_detection: {
    is_tech_related: true,
    categories: ['AI', 'ML'],
    confidence: 0.95,
    matched_keywords: ['GPT', 'neural network'],
  },
  content_analysis: {
    keywords: ['AI', 'technology'],
    topics: ['Artificial Intelligence'],
    summary: 'Test summary',
    sentiment: 'positive',
    category: 'Tech',
    entities: [{ name: 'OpenAI', type: 'Organization' }],
  },
};

// Verify TechDetection type
const techDetection: TechDetection = {
  is_tech_related: true,
  categories: ['AI'],
  confidence: 0.9,
  matched_keywords: ['AI'],
};

// Verify ContentAnalysis type
const contentAnalysis: ContentAnalysis = {
  keywords: ['AI'],
  topics: ['Technology'],
  summary: 'Summary',
  sentiment: 'positive',
  category: 'Tech',
  entities: [],
};

// Verify Entity type
const entity: Entity = {
  name: 'OpenAI',
  type: 'Organization',
};

// Verify SearchParams type
const searchParams: SearchParams = {
  page: 1,
  size: 20,
};

const searchParamsWithFilters: SearchParams = {
  keyword: 'AI',
  tech_categories: ['AI', 'ML'],
  sources: ['TechCrunch'],
  sentiment: 'positive',
  date_from: '2024-01-01',
  date_to: '2024-12-31',
  page: 1,
  size: 20,
  sort_by: 'relevance',
};

// Verify SearchResult type
const searchResult: SearchResult = {
  total: 100,
  articles: [article],
};

const searchResultWithAggregations: SearchResult = {
  total: 100,
  articles: [article],
  aggregations: {
    categories: { AI: 50 },
    sources: { TechCrunch: 40 },
    sentiments: { positive: 60 },
  },
};

// Verify Statistics type
const statistics: Statistics = {
  total_articles: 1000,
  tech_articles: 500,
  today_new: 50,
  top_keywords: [{ keyword: 'AI', count: 100 }],
  category_distribution: { AI: 200 },
  sentiment_distribution: { positive: 600 },
  source_distribution: { TechCrunch: 400 },
  time_series: [{ date: '2024-01-01', count: 10 }],
};

// Verify CrawlerTask type
const crawlerTask: CrawlerTask = {
  id: 'task-1',
  mode: 'all',
  status: 'idle',
  progress: {
    total: 0,
    crawled: 0,
    success: 0,
    failed: 0,
  },
};

const crawlerTaskRunning: CrawlerTask = {
  id: 'task-2',
  mode: 'with_analysis',
  status: 'running',
  progress: {
    total: 100,
    crawled: 50,
    success: 45,
    failed: 5,
  },
  started_at: '2024-01-01T00:00:00Z',
};

const crawlerTaskCompleted: CrawlerTask = {
  id: 'task-3',
  mode: 'tech_only',
  status: 'completed',
  progress: {
    total: 100,
    crawled: 100,
    success: 95,
    failed: 5,
  },
  started_at: '2024-01-01T00:00:00Z',
  completed_at: '2024-01-01T01:00:00Z',
};

const crawlerTaskError: CrawlerTask = {
  id: 'task-4',
  mode: 'all',
  status: 'error',
  progress: {
    total: 100,
    crawled: 30,
    success: 25,
    failed: 5,
  },
  started_at: '2024-01-01T00:00:00Z',
  error_message: 'Connection failed',
};

// Verify ApiResponse type
const apiResponse: ApiResponse<Article> = {
  data: article,
  success: true,
};

const apiResponseWithMessage: ApiResponse<Article[]> = {
  data: [article],
  message: 'Success',
  success: true,
};

// Verify ApiError type
const apiError: ApiError = {
  message: 'Error occurred',
};

const apiErrorWithDetails: ApiError = {
  message: 'Validation failed',
  code: 'VALIDATION_ERROR',
  details: { field: 'email', reason: 'invalid format' },
};

// Verify PaginationParams type
const paginationParams: PaginationParams = {
  page: 1,
  size: 20,
};

// Verify PaginatedResponse type
const paginatedResponse: PaginatedResponse<Article> = {
  items: [article],
  total: 100,
  page: 1,
  size: 20,
  total_pages: 5,
};

// Export to avoid unused variable warnings
export {
  article,
  articleWithAnalysis,
  techDetection,
  contentAnalysis,
  entity,
  searchParams,
  searchParamsWithFilters,
  searchResult,
  searchResultWithAggregations,
  statistics,
  crawlerTask,
  crawlerTaskRunning,
  crawlerTaskCompleted,
  crawlerTaskError,
  apiResponse,
  apiResponseWithMessage,
  apiError,
  apiErrorWithDetails,
  paginationParams,
  paginatedResponse,
};
