"""
主程序 - 爬取文章并保存到 Elasticsearch
"""
from backend.agent.agent_today_data import scrape_all_articles_to_es


if __name__ == "__main__":
    print("=" * 80)
    print("TopHub 文章爬虫 - 自动保存到 Elasticsearch")
    print("=" * 80)
    print()
    
    # 询问是否启用内容分析
    enable_analysis = input("是否启用内容分析？(y/n，默认 y): ").strip().lower() != 'n'
    print()
    
    # 爬取所有文章并保存到 ES
    result = scrape_all_articles_to_es(
        es_index_name="tophub_articles",
        batch_size=10,  # 每 10 条批量插入一次
        enable_analysis=enable_analysis  # 启用内容分析
    )
    
    print("\n" + "=" * 80)
    print("任务完成！")
    print("=" * 80)
    print(f"成功: {result['success']} 条")
    print(f"失败: {result['failed']} 条")
    if enable_analysis:
        print(f"已分析: {result['analyzed']} 条")
    print(f"总计: {result['total']} 条")
    
    print("\n💡 提示:")
    print("  - 使用 search_by_analysis.py 查看分析结果和统计")
    print("  - 使用 test_elasticsearch.py 测试搜索功能")
    print("  - 使用 run_crawler.py 选择不同的爬取模式")
