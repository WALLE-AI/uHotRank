import api from './api';
import type { Article } from '@/types/article';
import type { SearchParams, SearchResult } from '@/types/search';

export interface GetArticlesParams {
  page: number;
  size: number;
  sort_by?: string;
}

export interface GetArticlesResponse {
  articles: Article[];
  total: number;
}

export interface ExportArticlesParams {
  format: 'json' | 'csv' | 'excel';
  fields: string[];
  filters: SearchParams;
}

/**
 * Article service for managing article-related API calls
 */
export const articleService = {
  /**
   * Get paginated list of articles
   */
  async getArticles(params: GetArticlesParams): Promise<GetArticlesResponse> {
    const response = await api.get<GetArticlesResponse>('/articles', { params });
    return response.data;
  },

  /**
   * Get article by ID
   */
  async getArticleById(id: string): Promise<Article> {
    const response = await api.get<Article>(`/articles/${id}`);
    return response.data;
  },

  /**
   * Search articles with filters
   */
  async searchArticles(params: SearchParams): Promise<SearchResult> {
    const response = await api.post<SearchResult>('/articles/search', params);
    return response.data;
  },

  /**
   * Export articles to file
   */
  async exportArticles(params: ExportArticlesParams): Promise<Blob> {
    const response = await api.get('/articles/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};
