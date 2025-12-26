import api from './api';
import type { CrawlerTask } from '@/types/search';

export interface StartCrawlerConfig {
  mode: 'all' | 'tech_only' | 'with_analysis';
  batch_size?: number;
}

export interface StartCrawlerResponse {
  task_id: string;
}

export interface CrawlerHistoryItem {
  id: string;
  mode: string;
  status: string;
  started_at: string;
  completed_at?: string;
  total_crawled: number;
  success_count: number;
  failed_count: number;
}

/**
 * Crawler service for managing crawler-related API calls
 */
export const crawlerService = {
  /**
   * Start a new crawler task
   */
  async startCrawler(config: StartCrawlerConfig): Promise<StartCrawlerResponse> {
    const response = await api.post<StartCrawlerResponse>('/crawler/start', config);
    return response.data;
  },

  /**
   * Get current crawler task status
   */
  async getCrawlerStatus(): Promise<CrawlerTask> {
    const response = await api.get<CrawlerTask>('/crawler/status');
    return response.data;
  },

  /**
   * Stop the running crawler task
   */
  async stopCrawler(): Promise<void> {
    await api.post('/crawler/stop');
  },

  /**
   * Get crawler task history
   */
  async getCrawlerHistory(params?: { page?: number; size?: number }): Promise<{
    items: CrawlerHistoryItem[];
    total: number;
  }> {
    const response = await api.get<{
      items: CrawlerHistoryItem[];
      total: number;
    }>('/crawler/history', { params });
    return response.data;
  },
};
