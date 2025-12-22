import requests
from bs4 import BeautifulSoup
from newspaper import Article
from fake_useragent import UserAgent  # 用于随机生成 User-Agent
import time
import random
import json
import os
from playwright.sync_api import sync_playwright

# --- 配置区域 ---
OUTPUT_FILE = "tophub_articles.jsonl"  # 结果保存文件 (json lines 格式)
MIN_SLEEP = 3  # 最短等待时间 (秒)
MAX_SLEEP = 8  # 最长等待时间 (秒)

def get_random_headers():
    """
    随机生成请求头，伪装成不同浏览器
    """
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        # 如果库加载失败，使用备用的 UA 列表
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        user_agent = random.choice(user_agent_list)
        
    return {
        "User-Agent": user_agent,
        "Referer": "https://tophub.today/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

def save_to_file(data):
    """
    增量保存：爬一条存一条，防止程序中断丢失数据
    使用 JSONL 格式 (每行一个 JSON)，方便后续处理
    """
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
        

def scrape_tophub_dynamic_link():
    with sync_playwright() as p:
        # 启动浏览器 (headless=True 表示无头模式，不显示界面)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("正在加载页面...")
        page.goto("https://tophub.today")
        
        # 等待主要的榜单元素加载完成 (根据实际 DOM 结构替换选择器)
        # 例如等待包含 '热门' 字样的元素或特定的卡片 class
        try:
            page.wait_for_selector("div.cc-cd", timeout=10000)
        except:
            print("页面加载超时或结构已变")
            browser.close()
            return

        # 获取所有榜单卡片
        nodes = page.query_selector_all("div.cc-cd")
        
        results = []
        
        for node in nodes[-2:]:
            # 获取榜单标题
            category_el = node.query_selector("div.cc-cd-lb")
            category = category_el.inner_text().strip() if category_el else "Unknown"
            
            # 获取榜单内的链接
            links = node.query_selector_all("a")
            
            for link in links:
                title_el = link.query_selector("span.t")
                if title_el:
                    title = title_el.inner_text().strip()
                    url = link.get_attribute("href")
                    results.append(
                        {"category": category, "title": title, "tophub_url": url}
                        )

        browser.close()
        return results

def get_homepage_links():
    """获取首页所有文章链接"""
    url = "https://tophub.today"
    print(f"📡 正在获取首页列表: {url} ...")
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有榜单节点
        nodes = soup.find_all('div', class_='cc-cd')
        
        all_articles = []
        for node in nodes:
            # 获取榜单分类名称
            header = node.find('div', class_='cc-cd-lb')
            category = header.get_text(strip=True) if header else "其他"
            
            # 获取该榜单下的文章
            items = node.find_all('a', href=True)
            for item in items:
                title_tag = item.find('span', class_='t')
                title = title_tag.get_text(strip=True) if title_tag else item.get_text(strip=True)
                link = item['href']
                
                # 处理相对链接
                if not link.startswith('http'):
                    link = url + link
                
                # 简单过滤非文章链接
                if title and "查看更多" not in title:
                    all_articles.append({
                        "category": category,
                        "title": title,
                        "tophub_url": link
                    })
        
        print(f"✅ 成功发现 {len(all_articles)} 篇文章链接。")
        return all_articles
        
    except Exception as e:
        print(f"❌ 获取首页失败: {e}")
        return []

def gentle_scrape_content(article_info):
    """
    对单篇文章进行温和爬取
    """
    url = article_info['tophub_url']
    
    try:
        # newspaper3k 配置
        # browser_user_agent 属性非常重要，newspaper 默认 UA 很容易被封
        article = Article(url, language='zh', browser_user_agent=get_random_headers()['User-Agent'])
        
        article.download()
        article.parse()
        
        # 组装数据
        result = {
            "title": article_info['title'],
            "category": article_info['category'],
            "original_url": article.url, # 跳转后的真实地址
            "publish_date": str(article.publish_date) if article.publish_date else None,
            "content": article.text,
            "images": list(article.images), # 获取图片列表
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return result

    except Exception as e:
        # 即使失败也返回基本信息，标记错误
        return {
            "title": article_info['title'],
            "category": article_info['category'],
            "error": str(e),
            "status": "failed"
        }

