from __future__ import annotations

import asyncio
import logging
import time

import httpx

from app.agents.state import CareerFitState
from app.core.config import Settings, get_settings
from app.llm.cache import llm_cache
from app.llm.client import LLMClient
from app.llm.concurrent import generate_report_enhancement_concurrent
from app.llm.metrics import llm_metrics
from app.llm.prompts import build_report_enhancement_prompt
from app.llm.schemas import LLMOutputParseError, LLMReportEnhancement, parse_llm_enhancement


def build_llm_client(settings: Settings) -> LLMClient:
    if not settings.llm_api_key or not settings.llm_model:
        raise ValueError("LLM provider is missing api_key or model")
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        api_style=settings.llm_api_style,
        timeout_seconds=settings.llm_timeout_seconds,
    )


def generate_report_enhancement(
    state: CareerFitState,
    *,
    enabled: bool | None = None,
) -> tuple[LLMReportEnhancement | None, str | None]:
    settings = get_settings()
    should_run = settings.llm_enabled if enabled is None else enabled
    if not should_run:
        return None, None

    logger = logging.getLogger(__name__)

    cached_result = llm_cache.get(state)
    if cached_result:
        logger.info("Using cached LLM enhancement result")
        llm_metrics.record_call(
            duration=0.0,
            success=True,
            cached=True,
            model_name=settings.llm_model,
        )
        return cached_result, settings.llm_model

    client = build_llm_client(settings)
    model_name = settings.llm_model

    if settings.llm_concurrent_enabled:
        logger.info(
            f"Starting concurrent LLM enhancement with model={model_name}, "
            f"timeout={settings.llm_timeout_seconds}s"
        )
        try:
            enhancement = asyncio.run(generate_report_enhancement_concurrent(state, client))
            llm_cache.set(state, enhancement)
            return enhancement, model_name
        except Exception as exc:
            logger.error(f"Concurrent LLM enhancement failed: {exc}")
            logger.info("Falling back to single-call mode")
            return _generate_report_enhancement_single(state, client, settings, logger)
    else:
        return _generate_report_enhancement_single(state, client, settings, logger)


def _generate_report_enhancement_single(
    state: CareerFitState,
    client: LLMClient,
    settings: Settings,
    logger: logging.Logger,
) -> tuple[LLMReportEnhancement | None, str | None]:
    """单次调用模式生成报告增强"""
    model_name = settings.llm_model

    logger.info(
        f"Starting single-call LLM enhancement with model={model_name}, "
        f"timeout={settings.llm_timeout_seconds}s, "
        f"base_url={settings.llm_base_url}"
    )

    try:
        first_text = client.complete(build_report_enhancement_prompt(state))
    except httpx.TimeoutException as exc:
        logger.warning(
            f"LLM call timeout after {settings.llm_timeout_seconds}s, "
            f"retrying with extended timeout (180s)"
        )
        client.http_client.timeout = httpx.Timeout(180.0)
        try:
            first_text = client.complete(build_report_enhancement_prompt(state))
        except httpx.TimeoutException as exc:
            logger.error(
                f"LLM call timeout again after extended timeout (180s), "
                f"giving up and falling back to rule engine"
            )
            raise
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"LLM call HTTP error: {exc.response.status_code}, "
            f"response={exc.response.text[:500]}"
        )
        raise
    except Exception as exc:
        logger.error(f"LLM call unexpected error: {type(exc).__name__}: {exc}")
        raise

    try:
        result = parse_llm_enhancement(first_text)
        logger.info("LLM enhancement completed successfully")
        llm_cache.set(state, result)
        return result, model_name
    except LLMOutputParseError:
        logger.warning("LLM output is not valid JSON, attempting repair")
        repair_text = client.complete(build_report_enhancement_prompt(state, repair_text=first_text))
        result = parse_llm_enhancement(repair_text)
        logger.info("LLM enhancement completed successfully after repair")
        llm_cache.set(state, result)
        return result, model_name
