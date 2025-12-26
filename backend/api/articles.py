"""Articles API router."""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import Response

from backend.schemas.article import (
    ArticleListResponse,
    ArticleDetail,
    SearchRequest,
    SearchResponse,
)
from backend.service.article_service import ArticleService
from backend.db.elasticsearch_client import ElasticsearchClient, ArticleRepository

logger = logging.getLogger(__name__)

router = APIRouter()


def get_article_service() -> ArticleService:
    """依赖注入：获取文章服务实例"""
    es_client = ElasticsearchClient()
    repository = ArticleRepository(es_client, index_name="tophub_articles")
    return ArticleService(repository)


@router.get("", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: Optional[str] = Query(
        None,
        description="排序字段，支持 publish_date, scraped_at, -publish_date, -scraped_at",
    ),
    service: ArticleService = Depends(get_article_service),
):
    """
    获取文章列表（分页）

    - **page**: 页码，从1开始
    - **size**: 每页数量，最大100
    - **sort_by**: 排序字段，支持 publish_date, scraped_at，前缀 - 表示降序
    """
    try:
        return service.get_articles(page=page, size=size, sort_by=sort_by)
    except Exception as e:
        logger.error("获取文章列表失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取文章列表失败")


@router.get("/{article_id}", response_model=ArticleDetail)
async def get_article_by_id(
    article_id: str,
    service: ArticleService = Depends(get_article_service),
):
    """
    获取文章详情

    - **article_id**: 文章 ID
    """
    try:
        article = service.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail=f"文章不存在: {article_id}")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取文章详情失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="获取文章详情失败")


@router.post("/search", response_model=SearchResponse)
async def search_articles(
    request: SearchRequest,
    service: ArticleService = Depends(get_article_service),
):
    """
    搜索文章

    - **query**: 搜索关键词（可选）
    - **filters**: 过滤条件（可选）
      - **categories**: 分类列表
      - **sentiments**: 情感列表
      - **date_from**: 开始日期
      - **date_to**: 结束日期
      - **tech_only**: 仅技术文章
    - **page**: 页码，从1开始
    - **size**: 每页数量，最大100
    - **sort_by**: 排序字段
    """
    try:
        return service.search_articles(request)
    except Exception as e:
        logger.error("搜索文章失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="搜索文章失败")


@router.get("/export")
async def export_articles(
    format: str = Query(..., regex="^(json|csv|excel)$", description="导出格式"),
    fields: str = Query(..., description="导出字段，逗号分隔"),
    categories: Optional[str] = Query(None, description="分类过滤，逗号分隔"),
    sentiments: Optional[str] = Query(None, description="情感过滤，逗号分隔"),
    date_from: Optional[str] = Query(None, description="开始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    tech_only: Optional[bool] = Query(None, description="仅技术文章"),
    service: ArticleService = Depends(get_article_service),
):
    """
    导出文章数据

    - **format**: 导出格式 (json, csv, excel)
    - **fields**: 要导出的字段，逗号分隔
    - **categories**: 分类过滤，逗号分隔（可选）
    - **sentiments**: 情感过滤，逗号分隔（可选）
    - **date_from**: 开始日期（可选）
    - **date_to**: 结束日期（可选）
    - **tech_only**: 仅技术文章（可选）
    """
    try:
        # 解析字段列表
        fields_list = [f.strip() for f in fields.split(",")]

        # 构建过滤条件
        filters = {}
        if categories:
            filters["categories"] = [c.strip() for c in categories.split(",")]
        if sentiments:
            filters["sentiments"] = [s.strip() for s in sentiments.split(",")]
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if tech_only is not None:
            filters["tech_only"] = tech_only

        # 导出数据
        content = service.export_articles(
            format=format, fields=fields_list, filters=filters if filters else None
        )

        # 设置响应头
        content_types = {
            "json": "application/json",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        filenames = {
            "json": "articles.json",
            "csv": "articles.csv",
            "excel": "articles.xlsx",
        }

        return Response(
            content=content,
            media_type=content_types[format],
            headers={
                "Content-Disposition": f'attachment; filename="{filenames[format]}"'
            },
        )

    except ValueError as e:
        logger.error("导出参数错误: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("导出文章失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="导出文章失败")
