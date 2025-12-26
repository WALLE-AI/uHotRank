import { useEffect } from 'react';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { CrawlerTask } from '@/types/search';
import { crawlerService } from '@/services/crawlerService';

interface CrawlerProgressProps {
  task: CrawlerTask | null;
  onUpdate?: (task: CrawlerTask) => void;
}

export function CrawlerProgress({ task, onUpdate }: CrawlerProgressProps) {
  // Poll for updates when task is running
  useEffect(() => {
    if (!task || !task.is_running) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updatedTask = await crawlerService.getCrawlerStatus();
        onUpdate?.(updatedTask);
      } catch (error) {
        console.error('Failed to fetch crawler status:', error);
      }
    }, 2000); // Poll every 2 seconds

    return () => {
      clearInterval(interval);
    };
  }, [task?.is_running, task?.task_id, onUpdate]);

  if (!task) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>爬取进度</CardTitle>
          <CardDescription>暂无运行中的任务</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">启动爬虫后，这里将显示实时进度</p>
        </CardContent>
      </Card>
    );
  }

  const { progress } = task;
  const progressPercentage =
    progress.total > 0 ? Math.round((progress.crawled / progress.total) * 100) : 0;

  const successRate =
    progress.crawled > 0 ? Math.round((progress.success / progress.crawled) * 100) : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>爬取进度</CardTitle>
        <CardDescription>
          {task.status === 'running' && '正在实时更新...'}
          {task.status === 'completed' && '任务已完成'}
          {task.status === 'error' && '任务出错'}
          {task.status === 'idle' && '任务空闲'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">总体进度</span>
            <span className="text-muted-foreground">
              {progress.crawled} / {progress.total > 0 ? progress.total : '未知'}
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <p className="text-xs text-muted-foreground text-right">{progressPercentage}% 完成</p>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-3 gap-4">
          {/* Crawled */}
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span className="text-xs">已爬取</span>
            </div>
            <p className="text-2xl font-bold">{progress.crawled}</p>
          </div>

          {/* Success */}
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-xs">成功</span>
            </div>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {progress.success}
            </p>
          </div>

          {/* Failed */}
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <XCircle className="h-4 w-4" />
              <span className="text-xs">失败</span>
            </div>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{progress.failed}</p>
          </div>
        </div>

        {/* Success Rate */}
        {progress.crawled > 0 && (
          <div className="p-3 bg-muted rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">成功率</span>
              <span className="text-sm font-bold text-green-600 dark:text-green-400">
                {successRate}%
              </span>
            </div>
          </div>
        )}

        {/* Time Information */}
        {task.started_at && (
          <div className="space-y-2 text-xs text-muted-foreground">
            <div className="flex justify-between">
              <span>开始时间:</span>
              <span>{new Date(task.started_at).toLocaleString('zh-CN')}</span>
            </div>
            {task.completed_at && (
              <div className="flex justify-between">
                <span>完成时间:</span>
                <span>{new Date(task.completed_at).toLocaleString('zh-CN')}</span>
              </div>
            )}
            {task.status === 'running' && (
              <div className="flex justify-between">
                <span>运行时长:</span>
                <span>{getElapsedTime(task.started_at)}</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Calculate elapsed time from start time
 */
function getElapsedTime(startTime: string): string {
  const start = new Date(startTime).getTime();
  const now = Date.now();
  const elapsed = Math.floor((now - start) / 1000); // seconds

  const hours = Math.floor(elapsed / 3600);
  const minutes = Math.floor((elapsed % 3600) / 60);
  const seconds = elapsed % 60;

  if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`;
  } else if (minutes > 0) {
    return `${minutes}分钟 ${seconds}秒`;
  } else {
    return `${seconds}秒`;
  }
}
