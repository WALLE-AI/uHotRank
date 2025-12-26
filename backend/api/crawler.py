"""Crawler API router."""

import logging
from fastapi import APIRouter, Query, HTTPException, Depends

from backend.schemas.crawler import (
    StartCrawlerRequest,
    StartCrawlerResponse,
    CrawlerStatus,
    CrawlerHistoryResponse,
)
from backend.service.crawler_service import CrawlerService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_crawler_service() -> CrawlerService:
    """依赖注入：获取爬虫服务实例（单例）"""
    return CrawlerService()


@router.post("/start", response_model=StartCrawlerResponse)
async def start_crawler(
    request: StartCrawlerRequest,
    service: CrawlerService = Depends(get_crawler_service),
):
    """
    启动爬虫任务

    - **mode**: 爬虫模式
      - `all`: 爬取所有文章
      - `tech_only`: 仅爬取技术相关文章
      - `with_analysis`: 爬取并进行内容分析
    - **batch_size**: 批量大小，默认10
    """
    try:
        return await service.start_crawler(request)
    except ValueError as e:
        logger.warning("启动爬虫失败: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("启动爬虫失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="启动爬虫失败")


@router.get("/status", response_model=CrawlerStatus)
async def get_crawler_status(
    service: CrawlerService = Depends(get_crawler_service),
):
    """
    获取爬虫状态

    返回当前爬虫任务的运行状态、进度等信息
    """
    try:
        return await service.get_status()
    except Exception as e:
        logger.error("获取爬虫状态失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取爬虫状态失败")


@router.post("/stop")
async def stop_crawler(
    service: CrawlerService = Depends(get_crawler_service),
):
    """
    停止爬虫任务

    停止当前正在运行的爬虫任务
    """
    try:
        await service.stop_crawler()
        return {"message": "Crawler task stopped successfully"}
    except ValueError as e:
        logger.warning("停止爬虫失败: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("停止爬虫失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="停止爬虫失败")


@router.get("/history", response_model=CrawlerHistoryResponse)
async def get_crawler_history(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: CrawlerService = Depends(get_crawler_service),
):
    """
    获取爬虫历史记录

    - **page**: 页码，从1开始
    - **size**: 每页数量，最大100
    """
    try:
        return await service.get_history(page=page, size=size)
    except Exception as e:
        logger.error("获取爬虫历史失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取爬虫历史失败")
