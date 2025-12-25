import requests
from bs4 import BeautifulSoup
from newspaper import Article
from fake_useragent import UserAgent  # 用于随机生成 User-Agent
import time
import random
import json
import os
from playwright.sync_api import sync_playwright
import logging
import uuid
import asyncio
from curl_cffi import requests as cffi_requests # [修复] 添加缺失的导入

# [保留你的后端引用]
try:
    from backend.utils.url_to_markdown import Crawler, ReadabilityExtractor
    from backend.db import ElasticsearchClient, ArticleRepository
    from backend.agent.agent_content_keyword_analysis import analyze_article_keywords, batch_analyze_articles
except ImportError as e:
    print(f"警告：后端模块导入失败，请确保 backend 目录在路径中。错误: {e}")
    # 为了防止代码直接崩溃，这里可以定义一些占位类，或者直接报错停止
    pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- 配置区域 ---
OUTPUT_FILE = "tophub_articles.jsonl"  # 结果保存文件 (json lines 格式)
MIN_SLEEP = 3  # 最短等待时间
MAX_SLEEP = 8  # 最长等待时间

# [修复] 修复了列表缺少逗号和乱码的问题
category_list = [
    # "微博",
    # "微信",
    "知乎",
    "虎嗅",
    "IT之家",
    "掘金",
    "机器之心",
    "量子位",
    # "Readhub",
    # "百度贴吧",
    "虎扑社区",
    # "第一财经",
    "Product Hunt",
    "开源中国",
    "GitHub",
    "CSDN博客",
    "UI 中国"
]

# 尝试初始化 crawler，如果导入失败则忽略
try:
    crawler = Crawler()
except NameError:
    crawler = None

# --- 技术关键词配置 ---
# [修复] 修复了字典键值的乱码和引号
TECH_KEYWORDS = {
    "开源项目": [
        "开源", "open source", "github", "gitlab", "开源项目", "开源库",
        "新项目", "项目发布", "release", "开源工具"
    ],
    "大模型": [
        "大模型", "LLM", "GPT", "Claude", "Gemini", "ChatGPT", "语言模型",
        "大语言模型", "生成式AI", "Generative AI", "Foundation Model",
        "Transformer", "BERT", "预训练模型"
    ],
    "RAG技术": [
        "RAG", "检索增强", "Retrieval Augmented", "向量数据库", "Vector Database",
        "Embedding", "知识库", "文档检索", "语义搜索", "Semantic Search"
    ],
    "Agent技术": [
        "Agent", "智能体", "AI Agent", "自主代理", "Multi-Agent", "多智能体",
        "ReAct", "Chain of Thought", "CoT", "Tool Use", "Function Calling"
    ],
    "AI框架": [
        "LangChain", "LlamaIndex", "AutoGPT", "BabyAGI", "Semantic Kernel",
        "Haystack", "Transformers", "PyTorch", "TensorFlow", "JAX"
    ],
    "模型训练": [
        "微调", "Fine-tuning", "RLHF", "LoRA", "QLoRA", "PEFT", "量化",
        "Quantization", "蒸馏", "Distillation", "预训练", "Pre-training"
    ],
    "推理优化": [
        "推理加速", "Inference", "vLLM", "TensorRT", "ONNX", "模型压缩",
        "模型部署", "边缘计算", "Edge AI"
    ]
}

def get_random_headers():
    """
    随机生成请求头，伪装成不同浏览器
    """
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        # 如果库加载失败，使用备用 UA 列表
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
        try:
            page.wait_for_selector("div.cc-cd", timeout=10000)
        except:
            print("页面加载超时或结构已变更")
            browser.close()
            return []

        # 获取所有榜单卡片
        nodes = page.query_selector_all("div.cc-cd")
        
        results = []
        
        for node in nodes:
            # 获取榜单标题
            category_el = node.query_selector("div.cc-cd-lb")
            category = category_el.inner_text().strip() if category_el else "Unknown"
            print(f"发现榜单分类: {category}")
            
            # 获取榜单内的链接
            links = node.query_selector_all("a")
            
            for link in links:
                title_el = link.query_selector("span.t")
                if title_el:
                    title = title_el.inner_text().strip()
                    url = link.get_attribute("href")
                    # 对类别进行过滤
                    if category in category_list:
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
        
        print(f"成功发现 {len(all_articles)} 篇文章链接")
        return all_articles
        
    except Exception as e:
        print(f"获取首页失败: {e}")
        return []
    
    
