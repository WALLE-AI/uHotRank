import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

interface ElasticsearchSettings {
  host: string;
  username: string;
  password: string;
}

interface DisplaySettings {
  articlesPerPage: number;
  defaultSort: 'relevance' | 'time' | 'popularity';
  showTechBadge: boolean;
  showSentiment: boolean;
}

interface ThemeSettings {
  primaryColor: string;
  mode: 'light' | 'dark' | 'system';
}

interface Settings {
  elasticsearch: ElasticsearchSettings;
  display: DisplaySettings;
  theme: ThemeSettings;
}

interface SettingsStore {
  // State
  settings: Settings;
  loading: boolean;
  error: string | null;
  testingConnection: boolean;
  connectionStatus: 'idle' | 'success' | 'error';

  // Actions
  updateSettings: (settings: Partial<Settings>) => void;
  updateElasticsearch: (elasticsearch: Partial<ElasticsearchSettings>) => void;
  updateDisplay: (display: Partial<DisplaySettings>) => void;
  updateTheme: (theme: Partial<ThemeSettings>) => void;
  testConnection: () => Promise<boolean>;
  loadSettings: () => void;
  saveSettings: () => void;
  resetSettings: () => void;
  clearError: () => void;
}

const defaultSettings: Settings = {
  elasticsearch: {
    host: 'http://localhost:9200',
    username: '',
    password: '',
  },
  display: {
    articlesPerPage: 20,
    defaultSort: 'time',
    showTechBadge: true,
    showSentiment: true,
  },
  theme: {
    primaryColor: '#3b82f6',
    mode: 'system',
  },
};

const initialState = {
  settings: defaultSettings,
  loading: false,
  error: null,
  testingConnection: false,
  connectionStatus: 'idle' as const,
};

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      updateSettings: (newSettings: Partial<Settings>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            ...newSettings,
          },
        }));
      },

      updateElasticsearch: (elasticsearch: Partial<ElasticsearchSettings>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            elasticsearch: {
              ...state.settings.elasticsearch,
              ...elasticsearch,
            },
          },
        }));
      },

      updateDisplay: (display: Partial<DisplaySettings>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            display: {
              ...state.settings.display,
              ...display,
            },
          },
        }));
      },

      updateTheme: (theme: Partial<ThemeSettings>) => {
        set((state) => ({
          settings: {
            ...state.settings,
            theme: {
              ...state.settings.theme,
              ...theme,
            },
          },
        }));
      },

      testConnection: async () => {
        set({ testingConnection: true, error: null, connectionStatus: 'idle' });
        try {
          // Test Elasticsearch connection
          const { elasticsearch } = get().settings;

          // Validate settings
          if (!elasticsearch.host) {
            throw new Error('Elasticsearch 主机地址不能为空');
          }

          // Make test request to settings endpoint
          await api.post('/settings/test-connection', {
            host: elasticsearch.host,
            username: elasticsearch.username,
            password: elasticsearch.password,
          });

          set({
            testingConnection: false,
            connectionStatus: 'success',
          });
          return true;
        } catch (error) {
          set({
            testingConnection: false,
            connectionStatus: 'error',
            error: error instanceof Error ? error.message : '连接测试失败',
          });
          return false;
        }
      },

      loadSettings: () => {
        // Settings are automatically loaded from localStorage via persist middleware
        // This method can be used for additional loading logic if needed
        set({ loading: false });
      },

      saveSettings: () => {
        // Settings are automatically saved to localStorage via persist middleware
        // This method can be used for additional save logic if needed
        set({ loading: false });
      },

      resetSettings: () => {
        set({
          settings: defaultSettings,
          error: null,
          connectionStatus: 'idle',
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'settings-storage',
      version: 1,
      // Optionally migrate old settings format
      migrate: (persistedState: unknown, version: number) => {
        if (version === 0) {
          const state = persistedState as { settings?: Partial<Settings> };
          // Migration logic for version 0 to 1
          return {
            settings: {
              ...defaultSettings,
              ...state.settings,
            },
          };
        }
        return persistedState as SettingsStore;
      },
    }
  )
);

/**
 * Validate Elasticsearch settings
 */
export function validateElasticsearchSettings(settings: ElasticsearchSettings): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!settings.host) {
    errors.push('主机地址不能为空');
  } else {
    try {
      new URL(settings.host);
    } catch {
      errors.push('主机地址格式不正确');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate display settings
 */
export function validateDisplaySettings(settings: DisplaySettings): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (settings.articlesPerPage < 1 || settings.articlesPerPage > 100) {
    errors.push('每页文章数量必须在 1-100 之间');
  }

  if (!['relevance', 'time', 'popularity'].includes(settings.defaultSort)) {
    errors.push('默认排序方式无效');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
