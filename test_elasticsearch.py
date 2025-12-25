"""
快速测试 Elasticsearch 连接和基本功能
"""
import logging
from backend.db import ElasticsearchClient, ArticleRepository

logging.basicConfig(level=logging.INFO)

def test_connection():
    """测试连接"""
    print("=" * 60)
    print("测试 Elasticsearch 连接")
    print("=" * 60)
    
    try:
        es_client = ElasticsearchClient()
        
        if es_client.ping():
            print("✅ 连接成功！")
            
            info = es_client.get_info()
            print(f"\n集群信息:")
            print(f"  名称: {info['cluster_name']}")
            print(f"  版本: {info['version']['number']}")
            print(f"  Lucene: {info['version']['lucene_version']}")
            
            return es_client
        else:
            print("❌ 连接失败")
            return None
            
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        print("\n💡 请检查:")
        print("  1. Elasticsearch 是否已启动")
        print("  2. .env 文件配置是否正确")
        print("  3. 环境变量: ELASTICSEARCH_HOST, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD")
        return None


def test_crud_operations(es_client):
    """测试 CRUD 操作"""
    print("\n" + "=" * 60)
    print("测试 CRUD 操作")
    print("=" * 60)
    
    repo = ArticleRepository(es_client, index_name="test_articles")
    
    try:
        # 1. 创建索引
        print("\n1️⃣ 创建测试索引...")
        repo.create_index(delete_if_exists=True)
        print("✅ 索引创建成功")
        
        # 2. 创建文档
        print("\n2️⃣ 创建测试文档...")
        test_doc = {
            "title": "测试文章：GPT-4 发布",
            "category": "AI",
            "content": "OpenAI 发布了最新的 GPT-4 模型，支持更长的上下文窗口和更强的推理能力。",
            "original_url": "https://example.com/test-article",
            "tech_detection": {
                "is_tech_related": True,
                "categories": ["大模型"],
                "keywords": ["GPT-4", "OpenAI"],
                "confidence": 0.95,
                "summary": "检测到大模型相关内容"
            }
        }
        
        result = repo.create_document(test_doc, doc_id="test-1")
        print(f"✅ 文档创建成功: {result['_id']}")
        
        # 3. 批量创建
        print("\n3️⃣ 批量创建文档...")
        batch_docs = [
            {
                "title": "LangChain 新版本发布",
                "category": "开源",
                "content": "LangChain 发布了支持 Multi-Agent 的新版本",
                "original_url": "https://example.com/langchain",
                "tech_detection": {
                    "is_tech_related": True,
                    "categories": ["AI框架", "Agent技术"],
                    "confidence": 0.88
                }
            },
            {
                "title": "今日股市行情",
                "category": "财经",
                "content": "A股今日收涨",
                "original_url": "https://example.com/stock",
                "tech_detection": {
                    "is_tech_related": False,
                    "confidence": 0.1
                }
            }
        ]
        
        result = repo.bulk_create_documents(batch_docs)
        print(f"✅ 批量创建完成: 成功 {result['success']} 条")
        
        # 4. 读取文档
        print("\n4️⃣ 读取文档...")
        doc = repo.get_document("test-1")
        if doc:
            print(f"✅ 读取成功: {doc['title']}")
        
        # 5. 更新文档
        print("\n5️⃣ 更新文档...")
        repo.update_document("test-1", {"category": "大模型"})
        print("✅ 更新成功")
        
        # 6. 搜索
        print("\n6️⃣ 关键词搜索...")
        results = repo.search_by_keyword("GPT", size=5)
        print(f"✅ 找到 {len(results)} 条结果")
        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc['title']} (评分: {doc['_score']:.2f})")
        
        # 7. 技术文章搜索
        print("\n7️⃣ 技术文章搜索...")
        tech_articles = repo.search_tech_articles(min_confidence=0.5, size=10)
        print(f"✅ 找到 {len(tech_articles)} 条技术文章")
        for i, doc in enumerate(tech_articles, 1):
            tech_info = doc.get('tech_detection', {})
            print(f"   {i}. {doc['title']}")
            print(f"      分类: {', '.join(tech_info.get('categories', []))}")
            print(f"      置信度: {tech_info.get('confidence', 0)}")
        
        # 8. 统计
        print("\n8️⃣ 统计文档...")
        total = repo.count()
        tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
        print(f"✅ 总文档: {total} 条")
        print(f"✅ 技术文章: {tech_count} 条")
        
        # 9. 删除文档
        print("\n9️⃣ 删除文档...")
        repo.delete_document("test-1")
        print("✅ 删除成功")
        
        # 10. 清理：删除测试索引
        print("\n🔟 清理测试索引...")
        repo.delete_index()
        print("✅ 测试索引已删除")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 清理
        try:
            repo.delete_index()
        except:
            pass


if __name__ == "__main__":
    # 测试连接
    es_client = test_connection()
    
    if es_client:
        # 测试 CRUD
        test_crud_operations(es_client)
        
        # 关闭连接
        es_client.close()
        print("\n✅ 连接已关闭")
    else:
        print("\n❌ 无法继续测试，请先解决连接问题")