def get_html_stealth(url):
    """
    智能获取网页内容
    1. 优先尝试 curl_cffi (速度快)
    2. 如果遇到 403/验证墙，自动降级到 Playwright (能力强)
    """
    
    # --- 策略 A: 静态请求 (curl_cffi 升级版) ---
    print(f"   [尝试静态抓取] {url} ...")
    try:
        # 升级到 chrome124，模拟更现代的浏览器行为
        response = cffi_requests.get(
            url, 
            impersonate="chrome124", 
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.zhihu.com/" # 伪造来源
            },
            timeout=10,
            allow_redirects=True
        )
        
        # 检查是否是知乎的安全验证页面 (特征: 包含 zh-zse-ck 或 security.zhihu)
        is_blocked = response.status_code == 403 or "security.zhihu.com" in response.url or "zh-zse-ck" in response.text
        
        if response.status_code == 200 and not is_blocked:
            return response.text
        else:
            print(f"   [静态失败] 状态码: {response.status_code}，触发验证墙，准备切换浏览器...")

    except Exception as e:
        print(f"   [静态报错] {e}，准备切换浏览器...")

    # --- 策略 B: 动态浏览器兜底 (Playwright) ---
    # 专门对付知乎、微信等强验证网站
    print(f"   [启动浏览器兜底] 正在启动无头浏览器...")
    try:
        with sync_playwright() as p:
            # 启动浏览器，headless=True 表示不显示界面
            # args 参数用于规避部分自动化检测
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled'] 
            )
            
            # 创建上下文，设置视窗大小，伪装得更像真人
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            
            # 访问页面
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # 针对知乎：如果遇到验证，等待 JS 执行
            if "zhihu.com" in url:
                # 模拟鼠标滚动，触发加载
                page.mouse.wheel(0, 500)
                time.sleep(2) 
                
                # 等待核心内容出现 (QuestionHeader 是知乎问题的标志)
                try:
                    page.wait_for_selector("div.QuestionHeader", timeout=5000)
                except:
                    pass # 如果没等到也不报错，直接拿当前 HTML
            
            content = page.content()
            browser.close()
            
            print(f"   [浏览器成功] 获取到 {len(content)} 字节")
            return content

    except Exception as e:
        print(f"   [浏览器也失败] {e}")
        return None

