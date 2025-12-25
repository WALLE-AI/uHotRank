"""
搜索示例 - 演示如何从 Elasticsearch 搜索文章
"""
from backend.db import ElasticsearchClient, ArticleRepository

def main():
    """主函数"""
    print("=" * 80)
    print("Elasticsearch 搜索示例")
    print("=" * 80)
    
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
        tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
        print(f"总文档数: {total}")
        print(f"技术文章数: {tech_count}")
        print()
        
        # 2. 关键词搜索
        print("🔍 关键词搜索: 'GPT'")
        print("-" * 80)
        results = repo.search_by_keyword("GPT", size=5)
        if results:
            for i, doc in enumerate(results, 1):
                print(f"{i}. {doc['title']}")
                print(f"   分类: {doc.get('category', 'N/A')}")
                print(f"   评分: {doc['_score']:.2f}")
                print(f"   URL: {doc.get('original_url', 'N/A')}")
                print()
        else:
            print("未找到相关文章\n")
        
        # 3. 搜索技术文章
        print("🤖 技术文章搜索 (置信度 >= 0.5)")
        print("-" * 80)
        tech_articles = repo.search_tech_articles(min_confidence=0.5, size=5)
        if tech_articles:
            for i, doc in enumerate(tech_articles, 1):
                tech_info = doc.get('tech_detection', {})
                print(f"{i}. {doc['title']}")
                print(f"   分类: {', '.join(tech_info.get('categories', []))}")
                print(f"   置信度: {tech_info.get('confidence', 0)}")
                print(f"   关键词: {', '.join(tech_info.get('keywords', [])[:5])}")
                print()
        else:
            print("未找到技术文章\n")
        
        # 4. 搜索特定分类
        print("🔬 搜索特定分类: '大模型'")
        print("-" * 80)
        llm_articles = repo.search_tech_articles(
            categories=["大模型"],
            min_confidence=0.3,
            size=5
        )
        if llm_articles:
            for i, doc in enumerate(llm_articles, 1):
                tech_info = doc.get('tech_detection', {})
                print(f"{i}. {doc['title']}")
                print(f"   置信度: {tech_info.get('confidence', 0)}")
                print()
        else:
            print("未找到相关文章\n")
        
        # 5. 自定义搜索
        print("🎯 自定义搜索: 标题包含 '开源' 的文章")
        print("-" * 80)
        query = {
            "match": {
                "title": "开源"
            }
        }
        result = repo.search(query=query, size=5)
        hits = result.get("hits", {}).get("hits", [])
        if hits:
            for i, hit in enumerate(hits, 1):
                doc = hit["_source"]
                print(f"{i}. {doc['title']}")
                print(f"   分类: {doc.get('category', 'N/A')}")
                print()
        else:
            print("未找到相关文章\n")
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭连接
        es_client.close()
        print("=" * 80)
        print("✅ 连接已关闭")


if __name__ == "__main__":
    main()
