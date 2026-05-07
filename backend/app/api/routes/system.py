from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.thread_pool import analysis_thread_pool
from app.services.analysis_cache_service import analysis_cache

router = APIRouter(prefix="/api/system", tags=["system"])


class CacheStatsResponse(BaseModel):
    schema_version: str = "1"
    cache_size: int
    hits: int
    misses: int
    hit_rate: float
    ttl_seconds: int
    max_size: int


class ThreadPoolStatsResponse(BaseModel):
    schema_version: str = "1"
    max_workers: int
    active_tasks: int
    completed_tasks: int
    queued_tasks: int


class ClearCacheResponse(BaseModel):
    schema_version: str = "1"
    cleared: bool = True


@router.get("/cache/stats", response_model=CacheStatsResponse)
def get_cache_stats():
    stats = analysis_cache.get_stats()
    return CacheStatsResponse(
        cache_size=stats["cache_size"],
        hits=stats["hits"],
        misses=stats["misses"],
        hit_rate=stats["hit_rate"],
        ttl_seconds=stats["ttl_seconds"],
        max_size=stats["max_size"],
    )


@router.post("/cache/clear", response_model=ClearCacheResponse)
def clear_cache():
    analysis_cache.clear()
    return ClearCacheResponse()


@router.get("/pool/stats", response_model=ThreadPoolStatsResponse)
def get_pool_stats():
    stats = analysis_thread_pool.get_stats()
    return ThreadPoolStatsResponse(
        max_workers=stats["max_workers"],
        active_tasks=stats["active_tasks"],
        completed_tasks=stats["completed_tasks"],
        queued_tasks=stats.get("queued_tasks", 0),
    )
