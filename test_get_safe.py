import requests
from bs4 import BeautifulSoup
import time
import random
import csv

# 1. 配置请求头，模拟浏览器（反爬虫基础）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.safehoo.com/Build/'
}

# 2. 基础配置
BASE_URL = "https://www.safehoo.com"
START_URL = "https://www.safehoo.com/Build/" 
# 注意：你需要手动检查该网站的分页规律，假设是 /List_X.shtml 格式
# 如果首页和分页URL规则不同，需要特殊处理

def get_html(url):
    """发送请求并获取HTML内容，自动处理编码"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        # 关键：识别网页编码，防止中文乱码
        # safehoo 可能是 gb2312，这里让 requests 自动推断或指定 'gb18030'
        response.encoding = response.apparent_encoding 
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"请求失败: {url}, 错误: {e}")
    return None

def parse_list_page(html):
    """解析列表页，提取文章链接"""
    soup = BeautifulSoup(html, 'lxml')
    links = []
    
    # [需要修改]：请在浏览器F12中找到列表链接的 CSS 选择器
    # 假设文章列表在 <ul class="list"> 下的 <li> 中
    # 示例选择器： 'div.catList li a' (这只是猜测，需替换为真实值)
    article_tags = soup.select('div.main_list li a') 

    for tag in article_tags:
        link = tag.get('href')
        title = tag.get_text().strip()
        
        # 处理相对路径
        if link and not link.startswith('http'):
            # 有些链接可能是 ../ 开头，需要拼接
            full_link = BASE_URL + link if link.startswith('/') else BASE_URL + '/Build/' + link
            links.append({'title': title, 'url': full_link})
        elif link:
            links.append({'title': title, 'url': link})
            
    return links

def parse_detail_page(url):
    """解析详情页，提取正文内容"""
    html = get_html(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'lxml')
    data = {}
    
    try:
        # [需要修改]：根据实际详情页结构修改选择器
        # 提取标题
        data['title'] = soup.select_one('h1').get_text().strip()
        
        # 提取正文
        content_div = soup.select_one('div.content') # 假设正文在 class="content"
        if content_div:
            data['content'] = content_div.get_text().strip()
        else:
            data['content'] = "未找到正文"
            
        # 提取发布时间 (根据实际结构调整)
        info_text = soup.select_one('div.info').get_text() # 假设信息栏
        data['date'] = info_text  # 后续可以用正则提取具体日期
        
        data['url'] = url
        
    except AttributeError:
        print(f"解析详情页出错: {url}")
        return None
        
    return data

def main():
    # 存储文件
    with open('safehoo_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'date', 'content', 'url'])
        writer.writeheader()
        
        # 假设我们要爬取前 5 页
        for page in range(1, 6): 
            print(f"--- 正在爬取第 {page} 页 ---")
            
            # [需要修改]：构造分页 URL
            # 这里的 URL 构造逻辑需要你去网站实际点一下"下一页"来看看规律
            # 往往是: https://www.safehoo.com/Build/List_1.shtml 等
            if page == 1:
                url = "https://www.safehoo.com/Build/Index.shtml" # 或者是默认页
            else:
                url = f"https://www.safehoo.com/Build/List_{page}.shtml" # 示例
            
            html = get_html(url)
            if not html:
                continue
                
            article_links = parse_list_page(html)
            
            for item in article_links:
                print(f"正在抓取: {item['title']}")
                detail_data = parse_detail_page(item['url'])
                
                if detail_data:
                    writer.writerow(detail_data)
                
                # ⚠️ 关键：礼貌爬取，随机休眠 1-3 秒
                time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    main()