import { useEffect, useState } from 'react';
import { Clock, CheckCircle2, XCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { crawlerService, type CrawlerHistoryItem } from '@/services/crawlerService';

interface CrawlerHistoryProps {
  refreshTrigger?: number;
}

export function CrawlerHistory({ refreshTrigger }: CrawlerHistoryProps) {
  const [history, setHistory] = useState<CrawlerHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, [refreshTrigger]);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await crawlerService.getCrawlerHistory({ page: 1, size: 10 });
      setHistory(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载历史记录失败');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getModeLabel = (mode: string) => {
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'error':
        return '错误';
      case 'running':
        return '运行中';
      case 'idle':
        return '空闲';
      default:
        return status;
    }
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    const start = new Date(startTime).getTime();
    const end = endTime ? new Date(endTime).getTime() : Date.now();
    const duration = Math.floor((end - start) / 1000); // seconds

    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;

    if (hours > 0) {
      return `${hours}小时 ${minutes}分钟`;
    } else if (minutes > 0) {
      return `${minutes}分钟 ${seconds}秒`;
    } else {
      return `${seconds}秒`;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>历史任务</CardTitle>
          <CardDescription>查看过去的爬虫任务记录</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">加载中...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>历史任务</CardTitle>
          <CardDescription>查看过去的爬虫任务记录</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
          <Button onClick={fetchHistory} variant="outline" className="mt-4">
            重试
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>历史任务</CardTitle>
        <CardDescription>查看过去的爬虫任务记录</CardDescription>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <p className="text-sm text-muted-foreground">暂无历史记录</p>
        ) : (
          <div className="space-y-3">
            {history.map((item) => (
              <div
                key={item.id}
                className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(item.status)}
                      <span className="font-medium text-sm">{getModeLabel(item.mode)}</span>
                      <span className="text-xs text-muted-foreground">
                        {getStatusLabel(item.status)}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.started_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => toggleExpand(item.id)}>
                    {expandedId === item.id ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {/* Summary Stats */}
                <div className="mt-3 flex gap-4 text-xs">
                  <div>
                    <span className="text-muted-foreground">总计: </span>
                    <span className="font-medium">{item.total_crawled}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">成功: </span>
                    <span className="font-medium text-green-600 dark:text-green-400">
                      {item.success_count}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">失败: </span>
                    <span className="font-medium text-red-600 dark:text-red-400">
                      {item.failed_count}
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedId === item.id && (
                  <div className="mt-4 pt-4 border-t space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">任务 ID:</span>
                      <span className="font-mono">{item.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">开始时间:</span>
                      <span>{new Date(item.started_at).toLocaleString('zh-CN')}</span>
                    </div>
                    {item.completed_at && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">完成时间:</span>
                          <span>{new Date(item.completed_at).toLocaleString('zh-CN')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">运行时长:</span>
                          <span>{formatDuration(item.started_at, item.completed_at)}</span>
                        </div>
                      </>
                    )}
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">成功率:</span>
                      <span>
                        {item.total_crawled > 0
                          ? Math.round((item.success_count / item.total_crawled) * 100)
                          : 0}
                        %
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
