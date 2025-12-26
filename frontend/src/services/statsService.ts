import api from './api';
import type { Statistics } from '@/types/search';

export interface GetStatisticsParams {
  date_from?: string;
  date_to?: string;
}

export interface KeywordStat {
  keyword: string;
  count: number;
}

export interface CategoryStats {
  [category: string]: number;
}

export interface SentimentStats {
  positive: number;
  neutral: number;
  negative: number;
}

export interface SourceStats {
  [source: string]: number;
}

/**
 * Statistics service for managing statistics-related API calls
 */
export const statsService = {
  /**
   * Get overall statistics
   */
  async getStatistics(params?: GetStatisticsParams): Promise<Statistics> {
    const response = await api.get<Statistics>('/statistics', { params });
    return response.data;
  },

  /**
   * Get keyword statistics
   */
  async getKeywordStats(top_n: number = 50): Promise<KeywordStat[]> {
    const response = await api.get<KeywordStat[]>('/statistics/keywords', {
      params: { top_n },
    });
    return response.data;
  },

  /**
   * Get category distribution statistics
   */
  async getCategoryStats(params?: GetStatisticsParams): Promise<CategoryStats> {
    const response = await api.get<CategoryStats>('/statistics/categories', { params });
    return response.data;
  },

  /**
   * Get sentiment distribution statistics
   */
  async getSentimentStats(params?: GetStatisticsParams): Promise<SentimentStats> {
    const response = await api.get<SentimentStats>('/statistics/sentiments', { params });
    return response.data;
  },

  /**
   * Get source distribution statistics
   */
  async getSourceStats(params?: GetStatisticsParams): Promise<SourceStats> {
    const response = await api.get<SourceStats>('/statistics/sources', { params });
    return response.data;
  },

  /**
   * Get time series trend data
   */
  async getTrendStats(
    params?: GetStatisticsParams
  ): Promise<Array<{ date: string; count: number }>> {
    const response = await api.get<Array<{ date: string; count: number }>>('/statistics/trends', {
      params,
    });
    return response.data;
  },
};
