"""
运行爬虫并保存到 Elasticsearch
"""
from backend.agent.agent_today_data import (
    scrape_and_filter_tech_articles,
    scrape_all_articles_to_es
)

def main():
    """主函数"""
    print("选择运行模式:")
    print("1. 爬取所有文章并保存到 ES（批量模式，推荐）")
    print("2. 爬取并筛选技术文章（同时保存到 ES 和 JSONL）")
    print("3. 只爬取技术文章到 ES（不保存 JSONL）")
    
    choice = input("\n请输入选项 (1/2/3，默认 1): ").strip() or "1"
    
    # 询问是否启用去重检测
    check_dup = input("是否启用去重检测？(y/n，默认 y): ").strip().lower()
    check_duplicate = check_dup != 'n'
    
    skip_dup = True
    if check_duplicate:
        skip_dup_input = input("是否跳过重复文档？(y/n，默认 y): ").strip().lower()
        skip_duplicate = skip_dup_input != 'n'
    else:
        skip_duplicate = False
    
    print("\n" + "=" * 80)
    print(f"配置:")
    print(f"  去重检测: {'启用' if check_duplicate else '禁用'}")
    if check_duplicate:
        print(f"  重复处理: {'跳过' if skip_duplicate else '覆盖'}")
    print("=" * 80 + "\n")
    
    if choice == "1":
        # 模式 1：批量爬取所有文章
        print("开始批量爬取所有文章...")
        result = scrape_all_articles_to_es(
            es_index_name="tophub_articles",
            batch_size=10,
            check_duplicate=check_duplicate,
            skip_duplicate=skip_duplicate
        )
        print(f"\n最终结果:")
        print(f"  成功: {result['success']} 条")
        print(f"  失败: {result['failed']} 条")
        if check_duplicate:
            print(f"  重复: {result['duplicate']} 条")
        
    elif choice == "2":
        # 模式 2：爬取并筛选技术文章（保存到 ES 和 JSONL）
        print("开始爬取并筛选技术文章...")
        tech_articles = scrape_and_filter_tech_articles(
            save_to_es=True,
            save_to_jsonl=True,
            es_index_name="tophub_articles",
            check_duplicate=check_duplicate,
            skip_duplicate=skip_duplicate
        )
        print(f"\n共发现 {len(tech_articles)} 篇技术文章")
        
    elif choice == "3":
        # 模式 3：只保存到 ES
        print("开始爬取技术文章（仅保存到 ES）...")
        tech_articles = scrape_and_filter_tech_articles(
            save_to_es=True,
            save_to_jsonl=False,
            es_index_name="tophub_articles",
            check_duplicate=check_duplicate,
            skip_duplicate=skip_duplicate
        )
        print(f"\n共发现 {len(tech_articles)} 篇技术文章")
        
    else:
        print("无效的选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
