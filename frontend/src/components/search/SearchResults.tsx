import React, { useState } from 'react';
import { ArrowUpDown, FileText, Download } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Button } from '../ui/button';
import { ArticleCard } from '../article/ArticleCard';
import { ExportDialog } from '../export/ExportDialog';
import { useSearchStore } from '../../stores/searchStore';
import { downloadAsJSON, downloadAsCSV, downloadAsExcel } from '../../utils/export';
import { useToast } from '../../hooks/use-toast';
import { cn } from '../../lib/utils';

interface SearchResultsProps {
  className?: string;
}

// Helper function to highlight search keywords in text
const highlightKeyword = (text: string, keyword: string): React.ReactNode => {
  if (!keyword || !text) return text;

  const regex = new RegExp(`(${keyword})`, 'gi');
  const parts = text.split(regex);

  return parts.map((part, index) =>
    regex.test(part) ? (
      <mark key={index} className="bg-yellow-200 dark:bg-yellow-900 text-foreground font-medium">
        {part}
      </mark>
    ) : (
      part
    )
  );
};

export const SearchResults: React.FC<SearchResultsProps> = ({ className }) => {
  const { searchResults, searchParams, updateSearchParams, search, loading } = useSearchStore();
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const { toast } = useToast();

  const handleSortChange = (value: string) => {
    const newParams = {
      ...searchParams,
      sort_by: value as 'relevance' | 'time' | 'popularity',
    };
    updateSearchParams(newParams);
    search(newParams);
  };

  const handleExport = async (format: 'json' | 'csv' | 'excel', fields: string[]) => {
    if (!searchResults || searchResults.articles.length === 0) {
      toast({
        title: '导出失败',
        description: '没有可导出的文章',
        variant: 'destructive',
      });
      return;
    }

    try {
      const articles = searchResults.articles;

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

  if (loading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-between">
          <div className="h-6 w-32 bg-muted animate-pulse rounded" />
          <div className="h-10 w-40 bg-muted animate-pulse rounded" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-64 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (!searchResults) {
    return null;
  }

  const { total, articles } = searchResults;
  const keyword = searchParams.keyword || '';

  return (
    <div className={cn('space-y-4', className)}>
      {/* Results Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            找到 <span className="font-semibold text-foreground">{total}</span> 篇文章
            {keyword && (
              <>
                {' '}
                匹配 "<span className="font-semibold text-foreground">{keyword}</span>"
              </>
            )}
          </span>
        </div>

        {/* Sort Options and Export Button */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setExportDialogOpen(true)}
            disabled={articles.length === 0}
          >
            <Download className="h-4 w-4 mr-2" />
            导出
          </Button>
          <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
          <Select value={searchParams.sort_by || 'time'} onValueChange={handleSortChange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="排序方式" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="relevance">相关度</SelectItem>
              <SelectItem value="time">时间</SelectItem>
              <SelectItem value="popularity">热度</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Results List */}
      {articles.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <ArticleCard
              key={article.id}
              article={{
                ...article,
                // Highlight keyword in title
                title: keyword
                  ? (highlightKeyword(article.title, keyword) as string)
                  : article.title,
              }}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileText className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">未找到匹配的文章</h3>
          <p className="text-sm text-muted-foreground max-w-md">
            尝试调整搜索关键词或筛选条件，或者清除所有筛选重新搜索
          </p>
        </div>
      )}

      {/* Aggregations Summary (if available) */}
      {searchResults.aggregations && (
        <div className="mt-6 p-4 bg-muted/50 rounded-lg">
          <h4 className="text-sm font-medium mb-3">搜索结果分布</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            {searchResults.aggregations.categories && (
              <div>
                <span className="text-muted-foreground">分类:</span>
                <div className="mt-1 space-y-1">
                  {Object.entries(searchResults.aggregations.categories)
                    .slice(0, 3)
                    .map(([category, count]) => (
                      <div key={category} className="flex justify-between">
                        <span>{category}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
            {searchResults.aggregations.sources && (
              <div>
                <span className="text-muted-foreground">来源:</span>
                <div className="mt-1 space-y-1">
                  {Object.entries(searchResults.aggregations.sources)
                    .slice(0, 3)
                    .map(([source, count]) => (
                      <div key={source} className="flex justify-between">
                        <span>{source}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
            {searchResults.aggregations.sentiments && (
              <div>
                <span className="text-muted-foreground">情感:</span>
                <div className="mt-1 space-y-1">
                  {Object.entries(searchResults.aggregations.sentiments).map(
                    ([sentiment, count]) => (
                      <div key={sentiment} className="flex justify-between">
                        <span>
                          {sentiment === 'positive'
                            ? '正面'
                            : sentiment === 'negative'
                              ? '负面'
                              : '中性'}
                        </span>
                        <span className="font-medium">{count}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Export Dialog */}
      <ExportDialog
        open={exportDialogOpen}
        onOpenChange={setExportDialogOpen}
        filters={searchParams}
        onExport={handleExport}
      />
    </div>
  );
};
