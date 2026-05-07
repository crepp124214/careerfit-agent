from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


class AnalysisCacheService:
    def __init__(self, ttl_seconds: int | None = None, max_size: int = 200):
        default_ttl = int(os.getenv("CAREERFIT_ANALYSIS_CACHE_TTL", "3600"))
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else default_ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[float, dict]] = {}
        self._hits = 0
        self._misses = 0

    def _compute_key(self, job_id: int, resume_id: int) -> str:
        data = json.dumps({"job_id": job_id, "resume_id": resume_id}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def get(self, job_id: int, resume_id: int) -> dict | None:
        cache_key = self._compute_key(job_id, resume_id)
        current_time = time.time()

        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if current_time - timestamp < self.ttl_seconds:
                self._hits += 1
                hit_rate = self.get_hit_rate()
                logger.info(
                    f"分析缓存命中: job_id={job_id}, resume_id={resume_id}, "
                    f"age={int(current_time - timestamp)}s, hit_rate={hit_rate:.1%}"
                )
                return result
            else:
                del self._cache[cache_key]
                logger.debug(f"分析缓存过期: job_id={job_id}, resume_id={resume_id}")

        self._misses += 1
        logger.debug(f"分析缓存未命中: job_id={job_id}, resume_id={resume_id}")
        return None

    def set(self, job_id: int, resume_id: int, data: dict) -> None:
        cache_key = self._compute_key(job_id, resume_id)

        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
            logger.debug("分析缓存条目已淘汰")

        self._cache[cache_key] = (time.time(), data)
        logger.debug(
            f"分析缓存已设置: job_id={job_id}, resume_id={resume_id}, "
            f"cache_size={len(self._cache)}"
        )

    def invalidate(self, job_id: int, resume_id: int) -> None:
        cache_key = self._compute_key(job_id, resume_id)
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"分析缓存已失效: job_id={job_id}, resume_id={resume_id}")

    def get_hit_rate(self) -> float:
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get_stats(self) -> dict[str, Any]:
        return {
            "cache_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.get_hit_rate(),
            "ttl_seconds": self.ttl_seconds,
            "max_size": self.max_size,
        }

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("分析缓存已清空")


analysis_cache = AnalysisCacheService()
