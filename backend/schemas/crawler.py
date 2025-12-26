"""Crawler-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class StartCrawlerRequest(BaseModel):
    """启动爬虫请求模型"""
    mode: Literal["all", "tech_only", "with_analysis"] = Field(
        "all", 
        description="爬虫模式：all（全部）、tech_only（仅技术）、with_analysis（带分析）"
    )
    batch_size: int = Field(10, ge=1, le=100, description="批次大小")


class StartCrawlerResponse(BaseModel):
    """启动爬虫响应模型"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field("Crawler task started successfully", description="响应消息")


class CrawlerStatus(BaseModel):
    """爬虫状态模型"""
    is_running: bool = Field(..., description="是否正在运行")
    task_id: Optional[str] = Field(None, description="任务ID")
    mode: Optional[str] = Field(None, description="爬虫模式")
    progress: Optional[int] = Field(None, description="进度百分比")
    total_crawled: int = Field(0, description="已爬取总数")
    success_count: int = Field(0, description="成功数量")
    failed_count: int = Field(0, description="失败数量")
    started_at: Optional[str] = Field(None, description="开始时间")
    current_status: str = Field("idle", description="当前状态")


class CrawlerHistoryItem(BaseModel):
    """爬虫历史记录项模型"""
    id: str = Field(..., description="记录ID")
    mode: str = Field(..., description="爬虫模式")
    status: str = Field(..., description="任务状态")
    started_at: str = Field(..., description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    total_crawled: int = Field(..., description="已爬取总数")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")


class CrawlerHistoryResponse(BaseModel):
    """爬虫历史响应模型"""
    items: List[CrawlerHistoryItem] = Field(..., description="历史记录列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
