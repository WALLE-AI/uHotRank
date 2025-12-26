import time
import random
import csv
import os
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 引入强大的请求库
from curl_cffi import requests as cffi_requests
from playwright.sync_api import sync_playwright

class SafehooStealthSpider:
    def __init__(self):
        self.base_url = "https://www.safehoo.com"
        self.root_url = "https://www.safehoo.com/Build/"
        self.csv_filename = 'safehoo_stealth_data.csv'
        
        # 初始化 CSV 文件
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Title', 'Publish_Date', 'Content', 'URL'])

    def get_html_stealth(self, url):
        """
        [融合核心] 智能获取网页内容
        1. 优先尝试 curl_cffi (速度快，模拟 TLS 指纹)
        2. 如果失败或被拦截，自动降级到 Playwright (能力强，模拟真实浏览器)
        """
        
        # --- 策略 A: 静态请求 (curl_cffi) ---
        # print(f"   [⚡ 静态尝试] {url}") # 调试时可开启
        try:
            response = cffi_requests.get(
                url, 
                impersonate="chrome124", 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Referer": "https://www.safehoo.com/",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # 关键：Safehoo 是老网站，必须手动处理 GBK 编码
                # errors='replace' 防止个别特殊字符导致报错
                return response.content.decode('utf-8', errors='replace')
            elif response.status_code == 404:
                return None # 页面真的不存在
            else:
                print(f"   [⚠️ 静态失败] 状态码: {response.status_code}，准备切换浏览器...")

        except Exception as e:
            print(f"   [⚠️ 静态报错] {e}，准备切换浏览器...")

        # --- 策略 B: 动态浏览器兜底 (Playwright) ---
        print(f"   [🐢 启动浏览器兜底] 正在处理: {url} ...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True, 
                    args=['--disable-blink-features=AutomationControlled'] 
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                # 访问页面
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # [针对 Safehoo 的优化]
                # 等待列表页的列表容器 OR 详情页的正文容器出现
                try:
                    page.wait_for_selector("div.main_list, div.content, td#article_content", timeout=5000)
                except:
                    pass # 超时未找到也不报错，直接拿当前快照

                content = page.content()
                browser.close()
                return content

        except Exception as e:
            print(f"   [❌ 浏览器也失败] {e}")
            return None

    def discover_sub_channels(self):
        """阶段一：从 /Build/ 首页提取所有子版块"""
        print(f"🔍 正在扫描主页子版块: {self.root_url} ...")
        html = self.get_html_stealth(self.root_url)
        if not html:
            print("❌ 无法访问主页，程序终止。")
            return []

        soup = BeautifulSoup(html, 'lxml')
        sub_channels = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            full_url = urljoin(self.root_url, href)
            
            # 过滤逻辑
            path = urlparse(full_url).path
            if "/Build/" in full_url and full_url != self.root_url:
                if full_url.endswith('/') or "." not in path.split('/')[-1]:
                    if "Index.shtml" not in full_url:
                        sub_channels.add((text, full_url))

        channel_list = list(sub_channels)
        print(f"✅ 发现 {len(channel_list)} 个子版块")
        return channel_list

    def parse_detail(self, url, category_name):
        """阶段三：解析详情页内容"""
        html = self.get_html_stealth(url)
        if not html: return None

        soup = BeautifulSoup(html, 'lxml')
        try:
            h1 = soup.find('h1')
            title = h1.get_text(strip=True) if h1 else "无标题"

            content_div = soup.find('div', {'id': 'content'}) or \
                          soup.find('div', {'class': 'content'}) or \
                          soup.find('td', {'id': 'article_content'})
            
            content = ""
            if content_div:
                for tag in content_div(["script", "style"]):
                    tag.decompose()
                content = content_div.get_text('\n', strip=True)

            info_div = soup.find('div', {'class': 'info'})
            date_info = info_div.get_text(strip=True) if info_div else ""

            return [category_name, title, date_info, content, url]
        except:
            return None

    def crawl_channel(self, name, url):
        """阶段二：遍历单个版块"""
        print(f"\n🚀 开始抓取版块: [{name}]")
        
        MAX_PAGES = 50 
        
        for page in range(1, MAX_PAGES + 1):
            if page == 1:
                page_url = url.rstrip('/') + "/Index.shtml"
            else:
                page_url = url.rstrip('/') + f"/List_{page}.shtml"
            
            print(f"   📂 [{name}] 第 {page} 页...")
            html = self.get_html_stealth(page_url)
            
            # 404检测：curl_cffi返回None，playwright可能返回空或错误页
            if not html or "并没有找到您要访问的页面" in html:
                print(f"   🏁 版块 [{name}] 翻页结束")
                break

            soup = BeautifulSoup(html, 'lxml')
            links = soup.select('div.main_list li a, div.catList li a, ul.list li a')
            
            article_links = []
            for link in links:
                href = link.get('href')
                if href:
                    article_links.append(urljoin(page_url, href))
            
            if not article_links:
                if page == 1: break # 空版块
                else: break # 翻页结束

            # 遍历文章
            count = 0
            for art_url in article_links:
                data_row = self.parse_detail(art_url, name)
                if data_row:
                    self.save_to_csv(data_row)
                    count += 1
                    sys.stdout.write(f"\r        已抓取: {count}/{len(article_links)}")
                    sys.stdout.flush()
                
                # 只有在使用 curl_cffi 成功时才需要延时
                # 如果触发了 Playwright，因为启动浏览器本身就很慢，可以减少 sleep
                time.sleep(random.uniform(0.5, 1.0))
            print("") 

    def save_to_csv(self, row):
        with open(self.csv_filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def run(self):
        channels = self.discover_sub_channels()
        for name, link in channels:
            self.crawl_channel(name, link)
        print("\n🎉 全部任务完成！")

if __name__ == "__main__":
    spider = SafehooStealthSpider()
    spider.run()