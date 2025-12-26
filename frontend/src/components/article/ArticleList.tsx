import { useEffect, useRef, useCallback } from 'react';
import { ArticleCard } from './ArticleCard';
import { useUIStore } from '@/stores/uiStore';
import { cn } from '@/lib/utils';
import type { Article } from '@/types/article';
import { Loader2 } from 'lucide-react';

interface ArticleListProps {
  articles: Article[];
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  className?: string;
}

export function ArticleList({
  articles,
  loading = false,
  hasMore = false,
  onLoadMore,
  className,
}: ArticleListProps) {
  const viewMode = useUIStore((state) => state.viewMode);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Infinite scroll implementation with optimized threshold
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasMore && !loading && onLoadMore) {
        onLoadMore();
      }
    },
    [hasMore, loading, onLoadMore]
  );

  useEffect(() => {
    const element = loadMoreRef.current;
    if (!element) return;

    observerRef.current = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '200px', // Increased for better UX
      threshold: 0.1,
    });

    observerRef.current.observe(element);

    return () => {
      if (observerRef.current && element) {
        observerRef.current.unobserve(element);
      }
    };
  }, [handleObserver]);

  // Empty state
  if (!loading && articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-muted p-6 mb-4">
          <svg
            className="w-12 h-12 text-muted-foreground"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">暂无文章</h3>
        <p className="text-sm text-muted-foreground">当前没有找到任何文章，请尝试调整筛选条件</p>
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)}>
      {/* Article Grid/List with optimized rendering */}
      <div
        className={cn(
          'gap-4 sm:gap-6',
          viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3' 
            : 'flex flex-col'
        )}
      >
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <span className="ml-2 text-sm text-muted-foreground">加载中...</span>
        </div>
      )}

      {/* Infinite Scroll Trigger */}
      {hasMore && !loading && <div ref={loadMoreRef} className="h-10 w-full" />}

      {/* No More Data */}
      {!hasMore && articles.length > 0 && !loading && (
        <div className="text-center py-8 text-sm text-muted-foreground">已加载全部文章</div>
      )}
    </div>
  );
}
