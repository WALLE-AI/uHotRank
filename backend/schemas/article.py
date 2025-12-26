"""Article-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Entity(BaseModel):
    """实体模型"""
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型")


class ContentAnalysis(BaseModel):
    """内容分析模型"""
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    topics: List[str] = Field(default_factory=list, description="主题列表")
    summary: str = Field("", description="内容摘要")
    sentiment: str = Field("neutral", description="情感倾向")
    category: str = Field("", description="分类")
    entities: List[Entity] = Field(default_factory=list, description="实体列表")


class TechDetection(BaseModel):
    """技术检测模型"""
    is_tech_related: bool = Field(False, description="是否技术相关")
    categories: List[str] = Field(default_factory=list, description="技术分类")
    confidence: float = Field(0.0, description="置信度")
    matched_keywords: List[str] = Field(default_factory=list, description="匹配的关键词")


class ArticleBase(BaseModel):
    """文章基础模型"""
    id: str = Field(..., description="文章ID")
    url: str = Field(..., description="文章URL")
    title: str = Field(..., description="文章标题")
    category: str = Field(..., description="文章分类")
    published_time: str = Field(..., description="发布时间")
    content: Optional[str] = Field(None, description="文章内容")
    tech_detection: Optional[TechDetection] = Field(None, description="技术检测结果")
    content_analysis: Optional[ContentAnalysis] = Field(None, description="内容分析结果")
    created_at: str = Field(..., description="创建时间")


class ArticleDetail(ArticleBase):
    """文章详情模型（完整信息）"""
    pass


class ArticleListItem(BaseModel):
    """文章列表项模型（简化版）"""
    id: str = Field(..., description="文章ID")
    url: str = Field(..., description="文章URL")
    title: str = Field(..., description="文章标题")
    category: str = Field(..., description="文章分类")
    published_time: Optional[str] = Field(None, description="发布时间")
    summary: Optional[str] = Field(None, description="内容摘要")
    sentiment: Optional[str] = Field(None, description="情感倾向")


class ArticleListResponse(BaseModel):
    """文章列表响应模型"""
    articles: List[ArticleListItem] = Field(..., description="文章列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")


class SearchFilters(BaseModel):
    """搜索过滤器模型"""
    categories: Optional[List[str]] = Field(None, description="分类过滤")
    sentiments: Optional[List[str]] = Field(None, description="情感过滤")
    date_from: Optional[str] = Field(None, description="开始日期")
    date_to: Optional[str] = Field(None, description="结束日期")
    tech_only: Optional[bool] = Field(None, description="仅技术文章")


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: Optional[str] = Field(None, description="搜索关键词")
    filters: Optional[SearchFilters] = Field(None, description="过滤条件")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field(None, description="排序字段")


class SearchResponse(BaseModel):
    """搜索响应模型"""
    articles: List[ArticleListItem] = Field(..., description="文章列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
