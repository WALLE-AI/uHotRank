import { useState } from 'react';
import { Play, Square, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { crawlerService, type StartCrawlerConfig } from '@/services/crawlerService';
import type { CrawlerTask } from '@/types/search';

interface CrawlerControlProps {
  currentTask: CrawlerTask | null;
  onTaskUpdate: () => void;
}

export function CrawlerControl({ currentTask, onTaskUpdate }: CrawlerControlProps) {
  const [mode, setMode] = useState<StartCrawlerConfig['mode']>('all');
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const { toast } = useToast();

  const isRunning = currentTask?.status === 'running';

  const handleStart = async () => {
    setIsStarting(true);
    try {
      await crawlerService.startCrawler({ mode });
      toast({
        title: '爬虫已启动',
        description: `正在以"${getModeLabel(mode)}"模式爬取数据`,
      });
      onTaskUpdate();
    } catch (error) {
      toast({
        title: '启动失败',
        description: error instanceof Error ? error.message : '无法启动爬虫任务',
        variant: 'destructive',
      });
    } finally {
      setIsStarting(false);
    }
  };

  const handleStop = async () => {
    setIsStopping(true);
    try {
      await crawlerService.stopCrawler();
      toast({
        title: '爬虫已停止',
        description: '爬虫任务已成功停止',
      });
      onTaskUpdate();
    } catch (error) {
      toast({
        title: '停止失败',
        description: error instanceof Error ? error.message : '无法停止爬虫任务',
        variant: 'destructive',
      });
    } finally {
      setIsStopping(false);
    }
  };

  const getModeLabel = (mode: StartCrawlerConfig['mode']) => {
    switch (mode) {
      case 'all':
        return '全部文章';
      case 'tech_only':
        return '仅技术文章';
      case 'with_analysis':
        return '带内容分析';
      default:
        return mode;
    }
  };

  const getStatusLabel = (status: CrawlerTask['status']) => {
    switch (status) {
      case 'idle':
        return '空闲';
      case 'running':
        return '运行中';
      case 'completed':
        return '已完成';
      case 'error':
        return '错误';
      default:
        return status;
    }
  };

  const getStatusColor = (status: CrawlerTask['status']) => {
    switch (status) {
      case 'idle':
        return 'text-gray-500';
      case 'running':
        return 'text-blue-500';
      case 'completed':
        return 'text-green-500';
      case 'error':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>爬虫控制</CardTitle>
        <CardDescription>启动或停止爬虫任务，选择爬取模式</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Task Status */}
        {currentTask && (
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">任务状态:</span>
              <span className={`text-sm font-semibold ${getStatusColor(currentTask.status)}`}>
                {getStatusLabel(currentTask.status)}
              </span>
            </div>
            {isRunning && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
          </div>
        )}

        {/* Error Message */}
        {currentTask?.status === 'error' && currentTask.error_message && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">
              错误: {currentTask.error_message}
            </p>
          </div>
        )}

        {/* Mode Selection */}
        <div className="space-y-2">
          <Label htmlFor="crawler-mode">爬取模式</Label>
          <Select
            value={mode}
            onValueChange={(value) => setMode(value as StartCrawlerConfig['mode'])}
            disabled={isRunning}
          >
            <SelectTrigger id="crawler-mode">
              <SelectValue placeholder="选择爬取模式" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部文章</SelectItem>
              <SelectItem value="tech_only">仅技术文章</SelectItem>
              <SelectItem value="with_analysis">带内容分析</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            {mode === 'all' && '爬取所有文章，不进行技术检测'}
            {mode === 'tech_only' && '只爬取技术相关文章'}
            {mode === 'with_analysis' && '爬取文章并进行完整的内容分析'}
          </p>
        </div>

        {/* Control Buttons */}
        <div className="flex gap-2">
          <Button onClick={handleStart} disabled={isRunning || isStarting} className="flex-1">
            {isStarting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                启动中...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                启动爬虫
              </>
            )}
          </Button>
          <Button
            onClick={handleStop}
            disabled={!isRunning || isStopping}
            variant="destructive"
            className="flex-1"
          >
            {isStopping ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                停止中...
              </>
            ) : (
              <>
                <Square className="mr-2 h-4 w-4" />
                停止爬虫
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
