"""
文章内容关键词和主题分析
使用 LLM 提取文章的核心关键词和主题
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import os


from backend.models import chat_completion, LLMProvider

logger = logging.getLogger(__name__)


async def analyze_article_keywords(
    title: str,
    content: str,
    provider: Optional[LLMProvider] = None,
    max_keywords: int = 10,
    max_topics: int = 5
) -> Dict[str, Any]:
    """
    分析文章的关键词和主题
    
    Args:
        title: 文章标题
        content: 文章内容
        provider: LLM 提供商（可选）
        max_keywords: 最大关键词数量
        max_topics: 最大主题数量
    
    Returns:
        dict: {
            "keywords": List[str],           # 关键词列表
            "topics": List[str],             # 主题列表
            "summary": str,                  # 文章摘要
            "sentiment": str,                # 情感倾向: positive/neutral/negative
            "category": str,                 # 文章分类
            "entities": List[Dict],          # 实体识别
            "analysis_success": bool         # 分析是否成功
        }
    """
    # 限制内容长度（避免超过 token 限制）
    max_content_length = 3000
    truncated_content = content[:max_content_length] if len(content) > max_content_length else content
    
    # 构建提示词
    prompt = f"""请分析以下文章，提取关键信息。

标题：{title}

内容：
{truncated_content}

请以 JSON 格式返回分析结果，包含以下字段：
1. keywords: 提取最多 {max_keywords} 个核心关键词（数组）
2. topics: 提取最多 {max_topics} 个主要主题（数组）
3. summary: 用 1-2 句话总结文章核心内容
4. sentiment: 情感倾向（positive/neutral/negative）
5. category: 文章所属类别（如：科技、财经、社会、娱乐等）
6. entities: 识别的重要实体，格式为 [{{"name": "实体名", "type": "类型"}}]，类型可以是：人物、组织、地点、产品、技术等

只返回 JSON，不要其他说明文字。"""
    
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的文本分析助手，擅长提取文章的关键词、主题和实体。请严格按照 JSON 格式返回结果。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        # 调用 LLM
        response = await chat_completion(
            messages=messages,
            provider=provider,
            model=os.getenv("DEFAULT_LLM_MODEL"),
            temperature=0.3,  # 较低温度，更确定性
            max_tokens=1000
        )
        
        # 解析 JSON 响应
        # 尝试提取 JSON（可能包含在 markdown 代码块中）
        response = response.strip()
        
        # 移除可能的 markdown 代码块标记
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # 解析 JSON
        result = json.loads(response)
        
        # 验证和标准化结果
        analysis_result = {
            "keywords": result.get("keywords", [])[:max_keywords],
            "topics": result.get("topics", [])[:max_topics],
            "summary": result.get("summary", ""),
            "sentiment": result.get("sentiment", "neutral"),
            "category": result.get("category", "其他"),
            "entities": result.get("entities", []),
            "analysis_success": True
        }
        
        logger.info(f"文章分析成功: {title[:50]}...")
        return analysis_result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}")
        logger.error(f"响应内容: {response[:200]}...")
        return _get_default_analysis_result(False)
    
    except Exception as e:
        logger.error(f"文章分析失败: {e}")
        return _get_default_analysis_result(False)


def _get_default_analysis_result(success: bool = False) -> Dict[str, Any]:
    """获取默认的分析结果"""
    return {
        "keywords": [],
        "topics": [],
        "summary": "",
        "sentiment": "neutral",
        "category": "未分类",
        "entities": [],
        "analysis_success": success
    }


async def batch_analyze_articles(
    articles: List[Dict[str, Any]],
    provider: Optional[LLMProvider] = None,
    max_concurrent: int = 3
) -> List[Dict[str, Any]]:
    """
    批量分析文章
    
    Args:
        articles: 文章列表，每篇文章需包含 title 和 content
        provider: LLM 提供商
        max_concurrent: 最大并发数
    
    Returns:
        List[Dict]: 添加了分析结果的文章列表
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def analyze_with_semaphore(article: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            title = article.get("title", "")
            content = article.get("content", "")
            
            if not title or not content:
                article["content_analysis"] = _get_default_analysis_result(False)
                return article
            
            # 分析文章
            analysis = await analyze_article_keywords(
                title=title,
                content=content,
                provider=provider
            )
            
            # 添加分析结果
            article["content_analysis"] = analysis
            
            return article
    
    # 并发分析
    tasks = [analyze_with_semaphore(article) for article in articles]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常
    analyzed_articles = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"文章 {i} 分析失败: {result}")
            articles[i]["content_analysis"] = _get_default_analysis_result(False)
            analyzed_articles.append(articles[i])
        else:
            analyzed_articles.append(result)
    
    return analyzed_articles


