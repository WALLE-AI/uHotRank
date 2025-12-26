import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Article } from '@/types/article';

interface ArticleCardProps {
  article: Article;
  className?: string;
}

export function ArticleCard({ article, className }: ArticleCardProps) {
  const handleClick = () => {
    // Check if URL exists and is valid
    if (!article.url) {
      console.error('Article URL is missing:', article);
      return;
    }
    
    // Log for debugging
    console.log('Opening article URL:', article.url);
    
    // Open the original article URL directly in a new tab
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return '刚刚';
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    }
  };

  // Truncate content for summary
  const truncateContent = (content: string | undefined, maxLength: number = 150) => {
    if (!content) return '';
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength) + '...';
  };

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-lg active:scale-[0.98] touch-manipulation',
        'hover:scale-[1.02]',
        className
      )}
      onClick={handleClick}
    >
      <CardHeader className="pb-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-base sm:text-lg font-semibold line-clamp-2 flex-1">{article.title}</h3>
          {article.tech_detection?.is_tech_related && (
            <span className="inline-flex items-center rounded-full bg-blue-100 dark:bg-blue-900 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:text-blue-200 shrink-0">
              技术
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground">
          <span className="truncate">{article.category}</span>
          <span>•</span>
          <span className="whitespace-nowrap">{formatDate(article.published_time)}</span>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3">
          {article.content ? truncateContent(article.content) : '暂无内容'}
        </p>
        {article.tech_detection?.categories && article.tech_detection.categories.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {article.tech_detection.categories.slice(0, 3).map((category) => (
              <span
                key={category}
                className="inline-flex items-center rounded-md bg-gray-100 dark:bg-gray-800 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-300"
              >
                {category}
              </span>
            ))}
            {article.tech_detection.categories.length > 3 && (
              <span className="inline-flex items-center rounded-md bg-gray-100 dark:bg-gray-800 px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                +{article.tech_detection.categories.length - 3}
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
