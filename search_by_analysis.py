"""
基于内容分析的搜索示例
"""
from backend.db import ElasticsearchClient, ArticleRepository


def main():
    """主函数"""
    print("=" * 80)
    print("基于内容分析的搜索")
    print("=" * 80)
    print()
    
    # 连接 ES
    try:
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client, index_name="tophub_articles")
        print("✅ 连接成功\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # 1. 统计信息
        print("📊 数据统计:")
        print("-" * 80)
        total = repo.count()
        analyzed = repo.count(query={"term": {"content_analysis.analysis_success": True}})
        print(f"总文档数: {total}")
        print(f"已分析文档: {analyzed}")
        print(f"分析率: {analyzed/total*100:.1f}%" if total > 0 else "0%")
        print()
        
        # 2. 热门关键词
        print("🔑 热门关键词 (Top 20):")
        print("-" * 80)
        top_keywords = repo.get_keyword_statistics(top_n=20)
        for i, item in enumerate(top_keywords, 1):
            print(f"{i:2d}. {item['keyword']:<20} {item['count']:>3} 次")
        print()
        
        # 3. 热门主题
        print("📚 热门主题 (Top 10):")
        print("-" * 80)
        top_topics = repo.get_topic_statistics(top_n=10)
        for i, item in enumerate(top_topics, 1):
            print(f"{i:2d}. {item['topic']:<30} {item['count']:>3} 次")
        print()
        
        # 4. 分类统计
        print("📂 分类统计:")
        print("-" * 80)
        categories = repo.get_category_statistics()
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:<20} {count:>3} 篇")
        print()
        
        # 5. 情感统计
        print("😊 情感统计:")
        print("-" * 80)
        sentiments = repo.get_sentiment_statistics()
        sentiment_names = {
            "positive": "积极",
            "neutral": "中性",
            "negative": "消极"
        }
        for sentiment, count in sentiments.items():
            name = sentiment_names.get(sentiment, sentiment)
            print(f"  {name:<10} {count:>3} 篇")
        print()
        
        # 6. 通过关键词搜索
        print("🔍 搜索示例 1: 通过关键词搜索")
        print("-" * 80)
        keyword = input("请输入关键词 (默认: AI): ").strip() or "AI"
        
        results = repo.search_by_keywords([keyword], size=5)
        print(f"\n找到 {len(results)} 条结果:\n")
        
        for i, doc in enumerate(results, 1):
            analysis = doc.get('content_analysis', {})
            print(f"{i}. {doc.get('title', 'N/A')}")
            print(f"   分类: {analysis.get('category', 'N/A')}")
            print(f"   关键词: {', '.join(analysis.get('keywords', [])[:5])}")
            print(f"   情感: {analysis.get('sentiment', 'N/A')}")
            print()
        
        # 7. 通过主题搜索
        print("🔍 搜索示例 2: 通过主题搜索")
        print("-" * 80)
        
        if top_topics:
            topic = top_topics[0]['topic']
            print(f"搜索主题: {topic}\n")
            
            results = repo.search_by_topic(topic, size=5)
            print(f"找到 {len(results)} 条结果:\n")
            
            for i, doc in enumerate(results, 1):
                analysis = doc.get('content_analysis', {})
                print(f"{i}. {doc.get('title', 'N/A')}")
                print(f"   主题: {', '.join(analysis.get('topics', []))}")
                print()
        
        # 8. 通过分类搜索
        print("🔍 搜索示例 3: 通过分类搜索")
        print("-" * 80)
        
        if categories:
            category = list(categories.keys())[0]
            print(f"搜索分类: {category}\n")
            
            results = repo.search_by_category(category, size=5)
            print(f"找到 {len(results)} 条结果:\n")
            
            for i, doc in enumerate(results, 1):
                analysis = doc.get('content_analysis', {})
                print(f"{i}. {doc.get('title', 'N/A')}")
                print(f"   摘要: {analysis.get('summary', 'N/A')[:100]}...")
                print()
        
        # 9. 通过情感搜索
        print("🔍 搜索示例 4: 通过情感搜索")
        print("-" * 80)
        sentiment = input("请输入情感 (positive/neutral/negative，默认: positive): ").strip() or "positive"
        
        results = repo.search_by_sentiment(sentiment, size=5)
        print(f"\n找到 {len(results)} 条结果:\n")
        
        for i, doc in enumerate(results, 1):
            analysis = doc.get('content_analysis', {})
            print(f"{i}. {doc.get('title', 'N/A')}")
            print(f"   情感: {analysis.get('sentiment', 'N/A')}")
            print(f"   摘要: {analysis.get('summary', 'N/A')[:100]}...")
            print()
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        es_client.close()
        print("=" * 80)
        print("✅ 连接已关闭")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
