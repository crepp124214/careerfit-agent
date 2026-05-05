from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.llm.cache import llm_cache
from app.llm.client import LLMClient, LLMClientError
from app.llm.metrics import llm_metrics

router = APIRouter(prefix="/api/llm", tags=["llm"])

LLM_STATUS_CHECK_TIMEOUT_SECONDS = 180.0

TEST_PROMPT = """你是一个简历分析助手。请用JSON格式回复以下内容：
{
  "status": "ok",
  "model": "your model name",
  "capability": ["text-generation", "analysis"]
}

只返回JSON，不要其他内容。"""


class LLMStatusResponse(BaseModel):
    enabled: bool
    configured: bool
    connected: bool
    model_name: str | None = None
    error: str | None = None
    response_time_ms: float | None = None


@router.get("/status", response_model=LLMStatusResponse)
def get_llm_status():
    import time

    settings = get_settings()

    if not settings.llm_enabled:
        return LLMStatusResponse(
            enabled=False,
            configured=False,
            connected=False,
            error="LLM 功能未启用",
        )

    if not settings.llm_api_key or not settings.llm_model:
        return LLMStatusResponse(
            enabled=True,
            configured=False,
            connected=False,
            error="缺少 API Key 或模型名称配置",
        )

    try:
        start_time = time.time()

        client = LLMClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            api_style=settings.llm_api_style,
            timeout_seconds=LLM_STATUS_CHECK_TIMEOUT_SECONDS,
        )

        response = client.complete(TEST_PROMPT)
        elapsed_ms = (time.time() - start_time) * 1000
        client.close()

        if not response or len(response.strip()) == 0:
            return LLMStatusResponse(
                enabled=True,
                configured=True,
                connected=False,
                model_name=settings.llm_model,
                error="模型返回空响应",
                response_time_ms=elapsed_ms,
            )

        return LLMStatusResponse(
            enabled=True,
            configured=True,
            connected=True,
            model_name=settings.llm_model,
            response_time_ms=round(elapsed_ms, 2),
        )
    except LLMClientError as e:
        return LLMStatusResponse(
            enabled=True,
            configured=True,
            connected=False,
            model_name=settings.llm_model,
            error=f"连接失败: {str(e)}",
        )
    except Exception as e:
        return LLMStatusResponse(
            enabled=True,
            configured=True,
            connected=False,
            model_name=settings.llm_model,
            error=f"未知错误: {str(e)}",
        )


class LLMMetricsResponse(BaseModel):
    total_calls: int
    successful_calls: int
    failed_calls: int
    timeout_calls: int
    success_rate: float
    avg_duration: float
    avg_prompt_length: float
    avg_response_length: float
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    recent_calls_count: int


class LLMCacheStatsResponse(BaseModel):
    cache_size: int
    hits: int
    misses: int
    hit_rate: float
    ttl_seconds: int


@router.get("/metrics", response_model=LLMMetricsResponse)
def get_llm_metrics():
    """获取 LLM 调用统计信息"""
    stats = llm_metrics.get_stats()
    return LLMMetricsResponse(**stats)


@router.get("/cache/stats", response_model=LLMCacheStatsResponse)
def get_llm_cache_stats():
    """获取 LLM 缓存统计信息"""
    stats = llm_cache.get_stats()
    return LLMCacheStatsResponse(**stats)


@router.post("/cache/clear")
def clear_llm_cache():
    """清空 LLM 缓存"""
    llm_cache.clear()
    return {"message": "LLM cache cleared successfully"}


@router.post("/metrics/reset")
def reset_llm_metrics():
    """重置 LLM 统计信息"""
    llm_metrics.reset()
    return {"message": "LLM metrics reset successfully"}
