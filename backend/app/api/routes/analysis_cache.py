"""分析事件回放缓存模块"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class AnalysisEventCache:
    """分析任务事件回放缓存管理器
    
    缓存已完成任务的事件回放结果，避免重复计算。
    """

    def __init__(self, ttl_seconds: int = 600, max_size: int = 500):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._hits = 0
        self._misses = 0

    def _compute_key(self, task_id: int, runs_data: str) -> str:
        """基于任务ID和运行数据计算缓存 key"""
        data = {
            "task_id": task_id,
            "runs": runs_data,
        }
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get(self, task_id: int, runs: list) -> list[dict] | None:
        """从缓存获取事件回放结果"""
        runs_data = json.dumps([self._run_to_dict(r) for r in runs], sort_keys=True, ensure_ascii=False)
        cache_key = self._compute_key(task_id, runs_data)
        current_time = time.time()

        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if current_time - timestamp < self.ttl_seconds:
                self._hits += 1
                hit_rate = self.get_hit_rate()
                logger.debug(
                    f"Analysis event cache hit: task_id={task_id}, "
                    f"age={int(current_time - timestamp)}s, "
                    f"hit_rate={hit_rate:.1%}"
                )
                return result
            else:
                del self._cache[cache_key]
                logger.debug(f"Analysis event cache expired: task_id={task_id}")

        self._misses += 1
        logger.debug(f"Analysis event cache miss: task_id={task_id}")
        return None

    def set(self, task_id: int, runs: list, events: list[dict]) -> None:
        """将事件回放结果存入缓存"""
        runs_data = json.dumps([self._run_to_dict(r) for r in runs], sort_keys=True, ensure_ascii=False)
        cache_key = self._compute_key(task_id, runs_data)
        
        # 如果缓存已满，移除最旧的条目
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
            logger.debug("Analysis event cache evicted")
        
        self._cache[cache_key] = (time.time(), events)
        logger.debug(
            f"Analysis event cache set: task_id={task_id}, "
            f"cache_size={len(self._cache)}"
        )

    def invalidate_task(self, task_id: int) -> None:
        """使指定任务的所有缓存失效"""
        keys_to_remove = [
            key for key in self._cache.keys() 
            if key.startswith(str(task_id))
        ]
        for key in keys_to_remove:
            del self._cache[key]
        if keys_to_remove:
            logger.debug(f"Analysis event cache invalidated: task_id={task_id}, count={len(keys_to_remove)}")

    def _run_to_dict(self, run) -> dict:
        """将 AgentRun 对象转换为可序列化的字典"""
        return {
            "id": run.id,
            "node_name": run.node_name,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "execution_meta": run.execution_meta,
        }

    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "cache_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.get_hit_rate(),
            "ttl_seconds": self.ttl_seconds,
            "max_size": self.max_size,
        }

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Analysis event cache cleared")


# 全局事件回放缓存实例
analysis_event_cache = AnalysisEventCache(ttl_seconds=600, max_size=500)
