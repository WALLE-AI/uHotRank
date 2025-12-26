"""Statistics-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import Dict, List


class OverallStatistics(BaseModel):
    """总体统计模型"""
    total_articles: int = Field(..., description="文章总数")
    today_new: int = Field(..., description="今日新增")
    tech_articles: int = Field(..., description="技术文章数")
    analyzed_articles: int = Field(..., description="已分析文章数")
    categories_count: int = Field(..., description="分类数量")
    avg_sentiment_score: float = Field(..., description="平均情感分数")


class KeywordStat(BaseModel):
    """关键词统计项模型"""
    keyword: str = Field(..., description="关键词")
    count: int = Field(..., description="出现次数")


class KeywordStats(BaseModel):
    """关键词统计模型"""
    keywords: List[KeywordStat] = Field(..., description="关键词列表")


class CategoryStats(BaseModel):
    """分类统计模型"""
    categories: Dict[str, int] = Field(..., description="分类统计字典")


class SentimentStats(BaseModel):
    """情感统计模型"""
    positive: int = Field(..., description="正面文章数")
    neutral: int = Field(..., description="中性文章数")
    negative: int = Field(..., description="负面文章数")


class SourceStats(BaseModel):
    """来源统计模型"""
    sources: Dict[str, int] = Field(..., description="来源统计字典")


class TrendDataPoint(BaseModel):
    """趋势数据点模型"""
    date: str = Field(..., description="日期")
    count: int = Field(..., description="数量")


class TrendStats(BaseModel):
    """趋势统计模型"""
    trends: List[TrendDataPoint] = Field(..., description="趋势数据列表")
