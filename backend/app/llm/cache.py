"""LLM 结果缓存模块"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from functools import lru_cache
from typing import Any

from app.agents.state import CareerFitState
from app.llm.schemas import LLMReportEnhancement


logger = logging.getLogger(__name__)


class LLMCache:
    """LLM 结果缓存管理器"""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, LLMReportEnhancement]] = {}
        self._hits = 0
        self._misses = 0

    def _compute_cache_key(self, state: CareerFitState) -> str:
        """基于输入状态计算缓存 key"""
        relevant_data = {
            "gaps": state.get("gaps", []),
            "strengths": state.get("strengths", []),
            "score_items": state.get("match_result", {}).get("score_items", []),
        }
        data_str = json.dumps(relevant_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get(self, state: CareerFitState) -> LLMReportEnhancement | None:
        """从缓存获取结果"""
        cache_key = self._compute_cache_key(state)
        current_time = time.time()

        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if current_time - timestamp < self.ttl_seconds:
                self._hits += 1
                logger.info(
                    f"LLM cache hit: key={cache_key[:8]}, "
                    f"age={int(current_time - timestamp)}s, "
                    f"hit_rate={self.get_hit_rate():.1%}"
                )
                return result
            else:
                del self._cache[cache_key]
                logger.debug(f"LLM cache expired: key={cache_key[:8]}")

        self._misses += 1
        logger.debug(f"LLM cache miss: key={cache_key[:8]}")
        return None

    def set(self, state: CareerFitState, result: LLMReportEnhancement) -> None:
        """将结果存入缓存"""
        cache_key = self._compute_cache_key(state)
        self._cache[cache_key] = (time.time(), result)
        logger.info(
            f"LLM cache set: key={cache_key[:8]}, "
            f"cache_size={len(self._cache)}, "
            f"ttl={self.ttl_seconds}s"
        )

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
        }

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("LLM cache cleared")


llm_cache = LLMCache(ttl_seconds=3600)
