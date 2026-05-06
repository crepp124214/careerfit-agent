"""线程池管理模块

用于管理后台任务线程，防止线程泄漏，确保云端部署时后台任务正常执行。
"""
from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Callable

logger = logging.getLogger(__name__)


class AnalysisThreadPool:
    """分析任务线程池管理器
    
    提供统一的线程池管理，解决云端部署时后台线程被提前终止的问题。
    
    使用方式:
        >>> pool = AnalysisThreadPool(max_workers=5)
        >>> future = pool.submit(task_function, arg1, arg2)
        >>> result = future.result()  # 等待任务完成
    """

    def __init__(self, max_workers: int = 5):
        """初始化线程池
        
        Args:
            max_workers: 最大工作线程数
        """
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="analysis-worker",
        )
        self._max_workers = max_workers
        self._active_tasks: dict[int, Future] = {}
        self._lock = threading.Lock()
        logger.info(f"分析任务线程池已初始化，最大工作线程数: {max_workers}")

    def submit(self, task_id: int, func: Callable, *args: Any, **kwargs: Any) -> Future:
        """提交任务到线程池
        
        Args:
            task_id: 任务ID
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future 对象，可用于获取任务结果或状态
        """
        with self._lock:
            # 清理已完成的任务
            completed_ids = [
                tid for tid, future in self._active_tasks.items()
                if future.done()
            ]
            for tid in completed_ids:
                del self._active_tasks[tid]

            # 提交新任务
            future = self._executor.submit(func, *args, **kwargs)
            self._active_tasks[task_id] = future
            logger.info(f"[Task {task_id}] 任务已提交到线程池，当前活跃任务数: {len(self._active_tasks)}")
            return future

    def is_task_running(self, task_id: int) -> bool:
        """检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务是否正在运行
        """
        with self._lock:
            future = self._active_tasks.get(task_id)
            if future is None:
                return False
            return not future.done()

    def get_task_status(self, task_id: int) -> str:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态: 'pending', 'running', 'completed', 'failed', 'not_found'
        """
        with self._lock:
            future = self._active_tasks.get(task_id)
            if future is None:
                return "not_found"
            if future.done():
                if future.exception() is not None:
                    return "failed"
                return "completed"
            return "running"

    def get_active_task_count(self) -> int:
        """获取当前活跃任务数
        
        Returns:
            活跃任务数量
        """
        with self._lock:
            return sum(
                1 for future in self._active_tasks.values()
                if not future.done()
            )

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        """关闭线程池
        
        Args:
            wait: 是否等待所有任务完成
            cancel_futures: 是否取消未完成的任务
        """
        logger.info("正在关闭分析任务线程池...")
        self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)
        logger.info("分析任务线程池已关闭")

    def __del__(self) -> None:
        """析构函数，确保线程池被正确关闭"""
        try:
            self.shutdown(wait=False)
        except Exception:
            pass


# 全局线程池实例
analysis_thread_pool = AnalysisThreadPool(max_workers=5)
