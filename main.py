# --- 主程序 ---
import os
import random
import time
from backend.agent.agent_today_data import MAX_SLEEP, MIN_SLEEP, OUTPUT_FILE, gentle_scrape_content, get_homepage_links, save_to_file, scrape_tophub_dynamic_link


if __name__ == "__main__":
    # 1. 获取列表
    articles_list = scrape_tophub_dynamic_link()
    
    # 限制测试数量 (如果只是测试，取消下面这行的注释)
    # articles_list = articles_list[:5] 
    
    print(f"\n🚀 开始温和爬取任务，共 {len(articles_list)} 篇...")
    print(f"💾 数据将实时保存至: {os.path.abspath(OUTPUT_FILE)}\n")

    for i, item in enumerate(articles_list[:5]):
        print(f"[{i+1}/{len(articles_list)}] 正在处理: {item['title'][:20]}...")
        
        # 2. 执行爬取
        content_data = gentle_scrape_content(item)
        
        # 3. 实时保存
        save_to_file(content_data)
        
        # 4. 判断结果并打印反馈
        if "content" in content_data and len(content_data['content']) > 50:
             print(f"   -> 成功! (正文约 {len(content_data['content'])} 字)")
        else:
             print(f"   -> 抓取内容较少或失败 (可能需要登录或为图片/视频内容)")

        # 5. 【关键】随机温和等待
        # 模拟人类阅读完一篇文章后，发呆几秒再点下一篇
        sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
        print(f"   -> ☕ 休息 {sleep_time:.2f} 秒...\n")
        time.sleep(sleep_time)

    print("🎉 所有任务处理完毕！")