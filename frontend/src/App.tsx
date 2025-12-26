import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/toaster';
import { AppLayout } from '@/components/layout';
import { LoadingSpinner } from '@/components/common';

// Lazy load page components for code splitting
const ArticleListPage = lazy(() => import('@/pages/ArticleListPage'));
const ArticleDetailPage = lazy(() => import('@/pages/ArticleDetailPage'));
const StatisticsPage = lazy(() => import('@/pages/StatisticsPage'));
const CrawlerManagementPage = lazy(() => import('@/pages/CrawlerManagementPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="uhotrank-ui-theme">
      <BrowserRouter>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<ArticleListPage />} />
              <Route path="articles/:id" element={<ArticleDetailPage />} />
              <Route path="statistics" element={<StatisticsPage />} />
              <Route path="crawler" element={<CrawlerManagementPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
      <Toaster />
    </ThemeProvider>
  );
}

export default App;
