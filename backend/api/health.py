"""Health check API router."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db.elasticsearch_client import ElasticsearchClient

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str
    elasticsearch: str
    message: str


class VersionResponse(BaseModel):
    """版本信息响应模型"""

    version: str
    api_name: str
    description: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    检查服务状态和依赖项（Elasticsearch）的连接状态

    返回：
    - status: 服务状态 (healthy/unhealthy)
    - elasticsearch: Elasticsearch 连接状态 (connected/disconnected)
    - message: 状态描述信息
    """
    try:
        # 检查 Elasticsearch 连接
        es_client = ElasticsearchClient()
        es_status = "connected" if es_client.ping() else "disconnected"

        # 判断整体健康状态
        if es_status == "connected":
            status = "healthy"
            message = "Service is running normally"
        else:
            status = "unhealthy"
            message = "Elasticsearch connection failed"

        return HealthResponse(
            status=status, elasticsearch=es_status, message=message
        )

    except Exception as e:
        logger.error("健康检查失败: %s", e, exc_info=True)
        return HealthResponse(
            status="unhealthy",
            elasticsearch="error",
            message=f"Health check failed: {str(e)}",
        )


@router.get("/version", response_model=VersionResponse)
async def get_version():
    """
    获取 API 版本信息

    返回：
    - version: API 版本号
    - api_name: API 名称
    - description: API 描述
    """
    return VersionResponse(
        version="1.0.0",
        api_name="TopHub Article API",
        description="API for TopHub article management and analysis",
    )