def gentle_scrape_content(article_info):
    """
    对单篇文章进行温和爬取
    """
    url = article_info['tophub_url']
    # 1. 使用抗拦截方式下载 HTML
    html = get_html_stealth(url)
    
    if not html:
        return {"title": article_info['title'], "status": "failed_download"}
    
    # 提取正文内容
    try:
        extractor = ReadabilityExtractor()
        extract_content = extractor.extract_article(html)
        extract_content.url = url
        # print("markdown:", extract_content.to_markdown()) # 调试用
    except NameError:
         # 如果 ReadabilityExtractor 没有导入成功
        print("Error: ReadabilityExtractor not found")
        return {"title": article_info['title'], "status": "failed", "error": "Missing dependency"}

    try:
        # newspaper3k 配置
        # browser_user_agent 属性非常重要，newspaper 默认 UA 很容易被封
        article = Article(url, language='zh')
        article.download(input_html=html) # 直接传入已下载的HTML
        article.parse()
        
        # 组装数据
        result = {
            "uuid": str(uuid.uuid4()),
            "title": article_info['title'],
            "category": article_info['category'],
            "original_url": article.url, # 跳转后的真实地址
            "publish_date": str(article.publish_date) if article.publish_date else None,
            "content": extract_content.to_markdown(),
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


def detect_tech_content(text: str, title: str = "") -> dict:
    """
    检测文本中是否包含新开源项目、大模型前沿技术
    """
    if not text:
        return {
            "is_tech_related": False,
            "categories": [],
            "keywords": [],
            "confidence": 0.0,
            "summary": "内容为空"
        }

    
    # 合并标题和正文进行检测（标题权重更高）
    full_text = (title + " " + title + " " + text).lower()  # 标题重复2次增加权重
    
    matched_categories = []
    matched_keywords = []
    keyword_count = 0
    
    # 遍历所有技术分类和关键词
    for category, keywords in TECH_KEYWORDS.items():
        category_matched = False
        for keyword in keywords:
            # 不区分大小写匹配
            if keyword.lower() in full_text:
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
                    keyword_count += 1
                category_matched = True
        
        if category_matched:
            matched_categories.append(category)
    
    # 计算置信度
    # 基础分：匹配到的分类数量
    confidence = min(len(matched_categories) * 0.2, 0.6)
    
    # 加分：匹配到的关键词数量
    confidence += min(keyword_count * 0.05, 0.3)
    
    # 额外加分：标题中包含关键词
    title_lower = title.lower()
    title_match_count = sum(1 for kw in matched_keywords if kw.lower() in title_lower)
    confidence += min(title_match_count * 0.05, 0.1)
    
    # 确保置信度在 0-1 之间
    confidence = min(confidence, 1.0)
    
    # 判断是否相关（至少匹配1个分类，且置信度 >= 0.2）
    is_tech_related = len(matched_categories) > 0 and confidence >= 0.2
    
    # 生成摘要
    if is_tech_related:
        summary = f"检测到 {len(matched_categories)} 个技术领域：{', '.join(matched_categories[:3])}"
        if len(matched_categories) > 3:
            summary += f" 等"
    else:
        summary = "未检测到相关技术内容"
    
    return {
        "is_tech_related": is_tech_related,
        "categories": matched_categories,
        "keywords": matched_keywords[:10],  # 最多返回10个关键词
        "confidence": round(confidence, 2),
        "summary": summary
    }


def filter_tech_articles(articles: list) -> list:
    """
    从文章列表中筛选出技术相关的文章
    """
    tech_articles = []
    
    for article in articles:
        title = article.get('title', '')
        content = article.get('content', '')
        
        # 进行技术检测
        detection_result = detect_tech_content(content, title)
        
        # 只保留相关的文章
        if detection_result['is_tech_related']:
            article['tech_detection'] = detection_result
            tech_articles.append(article)
            print(f"发现技术文章: {title}")
            print(f"   分类: {', '.join(detection_result['categories'])}")
            print(f"   置信度: {detection_result['confidence']}")
    
    return tech_articles


def scrape_and_filter_tech_articles(
    save_to_es: bool = True,
    save_to_jsonl: bool = True,
    es_index_name: str = "tophub_articles",
    check_duplicate: bool = True,
    skip_duplicate: bool = True
):
    """
    完整流程：爬取文章并筛选技术相关内容，保存到 Elasticsearch 和 JSONL
    """
    print("=" * 60)
    print("开始爬取并筛选技术文章...")
    print("=" * 60)
    
    # 初始化 ES 客户端（如果需要）
    es_client = None
    repo = None
    if save_to_es:
        try:
            print("\n🔌 正在连接 Elasticsearch...")
            es_client = ElasticsearchClient()
            repo = ArticleRepository(es_client, index_name=es_index_name)
            
            # 确保索引存在
            if not repo.index_exists():
                print(f"📦 创建索引: {es_index_name}")
                repo.create_index()
            else:
                print(f"索引已存在: {es_index_name}")
                
        except Exception as e:
            logger.error(f"连接 Elasticsearch 失败: {e}")
            print(f"⚠️  将跳过 ES 保存，仅保存到 JSONL")
            save_to_es = False
    
    # 1. 获取首页文章列表
    articles = scrape_tophub_dynamic_link()
    if not articles:
        print("未获取到文章列表")
        if es_client:
            es_client.close()
        return []
    
    print(f"\n📊 共获取 {len(articles)} 篇文章，开始爬取内容...\n")
    
    # 2. 爬取每篇文章的详细内容
    detailed_articles = []
    duplicate_count = 0
    
    for i, article_info in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] 正在爬取: {article_info['title']}")
        
        article_content = gentle_scrape_content(article_info)
        
        if article_content.get('status') != 'failed':
            # 检查重复
            is_duplicate = False
            if save_to_es and repo and check_duplicate:
                dup_result = repo.check_duplicate(
                    article_content,
                    check_url=True,
                    check_title=True,
                    check_similarity=False  # 可选：启用相似度检测
                )
                
                if dup_result['is_duplicate']:
                    duplicate_count += 1
                    dup_type = dup_result['duplicate_type']
                    logger.info(f"⚠️  发现重复文档 ({dup_type}): {article_content['title']}")
                    
                    if skip_duplicate:
                        print(f"   ⏭️  跳过重复文档 (类型: {dup_type})")
                        is_duplicate = True
                    else:
                        print(f"   🔄 覆盖重复文档 (类型: {dup_type})")
            
            if not is_duplicate:
                detailed_articles.append(article_content)
                
                # 实时保存到 ES（逐条插入）
                if save_to_es and repo:
                    try:
                        doc_id = article_content.get('original_url') or article_content.get('tophub_url')
                        repo.create_document(article_content, doc_id=doc_id)
                        logger.info(f"已保存到 ES: {article_content['title']}")
                    except Exception as e:
                        logger.error(f"保存到 ES 失败: {e}")
        
        # 礼貌等待
        time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))
    
    print(f"\n成功爬取 {len(detailed_articles)} 篇文章")
    if check_duplicate:
        print(f"⏭️  跳过 {duplicate_count} 篇重复文章")
    
    # 3. 筛选技术相关文章
    print("\n" + "=" * 60)
    print("开始筛选技术相关文章...")
    print("=" * 60 + "\n")
    
    tech_articles = filter_tech_articles(detailed_articles)
    
    print("\n" + "=" * 60)
    print(f"筛选完成！共发现 {len(tech_articles)} 篇技术相关文章")
    print("=" * 60)
    
    # 4. 保存技术文章到单独的文件和索引
    if save_to_jsonl and tech_articles:
        tech_output_file = "tech_articles.jsonl"
        with open(tech_output_file, 'w', encoding='utf-8') as f:
            for article in tech_articles:
                f.write(json.dumps(article, ensure_ascii=False) + "\n")
        print(f"\n💾 技术文章已保存到 {tech_output_file}")
    
    # 5. 保存所有文章到 JSONL（如果需要）
    if save_to_jsonl and detailed_articles:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for article in detailed_articles:
                f.write(json.dumps(article, ensure_ascii=False) + "\n")
        print(f"💾 所有文章已保存到 {OUTPUT_FILE}")
    
    # 6. 显示统计信息
    if save_to_es and repo:
        try:
            total_count = repo.count()
            tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
            print(f"\n📊 Elasticsearch 统计:")
            print(f"   索引: {es_index_name}")
            print(f"   总文档数: {total_count}")
            print(f"   技术文章数: {tech_count}")
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
    
    # 7. 关闭 ES 连接
    if es_client:
        es_client.close()
        print("\nElasticsearch 连接已关闭")
    
    return tech_articles


