import { useEffect, useState } from 'react';
import { CrawlerControl } from '@/components/crawler/CrawlerControl';
import { CrawlerProgress } from '@/components/crawler/CrawlerProgress';
import { CrawlerHistory } from '@/components/crawler/CrawlerHistory';
import { crawlerService } from '@/services/crawlerService';
import type { CrawlerTask } from '@/types/search';

export function CrawlerManagementPage() {
  const [currentTask, setCurrentTask] = useState<CrawlerTask | null>(null);
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0);

  const fetchCurrentTask = async () => {
    try {
      const task = await crawlerService.getCrawlerStatus();
      setCurrentTask(task);
    } catch (error) {
      console.error('Failed to fetch crawler status:', error);
      // Set to null if no task exists
      setCurrentTask(null);
    }
  };

  useEffect(() => {
    // Initial fetch - wrapped in async IIFE to avoid setState warning
    void (async () => {
      await fetchCurrentTask();
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleTaskUpdate = () => {
    // Refresh current task
    fetchCurrentTask();
    // Trigger history refresh
    setHistoryRefreshTrigger((prev) => prev + 1);
  };

  const handleProgressUpdate = (task: CrawlerTask) => {
    setCurrentTask(task);

    // If task just completed or errored, refresh history
    if (task.status === 'completed' || task.status === 'error') {
      setHistoryRefreshTrigger((prev) => prev + 1);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">爬虫管理</h1>
        <p className="text-sm text-muted-foreground mt-2">管理和监控爬虫任务，查看爬取进度和历史记录</p>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-4 sm:space-y-6">
          <CrawlerControl currentTask={currentTask} onTaskUpdate={handleTaskUpdate} />
          <CrawlerProgress task={currentTask} onUpdate={handleProgressUpdate} />
        </div>

        {/* Right Column */}
        <div>
          <CrawlerHistory refreshTrigger={historyRefreshTrigger} />
        </div>
      </div>
    </div>
  );
}

export default CrawlerManagementPage;
