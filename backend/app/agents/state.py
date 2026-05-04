from typing import Any, TypedDict


class CareerFitState(TypedDict, total=False):
    raw_jd: str
    raw_resume: str
    jd_profile: dict[str, Any]
    resume_profile: dict[str, Any]
    rag_results: dict[str, Any]
    match_result: dict[str, Any]
    gaps: list[dict[str, Any]]
    strengths: list[dict[str, Any]]
    resume_suggestions: list[dict[str, Any]]
    interview_questions: list[dict[str, Any]]
    learning_plan: list[dict[str, Any]]
    next_best_action: dict[str, Any]
    llm_enhancement: dict[str, Any]
