import { useEffect, useState } from 'react';
import { ArticleList } from '@/components/article/ArticleList';
import { ExportDialog } from '@/components/export/ExportDialog';
import { useArticleStore } from '@/stores/articleStore';
import { useUIStore } from '@/stores/uiStore';
import { Button } from '@/components/ui/button';
import { Grid3x3, List, Loader2, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { downloadAsJSON, downloadAsCSV, downloadAsExcel } from '@/utils/export';
import type { SearchParams } from '@/types/search';

export function ArticleListPage() {
  const { toast } = useToast();
  const { articles, loading, error, pagination, fetchArticles, clearError } = useArticleStore();
  const { viewMode, toggleViewMode } = useUIStore();
  const [exportDialogOpen, setExportDialogOpen] = useState(false);

  // Initial load
  useEffect(() => {
    fetchArticles(1);
  }, [fetchArticles]);

  // Handle errors
  useEffect(() => {
    if (error) {
      toast({
        variant: 'destructive',
        title: '加载失败',
        description: error,
      });
      clearError();
    }
  }, [error, toast, clearError]);

  // Load more articles
  const handleLoadMore = () => {
    const nextPage = pagination.page + 1;
    const totalPages = Math.ceil(pagination.total / pagination.size);

    if (nextPage <= totalPages) {
      fetchArticles(nextPage);
    }
  };

  // Check if there are more articles to load
  const hasMore = pagination.page * pagination.size < pagination.total;

  // Handle export
  const handleExport = async (format: 'json' | 'csv' | 'excel', fields: string[]) => {
    if (articles.length === 0) {
      toast({
        title: '导出失败',
        description: '没有可导出的文章',
        variant: 'destructive',
      });
      return;
    }

    try {
      switch (format) {
        case 'json':
          downloadAsJSON(articles, fields);
          break;
        case 'csv':
          downloadAsCSV(articles, fields);
          break;
        case 'excel':
          downloadAsExcel(articles, fields);
          break;
      }

      toast({
        title: '导出成功',
        description: `已导出 ${articles.length} 篇文章`,
      });
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: '导出失败',
        description: '导出过程中发生错误，请重试',
        variant: 'destructive',
      });
    }
  };

  // Default search params for export dialog
  const defaultSearchParams: SearchParams = {
    page: 1,
    size: pagination.size,
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">文章列表</h1>
          <p className="text-sm text-muted-foreground mt-1">共 {pagination.total} 篇文章</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExportDialogOpen(true)}
            disabled={articles.length === 0}
            className="touch-manipulation"
          >
            <Download className="h-4 w-4 mr-2" />
            导出
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={toggleViewMode}
            title={viewMode === 'grid' ? '切换到列表视图' : '切换到网格视图'}
            className="touch-manipulation"
          >
            {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3x3 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Initial Loading State */}
      {loading && articles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
          <p className="text-muted-foreground">加载文章中...</p>
        </div>
      ) : (
        /* Article List */
        <ArticleList
          articles={articles}
          loading={loading}
          hasMore={hasMore}
          onLoadMore={handleLoadMore}
        />
      )}

      {/* Export Dialog */}
      <ExportDialog
        open={exportDialogOpen}
        onOpenChange={setExportDialogOpen}
        filters={defaultSearchParams}
        onExport={handleExport}
      />
    </div>
  );
}

export default ArticleListPage;
