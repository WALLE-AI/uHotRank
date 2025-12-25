"""
带内容分析的爬虫脚本
"""
import asyncio
import logging
from backend.agent.agent_today_data import (
    scrape_tophub_dynamic_link,
    gentle_scrape_content,
    MIN_SLEEP,
    MAX_SLEEP
)
from backend.agent.agent_content_keyword_analysis import analyze_article_keywords
from backend.db import ElasticsearchClient, ArticleRepository
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_with_content_analysis(
    es_index_name: str = "tophub_articles",
    enable_analysis: bool = True,
    check_duplicate: bool = True,
    skip_duplicate: bool = True
):
    """
    爬取文章并进行内容分析，保存到 Elasticsearch
    
    Args:
        es_index_name: Elasticsearch 索引名称
        enable_analysis: 是否启用内容分析
        check_duplicate: 是否检查重复
        skip_duplicate: 是否跳过重复
    
    Returns:
        dict: 统计信息
    """
    print("=" * 80)
    print("开始爬取文章并进行内容分析")
    print("=" * 80)
    
    # 1. 连接 ES
    try:
        print("\n🔌 正在连接 Elasticsearch...")
        es_client = ElasticsearchClient()
        repo = ArticleRepository(es_client, index_name=es_index_name)
        
        # 确保索引存在
        if not repo.index_exists():
            print(f"📦 创建索引: {es_index_name}")
            repo.create_index()
        else:
            print(f"✅ 索引已存在: {es_index_name}")
            
    except Exception as e:
        logger.error(f"❌ 连接 Elasticsearch 失败: {e}")
        return {"success": 0, "failed": 0, "duplicate": 0, "analyzed": 0, "error": str(e)}
    
    # 2. 获取文章列表
    articles = scrape_tophub_dynamic_link()
    if not articles:
        print("❌ 未获取到文章列表")
        es_client.close()
        return {"success": 0, "failed": 0, "duplicate": 0, "analyzed": 0, "error": "未获取到文章列表"}
    
    print(f"\n📊 共获取 {len(articles)} 篇文章，开始爬取内容...\n")
    if enable_analysis:
        print(f"🤖 内容分析: 已启用\n")
    if check_duplicate:
        print(f"🔍 重复检测: 已启用 (跳过模式: {'是' if skip_duplicate else '否'})\n")
    
    # 3. 爬取并分析
    success_count = 0
    failed_count = 0
    duplicate_count = 0
    analyzed_count = 0
    
    for i, article_info in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] 正在爬取: {article_info['title']}")
        
        # 爬取内容
        article_content = gentle_scrape_content(article_info)
        
        if article_content.get('status') == 'failed':
            failed_count += 1
            time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))
            continue
        
        # 检查重复
        is_duplicate = False
        if check_duplicate:
            dup_result = repo.check_duplicate(
                article_content,
                check_url=True,
                check_title=True,
                check_similarity=False
            )
            
            if dup_result['is_duplicate']:
                duplicate_count += 1
                dup_type = dup_result['duplicate_type']
                
                if skip_duplicate:
                    print(f"   ⏭️  跳过重复文档 (类型: {dup_type})")
                    is_duplicate = True
                else:
                    print(f"   🔄 将覆盖重复文档 (类型: {dup_type})")
        
        if not is_duplicate:
            # 进行内容分析
            if enable_analysis:
                try:
                    print(f"   🤖 正在分析内容...")
                    analysis_result = await analyze_article_keywords(
                        title=article_content.get('title', ''),
                        content=article_content.get('content', '')
                    )
                    
                    article_content['content_analysis'] = analysis_result
                    
                    if analysis_result.get('analysis_success'):
                        analyzed_count += 1
                        keywords = analysis_result.get('keywords', [])
                        category = analysis_result.get('category', '')
                        print(f"   ✅ 分析完成: {category} | 关键词: {', '.join(keywords[:3])}")
                    else:
                        print(f"   ⚠️  分析失败")
                        
                except Exception as e:
                    logger.error(f"   ❌ 内容分析失败: {e}")
                    article_content['content_analysis'] = {
                        "keywords": [],
                        "topics": [],
                        "summary": "",
                        "sentiment": "neutral",
                        "category": "未分类",
                        "entities": [],
                        "analysis_success": False
                    }
            
            # 保存到 ES
            try:
                doc_id = article_content.get('original_url') or article_content.get('tophub_url')
                repo.create_document(article_content, doc_id=doc_id)
                success_count += 1
                print(f"   💾 已保存到 ES")
            except Exception as e:
                logger.error(f"   ❌ 保存失败: {e}")
                failed_count += 1
        
        # 礼貌等待
        time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))
    
    # 4. 显示统计信息
    print("\n" + "=" * 80)
    print("爬取完成！")
    print("=" * 80)
    print(f"✅ 成功: {success_count} 条")
    print(f"❌ 失败: {failed_count} 条")
    if check_duplicate:
        print(f"⏭️  重复: {duplicate_count} 条")
    if enable_analysis:
        print(f"🤖 已分析: {analyzed_count} 条")
    
    # 5. 显示 ES 统计
    try:
        total_count = repo.count()
        analyzed_in_es = repo.count(query={"term": {"content_analysis.analysis_success": True}})
        
        print(f"\n📊 Elasticsearch 统计:")
        print(f"   索引: {es_index_name}")
        print(f"   总文档数: {total_count}")
        print(f"   已分析文档: {analyzed_in_es}")
        
        # 显示关键词统计
        if enable_analysis:
            print(f"\n🔑 热门关键词:")
            top_keywords = repo.get_keyword_statistics(top_n=10)
            for i, item in enumerate(top_keywords[:10], 1):
                print(f"   {i}. {item['keyword']}: {item['count']} 次")
            
            print(f"\n📚 热门主题:")
            top_topics = repo.get_topic_statistics(top_n=5)
            for i, item in enumerate(top_topics[:5], 1):
                print(f"   {i}. {item['topic']}: {item['count']} 次")
            
            print(f"\n📂 分类统计:")
            categories = repo.get_category_statistics()
            for category, count in list(categories.items())[:5]:
                print(f"   {category}: {count} 篇")
            
            print(f"\n😊 情感统计:")
            sentiments = repo.get_sentiment_statistics()
            for sentiment, count in sentiments.items():
                print(f"   {sentiment}: {count} 篇")
                
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
    
    # 6. 关闭连接
    es_client.close()
    print("\n✅ Elasticsearch 连接已关闭")
    
    return {
        "success": success_count,
        "failed": failed_count,
        "duplicate": duplicate_count,
        "analyzed": analyzed_count,
        "total": success_count + failed_count + duplicate_count
    }


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("带内容分析的文章爬虫")
    print("=" * 80)
    print()
    
    # 配置选项
    enable_analysis = input("是否启用内容分析？(y/n，默认 y): ").strip().lower() != 'n'
    check_duplicate = input("是否启用去重检测？(y/n，默认 y): ").strip().lower() != 'n'
    
    skip_duplicate = True
    if check_duplicate:
        skip_duplicate = input("是否跳过重复文档？(y/n，默认 y): ").strip().lower() != 'n'
    
    print()
    
    # 运行爬虫
    result = await scrape_with_content_analysis(
        es_index_name="tophub_articles",
        enable_analysis=enable_analysis,
        check_duplicate=check_duplicate,
        skip_duplicate=skip_duplicate
    )
    
    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
