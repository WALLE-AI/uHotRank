import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useArticleStore } from '@/stores/articleStore';
import { ArticleDetail } from '@/components/article';
import { ChevronRight } from 'lucide-react';

export function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentArticle, loading, error, fetchArticleById } = useArticleStore();

  useEffect(() => {
    if (id) {
      fetchArticleById(id);
    }
  }, [id, fetchArticleById]);

  const handleBack = () => {
    navigate('/');
  };

  // Loading state
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
            <p className="text-sm text-muted-foreground">加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <div className="text-red-600 dark:text-red-400 text-lg font-medium">加载失败</div>
            <p className="text-sm text-muted-foreground">{error}</p>
            <button onClick={handleBack} className="text-sm text-primary hover:underline">
              返回列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Not found state
  if (!currentArticle) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <div className="text-muted-foreground text-lg font-medium">文章不存在</div>
            <button onClick={handleBack} className="text-sm text-primary hover:underline">
              返回列表
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <Link to="/" className="hover:text-foreground transition-colors">
          首页
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link to="/" className="hover:text-foreground transition-colors">
          文章列表
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground font-medium line-clamp-1">{currentArticle.title}</span>
      </nav>

      {/* Article Detail */}
      <ArticleDetail article={currentArticle} onBack={handleBack} />
    </div>
  );
}

export default ArticleDetailPage;
