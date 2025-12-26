"""Statistics API router."""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from backend.schemas.statistics import (
    OverallStatistics,
    KeywordStats,
    CategoryStats,
    SentimentStats,
    SourceStats,
    TrendStats,
)
from backend.service.stats_service import StatsService
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_stats_service() -> StatsService:
    """依赖注入：获取统计服务实例"""
    es_client = ElasticsearchClient()
    repository = ArticleRepository(es_client, index_name="tophub_articles")
    return StatsService(repository)


@router.get("", response_model=OverallStatistics)
async def get_statistics(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取总体统计信息

    - **date_from**: 开始日期，格式 YYYY-MM-DD（可选）
    - **date_to**: 结束日期，格式 YYYY-MM-DD（可选）

    返回：
    - 文章总数
    - 今日新增
    - 技术文章数
    - 已分析文章数
    - 分类数量
    - 平均情感分数
    """
    try:
        return service.get_overall_statistics(date_from=date_from, date_to=date_to)
    except Exception as e:
        logger.error("获取总体统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取总体统计失败")


@router.get("/keywords", response_model=KeywordStats)
async def get_keyword_stats(
    top_n: int = Query(50, ge=1, le=200, description="返回前 N 个关键词"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取关键词统计

    - **top_n**: 返回前 N 个关键词，默认50，最大200

    返回关键词及其出现次数，按出现次数降序排列
    """
    try:
        return service.get_keyword_stats(top_n=top_n)
    except Exception as e:
        logger.error("获取关键词统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取关键词统计失败")


@router.get("/categories", response_model=CategoryStats)
async def get_category_stats(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取分类统计

    - **date_from**: 开始日期，格式 YYYY-MM-DD（可选）
    - **date_to**: 结束日期，格式 YYYY-MM-DD（可选）

    返回各分类的文章数量分布
    """
    try:
        return service.get_category_stats(date_from=date_from, date_to=date_to)
    except Exception as e:
        logger.error("获取分类统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取分类统计失败")


@router.get("/sentiments", response_model=SentimentStats)
async def get_sentiment_stats(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取情感统计

    - **date_from**: 开始日期，格式 YYYY-MM-DD（可选）
    - **date_to**: 结束日期，格式 YYYY-MM-DD（可选）

    返回正面、中性、负面文章的数量分布
    """
    try:
        return service.get_sentiment_stats(date_from=date_from, date_to=date_to)
    except Exception as e:
        logger.error("获取情感统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取情感统计失败")


@router.get("/sources", response_model=SourceStats)
async def get_source_stats(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取来源统计

    - **date_from**: 开始日期，格式 YYYY-MM-DD（可选）
    - **date_to**: 结束日期，格式 YYYY-MM-DD（可选）

    返回各来源网站的文章数量分布
    """
    try:
        return service.get_source_stats(date_from=date_from, date_to=date_to)
    except Exception as e:
        logger.error("获取来源统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取来源统计失败")


@router.get("/trends", response_model=TrendStats)
async def get_trend_stats(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    service: StatsService = Depends(get_stats_service),
):
    """
    获取趋势统计

    - **date_from**: 开始日期，格式 YYYY-MM-DD（可选）
    - **date_to**: 结束日期，格式 YYYY-MM-DD（可选）

    返回按日期聚合的文章数量时间序列数据
    """
    try:
        return service.get_trend_stats(date_from=date_from, date_to=date_to)
    except Exception as e:
        logger.error("获取趋势统计失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取趋势统计失败")
