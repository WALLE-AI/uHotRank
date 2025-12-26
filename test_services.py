"""Simple test to verify service layer implementation."""

import asyncio
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository
from backend.service.article_service import ArticleService
from backend.service.crawler_service import CrawlerService
from backend.service.stats_service import StatsService


def test_article_service():
    """测试 ArticleService"""
    print("=" * 60)
    print("测试 ArticleService")
    print("=" * 60)
    
    try:
        # 初始化
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client, index_name="tophub_articles")
        service = ArticleService(repo)
        
        # 测试获取文章列表
        print("\n1. 测试获取文章列表...")
        result = service.get_articles(page=1, size=5)
        print(f"   总数: {result.total}")
        print(f"   当前页: {result.page}")
        print(f"   每页数量: {result.size}")
        print(f"   返回文章数: {len(result.articles)}")
        if result.articles:
            print(f"   第一篇文章: {result.articles[0].title}")
        
        # 测试获取文章详情
        if result.articles:
            print("\n2. 测试获取文章详情...")
            article_id = result.articles[0].id
            detail = service.get_article_by_id(article_id)
            if detail:
                print(f"   文章标题: {detail.title}")
                print(f"   文章分类: {detail.category}")
                print(f"   内容长度: {len(detail.content)} 字符")
            else:
                print("   未找到文章")
        
        print("\n✅ ArticleService 测试通过")
        es_client.close()
        
    except Exception as e:
        print(f"\n❌ ArticleService 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_crawler_service():
    """测试 CrawlerService"""
    print("\n" + "=" * 60)
    print("测试 CrawlerService")
    print("=" * 60)
    
    try:
        # 初始化
        service = CrawlerService()
        
        # 测试获取状态
        print("\n1. 测试获取爬虫状态...")
        status = await service.get_status()
        print(f"   运行状态: {status.is_running}")
        print(f"   当前状态: {status.current_status}")
        
        # 测试获取历史记录
        print("\n2. 测试获取历史记录...")
        history = await service.get_history(page=1, size=5)
        print(f"   历史记录总数: {history.total}")
        print(f"   当前页记录数: {len(history.items)}")
        
        print("\n✅ CrawlerService 测试通过")
        
    except Exception as e:
        print(f"\n❌ CrawlerService 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_stats_service():
    """测试 StatsService"""
    print("\n" + "=" * 60)
    print("测试 StatsService")
    print("=" * 60)
    
    try:
        # 初始化
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client, index_name="tophub_articles")
        service = StatsService(repo)
        
        # 测试总体统计
        print("\n1. 测试总体统计...")
        overall = service.get_overall_statistics()
        print(f"   文章总数: {overall.total_articles}")
        print(f"   今日新增: {overall.today_new}")
        print(f"   技术文章: {overall.tech_articles}")
        print(f"   已分析文章: {overall.analyzed_articles}")
        print(f"   分类数量: {overall.categories_count}")
        print(f"   平均情感分数: {overall.avg_sentiment_score}")
        
        # 测试关键词统计
        print("\n2. 测试关键词统计...")
        keywords = service.get_keyword_stats(top_n=5)
        print(f"   关键词数量: {len(keywords.keywords)}")
        if keywords.keywords:
            print("   Top 5 关键词:")
            for i, kw in enumerate(keywords.keywords[:5], 1):
                print(f"      {i}. {kw.keyword}: {kw.count}")
        
        # 测试分类统计
        print("\n3. 测试分类统计...")
        categories = service.get_category_stats()
        print(f"   分类数量: {len(categories.categories)}")
        if categories.categories:
            print("   分类分布:")
            for cat, count in list(categories.categories.items())[:5]:
                print(f"      {cat}: {count}")
        
        # 测试情感统计
        print("\n4. 测试情感统计...")
        sentiments = service.get_sentiment_stats()
        print(f"   正面: {sentiments.positive}")
        print(f"   中性: {sentiments.neutral}")
        print(f"   负面: {sentiments.negative}")
        
        # 测试来源统计
        print("\n5. 测试来源统计...")
        sources = service.get_source_stats()
        print(f"   来源数量: {len(sources.sources)}")
        if sources.sources:
            print("   来源分布:")
            for source, count in list(sources.sources.items())[:5]:
                print(f"      {source}: {count}")
        
        print("\n✅ StatsService 测试通过")
        es_client.close()
        
    except Exception as e:
        print(f"\n❌ StatsService 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("开始测试服务层实现...\n")
    
    # 测试 ArticleService
    test_article_service()
    
    # 测试 CrawlerService
    asyncio.run(test_crawler_service())
    
    # 测试 StatsService
    test_stats_service()
    
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
