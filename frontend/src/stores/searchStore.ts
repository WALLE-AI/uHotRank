import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SearchParams, SearchResult } from '../types/search';
import { articleService } from '../services/articleService';

interface SearchStore {
  // State
  searchParams: SearchParams;
  searchResults: SearchResult | null;
  searchHistory: string[];
  loading: boolean;
  error: string | null;

  // Actions
  search: (params: SearchParams) => Promise<void>;
  updateSearchParams: (params: Partial<SearchParams>) => void;
  clearFilters: () => void;
  addToHistory: (keyword: string) => void;
  clearHistory: () => void;
  removeFromHistory: (keyword: string) => void;
  clearError: () => void;
  reset: () => void;
}

const defaultSearchParams: SearchParams = {
  page: 1,
  size: 20,
  sort_by: 'time',
};

const initialState = {
  searchParams: defaultSearchParams,
  searchResults: null,
  searchHistory: [],
  loading: false,
  error: null,
};

export const useSearchStore = create<SearchStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      search: async (params: SearchParams) => {
        set({ loading: true, error: null });
        try {
          const results = await articleService.searchArticles(params);
          set({
            searchResults: results,
            searchParams: params,
            loading: false,
          });

          // Add keyword to history if present
          if (params.keyword && params.keyword.trim()) {
            get().addToHistory(params.keyword.trim());
          }
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error.message : '搜索失败',
          });
        }
      },

      updateSearchParams: (params: Partial<SearchParams>) => {
        set((state) => ({
          searchParams: { ...state.searchParams, ...params },
        }));
      },

      clearFilters: () => {
        set({
          searchParams: defaultSearchParams,
          searchResults: null,
        });
      },

      addToHistory: (keyword: string) => {
        set((state) => {
          // Remove duplicate if exists
          const filtered = state.searchHistory.filter((k) => k !== keyword);
          // Add to beginning and limit to 10 items
          return {
            searchHistory: [keyword, ...filtered].slice(0, 10),
          };
        });
      },

      clearHistory: () => {
        set({ searchHistory: [] });
      },

      removeFromHistory: (keyword: string) => {
        set((state) => ({
          searchHistory: state.searchHistory.filter((k) => k !== keyword),
        }));
      },

      clearError: () => {
        set({ error: null });
      },

      reset: () => {
        set({
          ...initialState,
          searchHistory: get().searchHistory, // Keep history on reset
        });
      },
    }),
    {
      name: 'search-storage',
      partialize: (state) => ({
        searchHistory: state.searchHistory,
      }),
    }
  )
);
