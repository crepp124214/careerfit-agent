"""LLM 调用监控和统计"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LLMCallRecord:
    """单次 LLM 调用记录"""

    timestamp: float
    duration: float
    success: bool
    error_type: str | None = None
    error_message: str | None = None
    prompt_length: int = 0
    response_length: int = 0
    model_name: str | None = None
    cached: bool = False


@dataclass
class LLMMetrics:
    """LLM 调用统计指标"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_duration: float = 0.0
    total_prompt_length: int = 0
    total_response_length: int = 0
    recent_calls: list[LLMCallRecord] = field(default_factory=list)

    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_call(
        self,
        duration: float,
        success: bool,
        error_type: str | None = None,
        error_message: str | None = None,
        prompt_length: int = 0,
        response_length: int = 0,
        model_name: str | None = None,
        cached: bool = False,
    ) -> None:
        """记录一次 LLM 调用"""
        with self._lock:
            self.total_calls += 1
            self.total_duration += duration
            self.total_prompt_length += prompt_length
            self.total_response_length += response_length

            if cached:
                self.cache_hits += 1
            else:
                self.cache_misses += 1

            if success:
                self.successful_calls += 1
            else:
                self.failed_calls += 1
                if error_type == "TimeoutException":
                    self.timeout_calls += 1

            record = LLMCallRecord(
                timestamp=time.time(),
                duration=duration,
                success=success,
                error_type=error_type,
                error_message=error_message,
                prompt_length=prompt_length,
                response_length=response_length,
                model_name=model_name,
                cached=cached,
            )
            self.recent_calls.append(record)

            if len(self.recent_calls) > 100:
                self.recent_calls = self.recent_calls[-100:]

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            success_rate = (
                self.successful_calls / self.total_calls if self.total_calls > 0 else 0.0
            )
            avg_duration = (
                self.total_duration / self.total_calls if self.total_calls > 0 else 0.0
            )
            avg_prompt_length = (
                self.total_prompt_length / self.total_calls
                if self.total_calls > 0
                else 0.0
            )
            avg_response_length = (
                self.total_response_length / self.total_calls
                if self.total_calls > 0
                else 0.0
            )
            cache_hit_rate = (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0.0
            )

            return {
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "timeout_calls": self.timeout_calls,
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "avg_prompt_length": avg_prompt_length,
                "avg_response_length": avg_response_length,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": cache_hit_rate,
                "recent_calls_count": len(self.recent_calls),
            }

    def get_recent_errors(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取最近的错误记录"""
        with self._lock:
            errors = [
                {
                    "timestamp": call.timestamp,
                    "duration": call.duration,
                    "error_type": call.error_type,
                    "error_message": call.error_message,
                    "model_name": call.model_name,
                }
                for call in self.recent_calls
                if not call.success
            ]
            return errors[-limit:]

    def reset(self) -> None:
        """重置统计信息"""
        with self._lock:
            self.total_calls = 0
            self.successful_calls = 0
            self.failed_calls = 0
            self.timeout_calls = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.total_duration = 0.0
            self.total_prompt_length = 0
            self.total_response_length = 0
            self.recent_calls.clear()
            logger.info("LLM metrics reset")


llm_metrics = LLMMetrics()
