"""
测试文档去重检测功能
"""
import logging
from backend.db import ElasticsearchClient, ArticleRepository

logging.basicConfig(level=logging.INFO)

def test_duplicate_detection():
    """测试去重检测"""
    print("=" * 80)
    print("测试文档去重检测功能")
    print("=" * 80)
    
    # 连接 ES
    try:
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client, index_name="test_duplicate")
        print("✅ 连接成功\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # 1. 创建测试索引
        print("1️⃣ 创建测试索引...")
        repo.create_index(delete_if_exists=True)
        print("✅ 索引创建成功\n")
        
        # 2. 插入测试文档
        print("2️⃣ 插入测试文档...")
        test_doc = {
            "title": "GPT-4 发布：OpenAI 的最新突破",
            "category": "AI",
            "content": "OpenAI 今天发布了 GPT-4，这是一个大型多模态模型，能够接受图像和文本输入，并输出文本。GPT-4 在各种专业和学术基准测试中表现出人类水平的性能。",
            "original_url": "https://example.com/gpt4-release",
            "tophub_url": "https://tophub.today/n/xxx",
            "tech_detection": {
                "is_tech_related": True,
                "categories": ["大模型"],
                "confidence": 0.95
            }
        }
        
        repo.create_document(test_doc, doc_id="https://example.com/gpt4-release")
        print("✅ 文档插入成功\n")
        
        # 3. 测试 URL 重复检测
        print("3️⃣ 测试 URL 重复检测...")
        print("-" * 80)
        
        duplicate_doc = {
            "title": "GPT-4 发布的新消息",
            "content": "这是另一篇关于 GPT-4 的文章...",
            "original_url": "https://example.com/gpt4-release",  # 相同 URL
        }
        
        result = repo.check_duplicate(duplicate_doc, check_url=True)
        print(f"是否重复: {result['is_duplicate']}")
        print(f"重复类型: {result['duplicate_type']}")
        print(f"相似度: {result['similarity_score']}")
        if result['duplicate_doc']:
            print(f"重复文档标题: {result['duplicate_doc']['title']}")
        print()
        
        # 4. 测试标题重复检测
        print("4️⃣ 测试标题重复检测...")
        print("-" * 80)
        
        duplicate_title_doc = {
            "title": "GPT-4 发布：OpenAI 的最新突破",  # 相同标题
            "content": "完全不同的内容...",
            "original_url": "https://example.com/different-url",
        }
        
        result = repo.check_duplicate(duplicate_title_doc, check_title=True)
        print(f"是否重复: {result['is_duplicate']}")
        print(f"重复类型: {result['duplicate_type']}")
        print(f"相似度: {result['similarity_score']}")
        print()
        
        # 5. 测试内容相似度检测
        print("5️⃣ 测试内容相似度检测...")
        print("-" * 80)
        
        similar_doc = {
            "title": "OpenAI 推出 GPT-4 模型",
            "content": "OpenAI 最近发布了 GPT-4 大型语言模型，这个模型支持多模态输入，包括图像和文本。在多个基准测试中，GPT-4 展现了接近人类的表现。",
            "original_url": "https://example.com/another-gpt4-article",
        }
        
        result = repo.check_duplicate(
            similar_doc,
            check_url=False,
            check_title=False,
            check_similarity=True,
            similarity_threshold=0.5
        )
        print(f"是否重复: {result['is_duplicate']}")
        print(f"重复类型: {result['duplicate_type']}")
        print(f"相似度: {result['similarity_score']:.2f}")
        if result['duplicate_doc']:
            print(f"相似文档标题: {result['duplicate_doc']['title']}")
        print()
        
        # 6. 测试完全不同的文档
        print("6️⃣ 测试完全不同的文档...")
        print("-" * 80)
        
        different_doc = {
            "title": "Python 3.12 新特性介绍",
            "content": "Python 3.12 带来了许多新特性，包括更快的解释器、改进的错误消息等。",
            "original_url": "https://example.com/python312",
        }
        
        result = repo.check_duplicate(
            different_doc,
            check_url=True,
            check_title=True,
            check_similarity=True
        )
        print(f"是否重复: {result['is_duplicate']}")
        print(f"重复类型: {result['duplicate_type']}")
        print()
        
        # 7. 测试查找相似文档
        print("7️⃣ 测试查找相似文档...")
        print("-" * 80)
        
        similar_docs = repo.find_similar_documents(
            title="GPT-4 的新功能",
            content="GPT-4 是 OpenAI 的最新模型，支持多模态输入",
            min_score=0.3,
            size=5
        )
        
        print(f"找到 {len(similar_docs)} 个相似文档:")
        for i, doc in enumerate(similar_docs, 1):
            print(f"{i}. {doc['title']} (相似度: {doc['_score']:.2f})")
        print()
        
        # 8. 清理测试索引
        print("8️⃣ 清理测试索引...")
        repo.delete_index()
        print("✅ 测试索引已删除\n")
        
        print("=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 清理
        try:
            repo.delete_index()
        except:
            pass
    
    finally:
        es_client.close()
        print("\n✅ 连接已关闭")


if __name__ == "__main__":
    test_duplicate_detection()
