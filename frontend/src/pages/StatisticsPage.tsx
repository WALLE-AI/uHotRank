import { useState, useEffect, lazy, Suspense } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar } from 'lucide-react';
import { StatsOverview } from '@/components/stats';
import { LoadingSpinner } from '@/components/common';
import { statsService } from '@/services/statsService';
import type { Statistics } from '@/types/search';
import { useToast } from '@/hooks/use-toast';

// Lazy load heavy chart components
const KeywordCloud = lazy(() => import('@/components/stats/KeywordCloud'));
const CategoryChart = lazy(() => import('@/components/stats/CategoryChart'));
const SentimentChart = lazy(() => import('@/components/stats/SentimentChart'));
const SourceChart = lazy(() => import('@/components/stats/SourceChart'));
const TrendChart = lazy(() => import('@/components/stats/TrendChart'));

export function StatisticsPage() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<{
    date_from?: string;
    date_to?: string;
  }>({});
  const { toast } = useToast();

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const data = await statsService.getStatistics(dateRange);
      setStatistics(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
      toast({
        title: '加载失败',
        description: '无法加载统计数据，请稍后重试',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatistics();
  }, [dateRange]);

  const handleDateRangeChange = (range: 'week' | 'month' | 'year' | 'all') => {
    const now = new Date();
    let date_from: string | undefined;

    switch (range) {
      case 'week':
        date_from = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case 'month':
        date_from = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case 'year':
        date_from = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case 'all':
        date_from = undefined;
        break;
    }

    setDateRange({ date_from, date_to: now.toISOString() });
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">统计分析</h1>
          <p className="text-sm text-muted-foreground mt-1">查看文章数据的统计和可视化分析</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Calendar className="w-5 h-5 text-muted-foreground hidden sm:block" />
          <div className="flex flex-wrap gap-2">
            <Button
              variant={!dateRange.date_from ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleDateRangeChange('all')}
              className="touch-manipulation"
            >
              全部
            </Button>
            <Button
              variant={
                dateRange.date_from &&
                new Date(dateRange.date_from).getTime() >
                  new Date().getTime() - 8 * 24 * 60 * 60 * 1000
                  ? 'default'
                  : 'outline'
              }
              size="sm"
              onClick={() => handleDateRangeChange('week')}
              className="touch-manipulation"
            >
              7天
            </Button>
            <Button
              variant={
                dateRange.date_from &&
                new Date(dateRange.date_from).getTime() >
                  new Date().getTime() - 31 * 24 * 60 * 60 * 1000 &&
                new Date(dateRange.date_from).getTime() <
                  new Date().getTime() - 8 * 24 * 60 * 60 * 1000
                  ? 'default'
                  : 'outline'
              }
              size="sm"
              onClick={() => handleDateRangeChange('month')}
              className="touch-manipulation"
            >
              30天
            </Button>
            <Button
              variant={
                dateRange.date_from &&
                new Date(dateRange.date_from).getTime() <
                  new Date().getTime() - 31 * 24 * 60 * 60 * 1000
                  ? 'default'
                  : 'outline'
              }
              size="sm"
              onClick={() => handleDateRangeChange('year')}
              className="touch-manipulation"
            >
              一年
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <StatsOverview statistics={statistics} loading={loading} />

      {/* Keyword Cloud */}
      <Suspense fallback={<LoadingSpinner />}>
        <KeywordCloud keywords={statistics?.top_keywords || []} loading={loading} />
      </Suspense>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <Suspense fallback={<LoadingSpinner />}>
          <CategoryChart data={statistics?.category_distribution || {}} loading={loading} />
        </Suspense>
        <Suspense fallback={<LoadingSpinner />}>
          <SentimentChart data={statistics?.sentiment_distribution || {}} loading={loading} />
        </Suspense>
      </div>

      {/* Source Chart */}
      <Suspense fallback={<LoadingSpinner />}>
        <SourceChart data={statistics?.source_distribution || {}} loading={loading} />
      </Suspense>

      {/* Trend Chart */}
      <Suspense fallback={<LoadingSpinner />}>
        <TrendChart data={statistics?.time_series || []} loading={loading} />
      </Suspense>
    </div>
  );
}

export default StatisticsPage;