def extract_keywords_from_analysis(article: Dict[str, Any]) -> List[str]:
    """
    从文章中提取关键词（用于搜索和统计）
    
    Args:
        article: 包含 content_analysis 的文章
    
    Returns:
        List[str]: 关键词列表
    """
    analysis = article.get("content_analysis", {})
    keywords = analysis.get("keywords", [])
    
    # 也可以从实体中提取
    entities = analysis.get("entities", [])
    entity_names = [e.get("name", "") for e in entities if e.get("name")]
    
    # 合并并去重
    all_keywords = list(set(keywords + entity_names))
    
    return all_keywords


def get_article_statistics(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    获取文章统计信息
    
    Args:
        articles: 文章列表
    
    Returns:
        dict: 统计信息
    """
    from collections import Counter
    
    total = len(articles)
    analyzed = sum(1 for a in articles if a.get("content_analysis", {}).get("analysis_success", False))
    
    # 统计关键词
    all_keywords = []
    for article in articles:
        keywords = article.get("content_analysis", {}).get("keywords", [])
        all_keywords.extend(keywords)
    
    keyword_counter = Counter(all_keywords)
    top_keywords = keyword_counter.most_common(20)
    
    # 统计主题
    all_topics = []
    for article in articles:
        topics = article.get("content_analysis", {}).get("topics", [])
        all_topics.extend(topics)
    
    topic_counter = Counter(all_topics)
    top_topics = topic_counter.most_common(10)
    
    # 统计分类
    all_categories = []
    for article in articles:
        category = article.get("content_analysis", {}).get("category", "")
        if category:
            all_categories.append(category)
    
    category_counter = Counter(all_categories)
    
    # 统计情感
    all_sentiments = []
    for article in articles:
        sentiment = article.get("content_analysis", {}).get("sentiment", "")
        if sentiment:
            all_sentiments.append(sentiment)
    
    sentiment_counter = Counter(all_sentiments)
    
    # 统计实体
    all_entities = []
    for article in articles:
        entities = article.get("content_analysis", {}).get("entities", [])
        for entity in entities:
            name = entity.get("name", "")
            entity_type = entity.get("type", "")
            if name:
                all_entities.append(f"{name} ({entity_type})")
    
    entity_counter = Counter(all_entities)
    top_entities = entity_counter.most_common(20)
    
    return {
        "total_articles": total,
        "analyzed_articles": analyzed,
        "analysis_rate": f"{analyzed/total*100:.1f}%" if total > 0 else "0%",
        "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
        "top_topics": [{"topic": t, "count": c} for t, c in top_topics],
        "categories": dict(category_counter),
        "sentiments": dict(sentiment_counter),
        "top_entities": [{"entity": e, "count": c} for e, c in top_entities]
    }


# 同步包装函数（用于非异步环境）
def analyze_article_keywords_sync(
    title: str,
    content: str,
    provider: Optional[LLMProvider] = None
) -> Dict[str, Any]:
    """
    同步版本的文章分析
    
    Args:
        title: 文章标题
        content: 文章内容
        provider: LLM 提供商
    
    Returns:
        dict: 分析结果
    """
    return asyncio.run(analyze_article_keywords(title, content, provider))
