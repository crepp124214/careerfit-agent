"""LLM Client 调用缓存模块"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class LLMClientCache:
    """LLM 客户端调用缓存管理器
    
    缓存 LLM 的 complete 调用结果，避免重复请求相同的 prompt。
    适用于分析工作流中的重复 LLM 调用场景。
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, tuple[float, str]] = {}
        self._hits = 0
        self._misses = 0

    def _compute_key(self, prompt: str, model: str, api_style: str) -> str:
        """基于 prompt 和模型参数计算缓存 key"""
        data = {
            "prompt": prompt,
            "model": model,
            "api_style": api_style,
        }
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get(self, prompt: str, model: str, api_style: str) -> str | None:
        """从缓存获取 LLM 响应"""
        cache_key = self._compute_key(prompt, model, api_style)
        current_time = time.time()

        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if current_time - timestamp < self.ttl_seconds:
                self._hits += 1
                hit_rate = self.get_hit_rate()
                logger.info(
                    f"LLM client cache hit: key={cache_key[:8]}, "
                    f"age={int(current_time - timestamp)}s, "
                    f"hit_rate={hit_rate:.1%}"
                )
                return result
            else:
                del self._cache[cache_key]
                logger.debug(f"LLM client cache expired: key={cache_key[:8]}")

        self._misses += 1
        logger.debug(f"LLM client cache miss: key={cache_key[:8]}")
        return None

    def set(self, prompt: str, model: str, api_style: str, result: str) -> None:
        """将 LLM 响应存入缓存"""
        cache_key = self._compute_key(prompt, model, api_style)
        
        # 如果缓存已满，移除最旧的条目
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
            logger.debug(f"LLM client cache evicted: key={oldest_key[:8]}")
        
        self._cache[cache_key] = (time.time(), result)
        logger.info(
            f"LLM client cache set: key={cache_key[:8]}, "
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
            "max_size": self.max_size,
        }

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("LLM client cache cleared")


# 全局 LLM 客户端缓存实例
llm_client_cache = LLMClientCache(ttl_seconds=3600, max_size=1000)
