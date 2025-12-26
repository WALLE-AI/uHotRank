import { create } from 'zustand';
import type { Article } from '../types/article';
import { articleService } from '../services/articleService';

interface Pagination {
  page: number;
  size: number;
  total: number;
}

interface ArticleStore {
  // State
  articles: Article[];
  currentArticle: Article | null;
  loading: boolean;
  error: string | null;
  pagination: Pagination;

  // Actions
  fetchArticles: (page: number, size?: number) => Promise<void>;
  fetchArticleById: (id: string) => Promise<void>;
  setArticles: (articles: Article[]) => void;
  setCurrentArticle: (article: Article | null) => void;
  setPagination: (pagination: Partial<Pagination>) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  articles: [],
  currentArticle: null,
  loading: false,
  error: null,
  pagination: {
    page: 1,
    size: 20,
    total: 0,
  },
};

export const useArticleStore = create<ArticleStore>((set) => ({
  ...initialState,

  fetchArticles: async (page: number, size = 20) => {
    set({ loading: true, error: null });
    try {
      const data = await articleService.getArticles({ page, size });
      set((state) => ({
        articles: page === 1 ? data.articles : [...state.articles, ...data.articles],
        loading: false,
        pagination: {
          page,
          size,
          total: data.total,
        },
      }));
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : '加载文章失败',
      });
    }
  },

  fetchArticleById: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const article = await articleService.getArticleById(id);
      set({
        currentArticle: article,
        loading: false,
      });
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : '加载文章详情失败',
      });
    }
  },

  setArticles: (articles: Article[]) => {
    set({ articles });
  },

  setCurrentArticle: (article: Article | null) => {
    set({ currentArticle: article });
  },

  setPagination: (pagination: Partial<Pagination>) => {
    set((state) => ({
      pagination: { ...state.pagination, ...pagination },
    }));
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));
