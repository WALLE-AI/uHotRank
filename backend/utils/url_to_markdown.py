import re
from urllib.parse import urljoin

from markdownify import markdownify as md
from readabilipy import simple_json_from_html_string

import logging
import os

import requests

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()


class Article:
    url: str

    def __init__(self, title: str, html_content: str):
        self.title = title
        self.html_content = html_content

    def to_markdown(self, including_title: bool = True) -> str:
        markdown = ""
        if including_title:
            markdown += f"# {self.title}\n\n"
        markdown += md(self.html_content)
        # 对 markdown 内容进行过滤清理
        markdown = self._filter_markdown(markdown)
        return markdown
    
    def _filter_markdown(self, markdown: str) -> str:
        """
        激进过滤网页元素，只保留正文内容
        - 移除所有链接（保留链接文本）
        - 移除图片
        - 移除导航、广告、版权等非正文元素
        - 移除短行（通常是导航或标签）
        - 只保留有实际内容的段落
        """
        if not markdown:
            return ""
        
        # 1. 移除图片 ![alt](url)
        markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown)
        
        # 2. 将链接转换为纯文本（保留链接文字，去掉URL）
        # [text](url) -> text
        markdown = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown)
        
        # 3. 移除空链接
        markdown = re.sub(r'\[\]\([^\)]*\)', '', markdown)
        
        # 4. 移除常见的网页元素关键词行（更全面的列表）
        noise_patterns = [
            # 导航和菜单
            r'.*?(首页|导航|菜单|Menu|Navigation|Home|返回).*?\n',
            # 广告和推广
            r'.*?(广告|赞助|推广|Advertisement|Sponsored|AD).*?\n',
            # 社交分享
            r'.*?(分享|转发|点赞|收藏|Share|Like|Favorite|Tweet|Facebook|Twitter|微信|微博|QQ空间).*?\n',
            # 订阅和关注
            r'.*?(关注|订阅|Subscribe|Follow|Newsletter).*?\n',
            # 相关推荐
            r'.*?(相关文章|相关推荐|推荐阅读|猜你喜欢|热门文章|Related|Recommended|Popular|Hot).*?\n',
            # 查看更多
            r'.*?(查看更多|阅读更多|阅读原文|Read More|View More|More).*?\n',
            # 版权和声明
            r'.*?(版权|Copyright|All Rights Reserved|免责声明|Disclaimer|隐私政策|Privacy Policy).*?\n',
            # 评论和互动
            r'.*?(评论|留言|Comment|Reply|回复).*?\n',
            # 标签和分类
            r'.*?(标签|Tags|分类|Category|Categories).*?\n',
            # 作者信息（通常很短）
            r'.*?(作者|编辑|来源|Author|Editor|Source|By)[:：]\s*\S{1,20}\s*\n',
            # 日期时间（单独一行的）
            r'^\s*\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?\s*\d{0,2}[:：]?\d{0,2}[:：]?\d{0,2}\s*$',
            # 页码和导航
            r'.*?(上一页|下一页|Previous|Next|Page \d+|\d+/\d+).*?\n',
        ]
        
        for pattern in noise_patterns:
            markdown = re.sub(pattern, '', markdown, flags=re.IGNORECASE | re.MULTILINE)
        
        # 5. 按行处理，过滤掉噪音行
        lines = markdown.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行（稍后统一处理）
            if not line:
                filtered_lines.append('')
                continue
            
            # 跳过过短的行（可能是标签、按钮等，但保留标题）
            if len(line) < 10 and not line.startswith('#'):
                continue
            
            # 跳过只包含特殊字符和空格的行
            if re.match(r'^[\s\-_=\*\|]+$', line):
                continue
            
            # 跳过包含大量特殊符号的行（可能是分隔符或装饰）
            special_char_ratio = len(re.findall(r'[^\w\s\u4e00-\u9fff]', line)) / max(len(line), 1)
            if special_char_ratio > 0.5:
                continue
            
            # 跳过纯数字或纯符号的行
            if re.match(r'^[\d\s\.\-\+\*\/]+$', line):
                continue
            
            filtered_lines.append(line)
        
        # 6. 重新组合，移除多余空行
        markdown = '\n'.join(filtered_lines)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # 7. 移除开头和结尾的空白
        markdown = markdown.strip()
        
        # 8. 如果内容太短（可能过滤过度），返回提示
        if len(markdown) < 50:
            return "# 内容提取失败\n\n无法提取有效正文内容，可能页面结构不支持或内容过少。"
        
        return markdown

    def to_message(self) -> list[dict]:
        image_pattern = r"!\[.*?\]\((.*?)\)"

        content: list[dict[str, str]] = []
        parts = re.split(image_pattern, self.to_markdown())

        for i, part in enumerate(parts):
            if i % 2 == 1:
                image_url = urljoin(self.url, part.strip())
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            else:
                content.append({"type": "text", "text": part.strip()})

        return content
    

class JinaClient:
    def crawl(self, url: str, return_format: str = "html") -> str:
        headers = {
            "Content-Type": "application/json",
            "X-Return-Format": return_format,
        }
        if os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {os.getenv('JINA_API_KEY')}"
        else:
            logger.warning(
                "Jina API key is not set. Provide your own key to access a higher rate limit. See https://jina.ai/reader for more information."
            )
        data = {"url": url}
        response = requests.post("https://r.jina.ai/", headers=headers, json=data)
        return response.text

class ReadabilityExtractor:
    def extract_article(self, html: str) -> Article:
        article = simple_json_from_html_string(html, use_readability=True)
        return Article(
            title=article.get("title"),
            html_content=article.get("content"),
        )


class Crawler:
    def crawl(self, url: str) -> Article:
        # To help LLMs better understand content, we extract clean
        # articles from HTML, convert them to markdown, and split
        # them into text and image blocks for one single and unified
        # LLM message.
        #
        # Jina is not the best crawler on readability, however it's
        # much easier and free to use.
        #
        # Instead of using Jina's own markdown converter, we'll use
        # our own solution to get better readability results.
        jina_client = JinaClient()
        html = jina_client.crawl(url, return_format="html")
        extractor = ReadabilityExtractor()
        article = extractor.extract_article(html)
        article.url = url
        return article
    
    
crawler = Crawler()
    
    
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL
        # response = requests.get(url)
        # response.raise_for_status()  # Raise an exception for bad status codes

        # # Convert the HTML content to Markdown  是否可以采用jina来完成
        # markdown_content = markdownify(response.text).strip()
        result = crawler.crawl(url)
        markdown_content = result.to_markdown()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except requests.RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    
    

def test_crawler_markdown_output():
    """Test that crawler output can be converted to markdown."""
    crawler = Crawler()
    test_url = "https://finance.sina.com.cn/stock/relnews/us/2024-08-15/doc-incitsya6536375.shtml"
    # test_weixinarticl = "https://pypi.org/project/readability/"
    result = crawler.crawl(test_url)
    markdown = result.to_markdown()
    print("markdown:", markdown)
    
    
    
    
    
if __name__ == "__main__":
    test_crawler_markdown_output()