import type { Article } from './article';

// Search related types
export interface SearchParams {
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

export interface SearchResult {
  total: number;
  articles: Article[];
  aggregations?: {
    categories: Record<string, number>;
    sources: Record<string, number>;
    sentiments: Record<string, number>;
  };
}

export interface Statistics {
  total_articles: number;
  tech_articles: number;
  today_new: number;
  top_keywords: Array<{ keyword: string; count: number }>;
  category_distribution: Record<string, number>;
  sentiment_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  time_series: Array<{ date: string; count: number }>;
}

export interface CrawlerTask {
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
