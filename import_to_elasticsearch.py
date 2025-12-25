"""
将 tophub_articles.jsonl 数据导入到 Elasticsearch
"""
import json
import logging
from pathlib import Path

from backend.db import ElasticsearchClient, ArticleRepository

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_jsonl(file_path: str) -> list:
    """
    从 JSONL 文件加载数据
    
    Args:
        file_path: JSONL 文件路径
    
    Returns:
        文档列表
    """
    documents = []
    
    if not Path(file_path).exists():
        logger.error(f"文件不存在: {file_path}")
        return documents
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    doc = json.loads(line)
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    logger.warning(f"第 {line_num} 行 JSON 解析失败: {e}")
                    continue
        
        logger.info(f"✅ 从 {file_path} 加载了 {len(documents)} 条数据")
        return documents
        
    except Exception as e:
        logger.error(f"❌ 读取文件失败: {e}")
        return documents


def import_articles_to_es(
    jsonl_file: str = "tophub_articles.jsonl",
    index_name: str = "tophub_articles",
    recreate_index: bool = False
):
    """
    将文章数据导入到 Elasticsearch
    
    Args:
        jsonl_file: JSONL 文件路径
        index_name: 索引名称
        recreate_index: 是否重新创建索引
    """
    print("=" * 80)
    print("开始导入数据到 Elasticsearch")
    print("=" * 80)
    
    # 1. 加载数据
    print(f"\n📂 正在加载数据: {jsonl_file}")
    documents = load_jsonl(jsonl_file)
    
    if not documents:
        print("❌ 没有数据可导入")
        return
    
    print(f"✅ 成功加载 {len(documents)} 条数据")
    
    # 2. 连接 Elasticsearch
    print("\n🔌 正在连接 Elasticsearch...")
    try:
        es_client = ElasticsearchClient()
        print(f"✅ 连接成功")
        
        # 显示集群信息
        info = es_client.get_info()
        print(f"   版本: {info['version']['number']}")
        print(f"   集群: {info['cluster_name']}")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 请检查:")
        print("   1. Elasticsearch 是否已启动")
        print("   2. .env 文件中的连接配置是否正确")
        print("   3. 环境变量: ELASTICSEARCH_HOST, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD")
        return
    
    # 3. 创建仓库
    print(f"\n📦 正在初始化索引: {index_name}")
    repo = ArticleRepository(es_client, index_name=index_name)
    
    # 4. 创建索引
    if recreate_index or not repo.index_exists():
        print(f"🔨 正在创建索引...")
        if repo.create_index(delete_if_exists=recreate_index):
            print(f"✅ 索引创建成功")
        else:
            print(f"❌ 索引创建失败")
            return
    else:
        print(f"✅ 索引已存在")
    
    # 5. 批量导入数据
    print(f"\n📥 正在导入 {len(documents)} 条数据...")
    try:
        result = repo.bulk_create_documents(documents)
        
        print("\n" + "=" * 80)
        print("导入完成！")
        print("=" * 80)
        print(f"✅ 成功: {result['success']} 条")
        print(f"❌ 失败: {result['failed']} 条")
        
        if result['failed'] > 0 and result['failed_items']:
            print("\n失败的文档:")
            for item in result['failed_items'][:5]:  # 只显示前5个
                print(f"  - {item}")
        
        # 6. 验证导入
        print(f"\n🔍 验证数据...")
        total_count = repo.count()
        print(f"   索引中共有 {total_count} 条文档")
        
        # 统计技术文章
        tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
        print(f"   其中技术相关文章: {tech_count} 条")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 7. 关闭连接
        es_client.close()
        print("\n✅ 连接已关闭")


def test_search():
    """测试搜索功能"""
    print("\n" + "=" * 80)
    print("测试搜索功能")
    print("=" * 80)
    
    try:
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client)
        
        # 1. 关键词搜索
        print("\n🔍 测试关键词搜索: 'GPT'")
        results = repo.search_by_keyword("GPT", size=3)
        print(f"找到 {len(results)} 条结果:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.get('title', 'N/A')}")
            print(f"   分类: {doc.get('category', 'N/A')}")
            print(f"   评分: {doc.get('_score', 0):.2f}")
        
        # 2. 搜索技术文章
        print("\n\n🔍 测试技术文章搜索 (置信度 >= 0.5)")
        tech_articles = repo.search_tech_articles(min_confidence=0.5, size=5)
        print(f"找到 {len(tech_articles)} 条技术文章:")
        for i, doc in enumerate(tech_articles, 1):
            tech_info = doc.get('tech_detection', {})
            print(f"\n{i}. {doc.get('title', 'N/A')}")
            print(f"   分类: {', '.join(tech_info.get('categories', []))}")
            print(f"   置信度: {tech_info.get('confidence', 0)}")
        
        es_client.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入文章数据到 Elasticsearch")
    parser.add_argument(
        "--file",
        default="tophub_articles.jsonl",
        help="JSONL 文件路径 (默认: tophub_articles.jsonl)"
    )
    parser.add_argument(
        "--index",
        default="tophub_articles",
        help="索引名称 (默认: tophub_articles)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="重新创建索引（会删除已有数据）"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="导入后运行搜索测试"
    )
    
    args = parser.parse_args()
    
    # 导入数据
    import_articles_to_es(
        jsonl_file=args.file,
        index_name=args.index,
        recreate_index=args.recreate
    )
    
    # 运行测试
    if args.test:
        test_search()
