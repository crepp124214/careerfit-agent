import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SkillDimension(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    canonical_key: str
    category: str = "technical"
    weight: float = Field(default=0.7, ge=0, le=1)
    required_level: Literal["mentioned", "basic_usage", "project_practice", "deep_experience"] = "project_practice"
    jd_evidence: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)

    @field_validator("name", "canonical_key")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("字段不能为空")
        return stripped

    @field_validator("jd_evidence")
    @classmethod
    def non_empty_evidence(cls, value: list[str]) -> list[str]:
        if len(value) == 0:
            raise ValueError("jd_evidence 不能为空列表，至少需要一条证据")
        return value


class JDParseOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    job_family: str = "software_engineering"
    dimensions: list[SkillDimension] = Field(min_length=1)
    evidence_summary: str = ""


class ResumeEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skill_key: str
    evidence: list[str] = Field(default_factory=list)
    expression_level: Literal["not_mentioned", "mentioned", "basic_usage", "project_practice", "deep_experience"] = "mentioned"


class ResumeParseOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skills: list[ResumeEvidenceItem] = Field(min_length=1)
    project_summary: str = ""
    evidence_summary: str = ""


class RagQueryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skill_key: str
    query: str
    job_family: str = ""
    doc_types: list[str] = Field(default_factory=list)


class RagQueryPlanOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    queries: list[RagQueryItem] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_queries(cls, values: Any) -> Any:
        if isinstance(values, list):
            return {"queries": values}
        return values


class GapItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skill_key: str = ""
    gap_type: Literal["missing_skill", "weak_evidence", "expression_gap", "knowledge_insufficient"] = "missing_skill"
    reason: str = ""
    priority: Literal["high", "medium", "low"] = "medium"


class GapAnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    gaps: list[GapItem] = Field(default_factory=list)
    strengths: list[dict] = Field(default_factory=list)


class ResumeSuggestionOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    suggestions: list[dict] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_suggestions(cls, values: Any) -> Any:
        if isinstance(values, list):
            return {"suggestions": values}
        if isinstance(values, dict):
            if "recommendations" in values and "suggestions" not in values:
                values["suggestions"] = values.pop("recommendations")
        return values


class InterviewQuestionOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    questions: list[dict] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_questions(cls, values: Any) -> Any:
        if isinstance(values, list):
            return {"questions": values}
        return values


class LearningPlanOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tasks: list[dict] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_tasks(cls, values: Any) -> Any:
        if isinstance(values, list):
            return {"tasks": values}
        if isinstance(values, dict):
            if "learning_plans" in values and "tasks" not in values:
                values["tasks"] = values.pop("learning_plans")
        return values


class NextBestActionOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    description: str = ""
    target_skill: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_nba(cls, values: Any) -> Any:
        if isinstance(values, list):
            if len(values) > 0:
                first = values[0]
                if isinstance(first, dict):
                    return first
            return {"title": "", "description": ""}
        return values

    @field_validator("target_skill", mode="before")
    @classmethod
    def normalize_target_skill(cls, v: Any) -> str | None:
        if isinstance(v, dict):
            return v.get("skill_key") or v.get("name") or json.dumps(v, ensure_ascii=False)[:100]
        if isinstance(v, (list, tuple)):
            return str(v[0]) if v else None
        return v


class IntegrityCriticOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["low", "medium", "high"]
    risk_codes: list[str] = Field(default_factory=list)
    reason: str


class AnswerScoreOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)
    correctness_feedback: str
    completeness_feedback: str
    clarity_feedback: str
    improvement_suggestion: str
