from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class LLMResumeSuggestion(BaseModel):
    title: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)
    jd_requirement: str = ""
    resume_evidence: str = ""
    risk_level: Literal["low", "medium", "high"] = "low"


class LLMInterviewQuestion(BaseModel):
    skill: str = Field(min_length=1)
    question: str = Field(min_length=1)


class LLMLearningTask(BaseModel):
    skill: str = Field(min_length=1)
    task: str = Field(min_length=1)


class LLMNextBestAction(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    target_skill: str | None = None


class LLMReportEnhancement(BaseModel):
    resume_suggestions: list[LLMResumeSuggestion] = Field(default_factory=list)
    interview_questions: list[LLMInterviewQuestion] = Field(default_factory=list)
    learning_plan: list[LLMLearningTask] = Field(default_factory=list)
    next_best_action: LLMNextBestAction


class LLMOutputParseError(ValueError):
    pass


def _strip_code_fence(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def parse_llm_enhancement(text: str) -> LLMReportEnhancement:
    try:
        data = json.loads(_strip_code_fence(text).strip())
        return LLMReportEnhancement.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise LLMOutputParseError("LLM output is not valid report enhancement JSON") from exc
