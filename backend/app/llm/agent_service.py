from __future__ import annotations

import json
import logging
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

MAX_JSON_REPAIR_ATTEMPTS = 2


def _repair_prompt(text: str, schema_hint: str = "") -> str:
    hint = f"\n\n目标 JSON 结构要求：{schema_hint}" if schema_hint else ""
    return (
        "你之前的输出不是合法的 JSON 或缺少必要字段。"
        "请严格按以下要求重新输出：\n"
        "1. 只输出纯 JSON，不要 Markdown 代码块标记\n"
        "2. 包含所有必需字段\n"
        "3. 不要添加任何额外字段\n"
        f"4. 原始输出：{text}{hint}"
    )


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


class AgentLLMError(Exception):
    def __init__(self, message: str, last_output: str = "", validation_errors: list[str] | None = None):
        super().__init__(message)
        self.last_output = last_output
        self.validation_errors = validation_errors or []


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
            "model_name": model_name,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
            "llm_error": "llm_unavailable",
        }

    retry_count = 0
    last_text = ""
    last_errors: list[str] = []

    try:
        first_text = client.complete(prompt)
        last_text = first_text
        first_text = _extract_json(first_text)
        result = output_model.model_validate_json(first_text)
    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        retry_count += 1
        last_errors = _collect_validation_errors(exc)
        logger.warning(
            "[%s] LLM output JSON validation failed (attempt %d/%d): %s",
            agent_role, 1, MAX_JSON_REPAIR_ATTEMPTS + 1,
            exc,
        )

        json_schema = output_model.model_json_schema()
        schema_hint = json.dumps(list(json_schema.get("properties", {}).keys()), ensure_ascii=False)

        for attempt in range(2, MAX_JSON_REPAIR_ATTEMPTS + 2):
            try:
                repair_prompt = _repair_prompt(last_text, schema_hint)
                repair_text = client.complete(repair_prompt)
                last_text = repair_text
                repair_text = _extract_json(repair_text)
                result = output_model.model_validate_json(repair_text)
                retry_count = attempt
                logger.info("[%s] LLM output repaired successfully on attempt %d", agent_role, attempt)
                break
            except (ValidationError, ValueError, json.JSONDecodeError) as exc:
                retry_count = attempt
                last_errors = _collect_validation_errors(exc)
                logger.warning(
                    "[%s] LLM output repair failed (attempt %d/%d): %s",
                    agent_role, attempt, MAX_JSON_REPAIR_ATTEMPTS + 1, exc,
                )
        else:
            raise AgentLLMError(
                message=f"JSON format invalid after {MAX_JSON_REPAIR_ATTEMPTS} repair attempts",
                last_output=last_text[:500],
                validation_errors=last_errors[-5:] if last_errors else [],
            )

    return result, {
        "agent_role": agent_role,
        "execution_mode": "llm",
        "model_name": model_name,
        "fallback_used": False,
        "schema_valid": True,
        "retry_count": retry_count,
        "llm_error": None,
    }


def _collect_validation_errors(exc: BaseException) -> list[str]:
    errors = []
    if isinstance(exc, ValidationError):
        for e in exc.errors():
            loc = " → ".join(str(x) for x in e["loc"])
            errors.append(f"{loc}: {e['msg']}")
    else:
        errors.append(str(exc))
    return errors
