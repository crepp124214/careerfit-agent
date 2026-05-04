from __future__ import annotations

import json
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _repair_prompt(text: str) -> str:
    return "请把下面内容修复为严格 JSON，只保留指定字段，不要添加 Markdown：\n" + text


def run_structured_agent(
    *,
    client: Any | None,
    agent_role: str,
    prompt: str,
    output_model: type[T],
    enabled: bool = True,
    fallback: Callable[[], T] | None = None,
    model_name: str | None = None,
) -> tuple[T, dict[str, Any]]:
    if not enabled or client is None:
        if fallback is None:
            raise ValueError("LLM disabled but fallback is missing")
        result = fallback()
        return result, {
            "agent_role": agent_role,
            "execution_mode": "rule",
            "model_name": None,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
        }

    retry_count = 0
    first_text = client.complete(prompt)
    try:
        result = output_model.model_validate_json(first_text)
    except (ValidationError, ValueError, json.JSONDecodeError):
        retry_count = 1
        repair_text = client.complete(_repair_prompt(first_text))
        result = output_model.model_validate_json(repair_text)

    return result, {
        "agent_role": agent_role,
        "execution_mode": "llm",
        "model_name": model_name,
        "fallback_used": False,
        "schema_valid": True,
        "retry_count": retry_count,
    }
