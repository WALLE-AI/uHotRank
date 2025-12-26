"""Statistics service for data analysis and aggregation."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from backend.db.elasticsearch_client import ArticleRepository
from backend.schemas.statistics import (
    OverallStatistics,
    KeywordStat,
    KeywordStats,
    CategoryStats,
    SentimentStats,
    SourceStats,
    TrendDataPoint,
    TrendStats,
)

logger = logging.getLogger(__name__)


class StatsService:
    """统计服务层 - 提供数据分析和统计功能"""

    def __init__(self, repository: ArticleRepository):
        """
        初始化统计服务

        Args:
            repository: 文章数据仓库实例
        """
        self.repository = repository

    def get_overall_statistics(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> OverallStatistics:
        """
        获取总体统计信息

        Args:
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）

        Returns:
            OverallStatistics: 总体统计数据
        """
        try:
            # 构建日期过滤查询
            date_query = self._build_date_query(date_from, date_to)

            # 获取总文章数
            total_articles = self.repository.count(query=date_query)

            # 获取今日新增（最近24小时）
            today_start = (datetime.now() - timedelta(days=1)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            today_query = {"range": {"scraped_at": {"gte": today_start}}}
            today_new = self.repository.count(query=today_query)

            # 获取技术文章数
            tech_query = {"term": {"tech_detection.is_tech_related": True}}
            if date_query:
                tech_query = {"bool": {"must": [tech_query, date_query]}}
            tech_articles = self.repository.count(query=tech_query)

            # 获取已分析文章数
            analyzed_query = {"term": {"content_analysis.analysis_success": True}}
            if date_query:
                analyzed_query = {"bool": {"must": [analyzed_query, date_query]}}
            analyzed_articles = self.repository.count(query=analyzed_query)

            # 获取分类数量
            categories = self.get_category_stats(date_from, date_to)
            categories_count = len(categories.categories)

            # 计算平均情感分数
            sentiments = self.get_sentiment_stats(date_from, date_to)
            total_sentiment_articles = (
                sentiments.positive + sentiments.neutral + sentiments.negative
            )
            if total_sentiment_articles > 0:
                # 正面=1, 中性=0, 负面=-1
                avg_sentiment_score = (
                    sentiments.positive - sentiments.negative
                ) / total_sentiment_articles
            else:
                avg_sentiment_score = 0.0

            return OverallStatistics(
                total_articles=total_articles,
                today_new=today_new,
                tech_articles=tech_articles,
                analyzed_articles=analyzed_articles,
                categories_count=categories_count,
                avg_sentiment_score=round(avg_sentiment_score, 2),
            )

        except Exception as e:
            logger.error(f"获取总体统计失败: {e}")
            raise

    def get_keyword_stats(self, top_n: int = 50) -> KeywordStats:
        """
        获取关键词统计

        Args:
            top_n: 返回前 N 个关键词

        Returns:
            KeywordStats: 关键词统计数据
        """
        try:
            keyword_data = self.repository.get_keyword_statistics(top_n=top_n)

            keywords = [
                KeywordStat(keyword=item["keyword"], count=item["count"])
                for item in keyword_data
            ]

            return KeywordStats(keywords=keywords)

        except Exception as e:
            logger.error(f"获取关键词统计失败: {e}")
            raise

    def get_category_stats(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> CategoryStats:
        """
        获取分类统计

        Args:
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）

        Returns:
            CategoryStats: 分类统计数据
        """
        try:
            # 构建聚合查询
            date_query = self._build_date_query(date_from, date_to)

            agg_query = {
                "size": 0,
                "aggs": {
                    "categories": {
                        "terms": {"field": "content_analysis.category.keyword", "size": 100}
                    }
                },
            }

            if date_query:
                agg_query["query"] = date_query

            result = self.repository.es.search(
                index=self.repository.index_name, body=agg_query
            )

            buckets = (
                result.get("aggregations", {}).get("categories", {}).get("buckets", [])
            )

            categories = {bucket["key"]: bucket["doc_count"] for bucket in buckets}

            return CategoryStats(categories=categories)

        except Exception as e:
            logger.error(f"获取分类统计失败: {e}")
            raise

    def get_sentiment_stats(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> SentimentStats:
        """
        获取情感统计

        Args:
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）

        Returns:
            SentimentStats: 情感统计数据
        """
        try:
            # 构建聚合查询
            date_query = self._build_date_query(date_from, date_to)

            agg_query = {
                "size": 0,
                "aggs": {
                    "sentiments": {"terms": {"field": "content_analysis.sentiment.keyword"}}
                },
            }

            if date_query:
                agg_query["query"] = date_query

            result = self.repository.es.search(
                index=self.repository.index_name, body=agg_query
            )

            buckets = (
                result.get("aggregations", {}).get("sentiments", {}).get("buckets", [])
            )

            sentiment_dict = {bucket["key"]: bucket["doc_count"] for bucket in buckets}

            return SentimentStats(
                positive=sentiment_dict.get("positive", 0),
                neutral=sentiment_dict.get("neutral", 0),
                negative=sentiment_dict.get("negative", 0),
            )

        except Exception as e:
            logger.error(f"获取情感统计失败: {e}")
            raise

    def get_source_stats(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> SourceStats:
        """
        获取来源统计

        Args:
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）

        Returns:
            SourceStats: 来源统计数据
        """
        try:
            # 构建聚合查询（按 category 字段统计，因为它代表来源网站）
            date_query = self._build_date_query(date_from, date_to)

            agg_query = {
                "size": 0,
                "aggs": {"sources": {"terms": {"field": "category", "size": 100}}},
            }

            if date_query:
                agg_query["query"] = date_query

            result = self.repository.es.search(
                index=self.repository.index_name, body=agg_query
            )

            buckets = (
                result.get("aggregations", {}).get("sources", {}).get("buckets", [])
            )

            sources = {bucket["key"]: bucket["doc_count"] for bucket in buckets}

            return SourceStats(sources=sources)

        except Exception as e:
            logger.error(f"获取来源统计失败: {e}")
            raise

    def get_trend_stats(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> TrendStats:
        """
        获取趋势统计（按日期聚合）

        Args:
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）

        Returns:
            TrendStats: 趋势统计数据
        """
        try:
            # 构建日期直方图聚合查询
            date_query = self._build_date_query(date_from, date_to)

            agg_query = {
                "size": 0,
                "aggs": {
                    "trends": {
                        "date_histogram": {
                            "field": "publish_date",
                            "calendar_interval": "day",
                            "format": "yyyy-MM-dd",
                            "min_doc_count": 0,
                        }
                    }
                },
            }

            if date_query:
                agg_query["query"] = date_query

            result = self.repository.es.search(
                index=self.repository.index_name, body=agg_query
            )

            buckets = (
                result.get("aggregations", {}).get("trends", {}).get("buckets", [])
            )

            trends = [
                TrendDataPoint(date=bucket["key_as_string"], count=bucket["doc_count"])
                for bucket in buckets
            ]

            return TrendStats(trends=trends)

        except Exception as e:
            logger.error(f"获取趋势统计失败: {e}")
            raise

    def _build_date_query(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        构建日期范围查询

        Args:
            date_from: 开始日期
            date_to: 结束日期

        Returns:
            查询条件，如果没有日期限制则返回 None
        """
        if not date_from and not date_to:
            return None

        date_range = {}
        if date_from:
            date_range["gte"] = date_from
        if date_to:
            date_range["lte"] = date_to

        return {"range": {"publish_date": date_range}}
