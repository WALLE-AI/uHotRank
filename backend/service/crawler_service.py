"""Crawler service for managing crawler tasks."""

import logging
import asyncio
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.schemas.crawler import (
    StartCrawlerRequest,
    StartCrawlerResponse,
    CrawlerStatus,
    CrawlerHistoryItem,
    CrawlerHistoryResponse,
)

logger = logging.getLogger(__name__)


class CrawlerService:
    """爬虫服务层 - 管理爬虫任务的生命周期（单例模式）"""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化爬虫服务"""
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.current_task: Optional[asyncio.Task] = None
        self.task_id: Optional[str] = None
        self.task_status: Dict[str, Any] = {
            "is_running": False,
            "mode": None,
            "progress": 0,
            "total_crawled": 0,
            "success_count": 0,
            "failed_count": 0,
            "started_at": None,
            "current_status": "idle",
        }
        self.task_history: List[Dict[str, Any]] = []
        self._initialized = True

    async def start_crawler(
        self, request: StartCrawlerRequest
    ) -> StartCrawlerResponse:
        """
        启动爬虫任务

        Args:
            request: 启动请求参数

        Returns:
            StartCrawlerResponse: 启动响应
        """
        async with self._lock:
            # 检查是否已有任务在运行
            if self.task_status["is_running"]:
                raise ValueError("已有爬虫任务正在运行，请等待完成或先停止当前任务")

            # 生成任务 ID
            self.task_id = str(uuid.uuid4())

            # 更新状态
            self.task_status = {
                "is_running": True,
                "mode": request.mode,
                "progress": 0,
                "total_crawled": 0,
                "success_count": 0,
                "failed_count": 0,
                "started_at": datetime.now().isoformat(),
                "current_status": "running",
            }

            # 启动异步任务
            self.current_task = asyncio.create_task(
                self._run_crawler_task(request.mode, request.batch_size)
            )

            logger.info(f"爬虫任务已启动: {self.task_id}, 模式: {request.mode}")

            return StartCrawlerResponse(
                task_id=self.task_id, message="Crawler task started successfully"
            )

    async def _run_crawler_task(self, mode: str, batch_size: int):
        """
        运行爬虫任务（后台任务）

        Args:
            mode: 爬虫模式
            batch_size: 批量大小
        """
        try:
            # 导入爬虫函数
            from backend.agent.agent_today_data import scrape_all_articles_to_es

            # 根据模式设置参数
            enable_analysis = mode == "with_analysis"
            
            # 运行爬虫（在线程池中执行，避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: scrape_all_articles_to_es(
                    es_index_name="tophub_articles",
                    batch_size=batch_size,
                    check_duplicate=True,
                    skip_duplicate=True,
                    enable_analysis=enable_analysis,
                ),
            )

            # 更新状态
            self.task_status["is_running"] = False
            self.task_status["current_status"] = "completed"
            self.task_status["total_crawled"] = result.get("total", 0)
            self.task_status["success_count"] = result.get("success", 0)
            self.task_status["failed_count"] = result.get("failed", 0)

            # 添加到历史记录
            history_item = {
                "id": self.task_id,
                "mode": mode,
                "status": "completed",
                "started_at": self.task_status["started_at"],
                "completed_at": datetime.now().isoformat(),
                "total_crawled": result.get("total", 0),
                "success_count": result.get("success", 0),
                "failed_count": result.get("failed", 0),
            }
            self.task_history.insert(0, history_item)  # 最新的在前面

            logger.info(f"爬虫任务完成: {self.task_id}")

        except asyncio.CancelledError:
            # 任务被取消
            self.task_status["is_running"] = False
            self.task_status["current_status"] = "stopped"

            # 添加到历史记录
            history_item = {
                "id": self.task_id,
                "mode": mode,
                "status": "stopped",
                "started_at": self.task_status["started_at"],
                "completed_at": datetime.now().isoformat(),
                "total_crawled": self.task_status["total_crawled"],
                "success_count": self.task_status["success_count"],
                "failed_count": self.task_status["failed_count"],
            }
            self.task_history.insert(0, history_item)

            logger.info(f"爬虫任务已停止: {self.task_id}")

        except Exception as e:
            # 任务失败
            self.task_status["is_running"] = False
            self.task_status["current_status"] = "failed"

            # 添加到历史记录
            history_item = {
                "id": self.task_id,
                "mode": mode,
                "status": "failed",
                "started_at": self.task_status["started_at"],
                "completed_at": datetime.now().isoformat(),
                "total_crawled": self.task_status["total_crawled"],
                "success_count": self.task_status["success_count"],
                "failed_count": self.task_status["failed_count"],
                "error": str(e),
            }
            self.task_history.insert(0, history_item)

            logger.error(f"爬虫任务失败: {self.task_id}, 错误: {e}")

    async def get_status(self) -> CrawlerStatus:
        """
        获取当前爬虫状态

        Returns:
            CrawlerStatus: 爬虫状态
        """
        return CrawlerStatus(
            is_running=self.task_status["is_running"],
            task_id=self.task_id if self.task_status["is_running"] else None,
            mode=self.task_status["mode"],
            progress=self.task_status["progress"],
            total_crawled=self.task_status["total_crawled"],
            success_count=self.task_status["success_count"],
            failed_count=self.task_status["failed_count"],
            started_at=self.task_status["started_at"],
            current_status=self.task_status["current_status"],
        )

    async def stop_crawler(self) -> None:
        """
        停止当前运行的爬虫任务

        Raises:
            ValueError: 如果没有运行中的任务
        """
        async with self._lock:
            if not self.task_status["is_running"]:
                raise ValueError("没有正在运行的爬虫任务")

            if self.current_task and not self.current_task.done():
                self.current_task.cancel()
                logger.info(f"正在停止爬虫任务: {self.task_id}")

                # 等待任务完成取消
                try:
                    await self.current_task
                except asyncio.CancelledError:
                    pass

    async def get_history(
        self, page: int = 1, size: int = 20
    ) -> CrawlerHistoryResponse:
        """
        获取爬虫历史记录

        Args:
            page: 页码
            size: 每页数量

        Returns:
            CrawlerHistoryResponse: 历史记录响应
        """
        # 计算分页
        total = len(self.task_history)
        start = (page - 1) * size
        end = start + size

        # 获取当前页的数据
        page_items = self.task_history[start:end]

        # 转换为模型
        items = [
            CrawlerHistoryItem(
                id=item["id"],
                mode=item["mode"],
                status=item["status"],
                started_at=item["started_at"],
                completed_at=item.get("completed_at"),
                total_crawled=item["total_crawled"],
                success_count=item["success_count"],
                failed_count=item["failed_count"],
            )
            for item in page_items
        ]

        return CrawlerHistoryResponse(items=items, total=total, page=page, size=size)
