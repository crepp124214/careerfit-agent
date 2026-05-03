from __future__ import annotations

from app.agents.state import CareerFitState
from app.core.config import Settings, get_settings
from app.llm.client import LLMClient
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
) -> LLMReportEnhancement | None:
    settings = get_settings()
    should_run = settings.llm_enabled if enabled is None else enabled
    if not should_run:
        return None

    client = build_llm_client(settings)
    first_text = client.complete(build_report_enhancement_prompt(state))
    try:
        return parse_llm_enhancement(first_text)
    except LLMOutputParseError:
        repair_text = client.complete(build_report_enhancement_prompt(state, repair_text=first_text))
        return parse_llm_enhancement(repair_text)