def scrape_all_articles_to_es(
    es_index_name: str = "tophub_articles",
    batch_size: int = 10,
    check_duplicate: bool = True,
    skip_duplicate: bool = True,
    enable_analysis: bool = True
):
    """
    爬取所有文章并直接保存到 Elasticsearch（批量模式）
    """
    print("=" * 60)
    print("开始爬取文章并保存到 Elasticsearch")
    print("=" * 60)
    
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
            print(f"索引已存在: {es_index_name}")
            
    except Exception as e:
        logger.error(f"连接 Elasticsearch 失败: {e}")
        return {"success": 0, "failed": 0, "duplicate": 0, "analyzed": 0, "error": str(e)}
    
    # 2. 获取文章列表
    articles = scrape_tophub_dynamic_link()
    if not articles:
        print("未获取到文章列表")
        es_client.close()
        return {"success": 0, "failed": 0, "duplicate": 0, "analyzed": 0, "error": "未获取到文章列表"}
    
    print(f"\n共获取 {len(articles)} 篇文章，开始爬取内容...\n")
    if check_duplicate:
        print(f"🔍 重复检测: 已启用 (跳过模式: {'是' if skip_duplicate else '否'})")
    if enable_analysis:
        print(f"🤖 内容分析: 已启用")
    print()
    
    # 3. 爬取并批量保存
    batch = []
    success_count = 0
    failed_count = 0
    duplicate_count = 0
    analyzed_count = 0
    
    # 用于批量分析的文章列表
    articles_to_analyze = []
    
    for i, article_info in enumerate(articles[:5], 1):
        print(f"[{i}/{len(articles)}] 正在爬取: {article_info['title']}")
        
        article_content = gentle_scrape_content(article_info)
        
        if article_content.get('status') != 'failed':
            # 检查重复
            is_duplicate = False
            if check_duplicate:
                dup_result = repo.check_duplicate(
                    article_content,
                    check_url=True,
                    check_title=True,
                    check_similarity=False  # 可选：启用相似度检测
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
                # 添加到待分析列表
                if enable_analysis:
                    articles_to_analyze.append(article_content)
                else:
                    batch.append(article_content)
                
                # 达到批量大小时，进行分析和插入
                if len(articles_to_analyze) >= batch_size or len(batch) >= batch_size:
                    if enable_analysis and articles_to_analyze:
                        print(f"\n   🤖 正在批量分析 {len(articles_to_analyze)} 篇文章...")
                        
                        # 使用 asyncio 运行批量分析
                        try:
                            # 修复：检查是否已有运行中的 loop
                            try:
                                loop = asyncio.get_event_loop()
                            except RuntimeError:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                            analyzed_articles = loop.run_until_complete(
                                batch_analyze_articles(articles_to_analyze, max_concurrent=3)
                            )
                            
                            # 统计成功分析的数量
                            for article in analyzed_articles:
                                if article.get('content_analysis', {}).get('analysis_success'):
                                    analyzed_count += 1
                            
                            batch.extend(analyzed_articles)
                            articles_to_analyze = []
                            
                            print(f"   分析完成，成功 {analyzed_count} 篇")
                            
                        except Exception as e:
                            logger.error(f"   批量分析失败: {e}")
                            # 即使分析失败，也保存原始数据
                            batch.extend(articles_to_analyze)
                            articles_to_analyze = []
                    
                    # 批量插入
                    if batch:
                        try:
                            result = repo.bulk_create_documents(batch)
                            success_count += result['success']
                            failed_count += result['failed']
                            print(f"   💾 批量保存: 成功 {result['success']} 篇")
                            batch = []
                        except Exception as e:
                            logger.error(f"批量保存失败: {e}")
                            failed_count += len(batch)
                            batch = []
        else:
            failed_count += 1
        
        # 礼貌等待
        time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))
    
    # 4. 处理剩余的文章
    if articles_to_analyze:
        print(f"\n🤖 正在分析剩余 {len(articles_to_analyze)} 篇文章...")
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            analyzed_articles = loop.run_until_complete(
                batch_analyze_articles(articles_to_analyze, max_concurrent=3)
            )
            
            for article in analyzed_articles:
                if article.get('content_analysis', {}).get('analysis_success'):
                    analyzed_count += 1
            
            batch.extend(analyzed_articles)
            print(f"分析完成")
            
        except Exception as e:
            logger.error(f"批量分析失败: {e}")
            batch.extend(articles_to_analyze)
    
    # 保存剩余的文章
    if batch:
        try:
            result = repo.bulk_create_documents(batch)
            success_count += result['success']
            failed_count += result['failed']
            print(f"   💾 批量保存: 成功 {result['success']} 篇")
        except Exception as e:
            logger.error(f"批量保存失败: {e}")
            failed_count += len(batch)
    
    # 5. 显示统计信息
    print("\n" + "=" * 60)
    print("爬取完成")
    print("=" * 60)
    print(f"成功: {success_count} 篇")
    print(f"失败: {failed_count} 篇")
    if check_duplicate:
        print(f"⏭️  重复: {duplicate_count} 篇")
    if enable_analysis:
        print(f"🤖 已分析: {analyzed_count} 篇")
    
    try:
        total_count = repo.count()
        tech_count = repo.count(query={"term": {"tech_detection.is_tech_related": True}})
        analyzed_in_es = repo.count(query={"term": {"content_analysis.analysis_success": True}})
        
        print(f"\n📊 Elasticsearch 统计:")
        print(f"   索引: {es_index_name}")
        print(f"   总文档数: {total_count}")
        print(f"   技术文章数: {tech_count}")
        if enable_analysis:
            print(f"   已分析文章: {analyzed_in_es}")
            
            # 显示热门关键词
            print(f"\n🔑 热门关键词 (Top 10):")
            top_keywords = repo.get_keyword_statistics(top_n=10)
            for i, item in enumerate(top_keywords[:10], 1):
                print(f"   {i}. {item['keyword']}: {item['count']} 次")
            
            # 显示热门主题
            print(f"\n📚 热门主题 (Top 5):")
            top_topics = repo.get_topic_statistics(top_n=5)
            for i, item in enumerate(top_topics[:5], 1):
                print(f"   {i}. {item['topic']}: {item['count']} 次")
            
            # 显示分类统计
            print(f"\n📂 分类统计:")
            categories = repo.get_category_statistics()
            for category, count in list(categories.items())[:5]:
                print(f"   {category}: {count} 篇")
            
            # 显示情感统计
            print(f"\n😊 情感统计:")
            sentiments = repo.get_sentiment_statistics()
            for sentiment, count in sentiments.items():
                print(f"   {sentiment}: {count} 篇")
                
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
    
    # 6. 关闭连接
    es_client.close()
    print("\nElasticsearch 连接已关闭")
    
    return {
        "success": success_count,
        "failed": failed_count,
        "duplicate": duplicate_count,
        "analyzed": analyzed_count,
        "total": success_count + failed_count + duplicate_count
    }

if __name__ == "__main__":
    # 在这里运行，例如：
    # scrape_and_filter_tech_articles(save_to_es=False) # 仅测试爬取
    pass