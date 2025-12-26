import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Article } from '@/types/article';
import { ArrowLeft, ExternalLink } from 'lucide-react';

interface ArticleDetailProps {
  article: Article;
  onBack?: () => void;
  className?: string;
}

export function ArticleDetail({ article, onBack, className }: ArticleDetailProps) {
  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get sentiment label and color
  const getSentimentInfo = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return { label: '积极', color: 'text-green-600 dark:text-green-400' };
      case 'negative':
        return { label: '消极', color: 'text-red-600 dark:text-red-400' };
      case 'neutral':
      default:
        return { label: '中性', color: 'text-gray-600 dark:text-gray-400' };
    }
  };

  return (
    <div className={cn('space-y-4 sm:space-y-6', className)}>
      {/* Back Button */}
      {onBack && (
        <Button 
          variant="ghost" 
          onClick={onBack} 
          className="gap-2 touch-manipulation active:scale-95 transition-transform" 
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4" />
          返回列表
        </Button>
      )}

      {/* Main Article Content */}
      <Card>
        <CardHeader className="space-y-3 sm:space-y-4">
          <div className="space-y-3 sm:space-y-4">
            {/* Title */}
            <h1 className="text-2xl sm:text-3xl font-bold leading-tight">{article.title}</h1>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-muted-foreground">
              <span className="font-medium">{article.category}</span>
              <span>•</span>
              <span className="whitespace-nowrap">{formatDate(article.published_time)}</span>
              {article.tech_detection?.is_tech_related && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center rounded-full bg-blue-100 dark:bg-blue-900 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:text-blue-200">
                    技术文章
                  </span>
                </>
              )}
            </div>

            {/* Original Link */}
            <div>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline touch-manipulation active:scale-95 transition-transform"
              >
                <ExternalLink className="h-4 w-4" />
                查看原文
              </a>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {/* Article Content */}
          <div className="prose prose-sm sm:prose dark:prose-invert max-w-none">
            <p className="whitespace-pre-wrap leading-relaxed text-sm sm:text-base">{article.content}</p>
          </div>
        </CardContent>
      </Card>

      {/* Tech Detection Results */}
      {article.tech_detection && article.tech_detection.is_tech_related && (
        <Card data-testid="tech-detection">
          <CardHeader>
            <CardTitle className="text-lg sm:text-xl">技术检测结果</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4">
            {/* Confidence */}
            <div>
              <h3 className="text-sm font-medium mb-2">置信度</h3>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${article.tech_detection.confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm font-medium whitespace-nowrap">
                  {(article.tech_detection.confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Categories */}
            {article.tech_detection.categories.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">技术分类</h3>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {article.tech_detection.categories.map((category) => (
                    <span
                      key={category}
                      className="inline-flex items-center rounded-md bg-blue-100 dark:bg-blue-900 px-2.5 sm:px-3 py-1 text-xs sm:text-sm font-medium text-blue-800 dark:text-blue-200"
                    >
                      {category}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Matched Keywords */}
            {article.tech_detection.matched_keywords.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">匹配关键词</h3>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {article.tech_detection.matched_keywords.map((keyword, index) => (
                    <span
                      key={`${keyword}-${index}`}
                      className="inline-flex items-center rounded-md bg-gray-100 dark:bg-gray-800 px-2 sm:px-2.5 py-1 text-xs font-medium text-gray-700 dark:text-gray-300"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Content Analysis Results */}
      {article.content_analysis && (
        <Card data-testid="content-analysis">
          <CardHeader>
            <CardTitle className="text-lg sm:text-xl">内容分析结果</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4">
            {/* Summary */}
            {article.content_analysis.summary && (
              <div>
                <h3 className="text-sm font-medium mb-2">摘要</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {article.content_analysis.summary}
                </p>
              </div>
            )}

            {/* Keywords */}
            {article.content_analysis.keywords.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">关键词</h3>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {article.content_analysis.keywords.map((keyword, index) => (
                    <span
                      key={`${keyword}-${index}`}
                      className="inline-flex items-center rounded-md bg-purple-100 dark:bg-purple-900 px-2.5 sm:px-3 py-1 text-xs sm:text-sm font-medium text-purple-800 dark:text-purple-200"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Topics */}
            {article.content_analysis.topics.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">主题</h3>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {article.content_analysis.topics.map((topic, index) => (
                    <span
                      key={`${topic}-${index}`}
                      className="inline-flex items-center rounded-md bg-indigo-100 dark:bg-indigo-900 px-2.5 sm:px-3 py-1 text-xs sm:text-sm font-medium text-indigo-800 dark:text-indigo-200"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Sentiment */}
            <div>
              <h3 className="text-sm font-medium mb-2">情感分析</h3>
              <span
                className={cn(
                  'inline-flex items-center rounded-md px-2.5 sm:px-3 py-1 text-xs sm:text-sm font-medium',
                  getSentimentInfo(article.content_analysis.sentiment).color
                )}
              >
                {getSentimentInfo(article.content_analysis.sentiment).label}
              </span>
            </div>

            {/* Category */}
            {article.content_analysis.category && (
              <div>
                <h3 className="text-sm font-medium mb-2">内容分类</h3>
                <span className="inline-flex items-center rounded-md bg-gray-100 dark:bg-gray-800 px-2.5 sm:px-3 py-1 text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">
                  {article.content_analysis.category}
                </span>
              </div>
            )}

            {/* Entities */}
            {article.content_analysis.entities.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-2">实体识别</h3>
                <div className="space-y-2">
                  {article.content_analysis.entities.map((entity, index) => (
                    <div
                      key={`${entity.name}-${index}`}
                      className="flex items-center gap-2 text-sm"
                    >
                      <span className="inline-flex items-center rounded-md bg-amber-100 dark:bg-amber-900 px-2 py-0.5 text-xs font-medium text-amber-800 dark:text-amber-200">
                        {entity.type}
                      </span>
                      <span className="text-muted-foreground break-all">{entity.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
