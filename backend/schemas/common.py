"""Common Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码，从1开始")
    size: int = Field(20, ge=1, le=100, description="每页数量，最大100")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    message: str = Field(..., description="错误消息")
    code: Optional[str] = Field(None, description="错误代码")
    details: Optional[dict] = Field(None, description="错误详情")
