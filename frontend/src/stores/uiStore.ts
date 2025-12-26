import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';
type ViewMode = 'grid' | 'list';

interface UIStore {
  // State
  theme: Theme;
  sidebarOpen: boolean;
  viewMode: ViewMode;

  // Actions
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setViewMode: (mode: ViewMode) => void;
  toggleViewMode: () => void;
}

const initialState = {
  theme: 'system' as Theme,
  sidebarOpen: true,
  viewMode: 'grid' as ViewMode,
};

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setTheme: (theme: Theme) => {
        set({ theme });
        applyTheme(theme);
      },

      toggleTheme: () => {
        const currentTheme = get().theme;
        let newTheme: Theme;

        if (currentTheme === 'light') {
          newTheme = 'dark';
        } else if (currentTheme === 'dark') {
          newTheme = 'system';
        } else {
          newTheme = 'light';
        }

        set({ theme: newTheme });
        applyTheme(newTheme);
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      setViewMode: (mode: ViewMode) => {
        set({ viewMode: mode });
      },

      toggleViewMode: () => {
        set((state) => ({
          viewMode: state.viewMode === 'grid' ? 'list' : 'grid',
        }));
      },
    }),
    {
      name: 'ui-storage',
      onRehydrateStorage: () => (state) => {
        // Apply theme after rehydration from localStorage
        if (state) {
          applyTheme(state.theme);
        } else {
          // First time load - apply default theme
          applyTheme(initialState.theme);
        }
      },
    }
  )
);

/**
 * Apply theme to document
 */
function applyTheme(theme: Theme) {
  const root = window.document.documentElement;

  // Remove existing theme classes
  root.classList.remove('light', 'dark');

  if (theme === 'system') {
    // Use system preference
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
    root.classList.add(systemTheme);
  } else {
    root.classList.add(theme);
  }
}

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const store = useUIStore.getState();
    if (store.theme === 'system') {
      applyTheme('system');
    }
  });
}
