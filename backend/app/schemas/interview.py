from __future__ import annotations

from pydantic import BaseModel, Field


class InterviewSessionCreate(BaseModel):
    report_id: int
    include_rag: bool = True


class InterviewQuestionRead(BaseModel):
    id: int
    skill: str
    category: str
    difficulty: str
    question: str
    answer_hint: str | None = None
    follow_ups: list[str] = Field(default_factory=list)
    source: str
    status: str
    notes: str | None = None
    sort_order: int = 0
    answer_text: str | None = None
    answer_score: int | None = None
    answer_feedback: dict | None = None
    answer_submitted_at: str | None = None
    attempt_count: int = 0


class InterviewQuestionUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class InterviewAnswerSubmit(BaseModel):
    answer_text: str = Field(..., min_length=1, max_length=5000)


class InterviewSessionRead(BaseModel):
    id: int
    report_id: int
    job_title: str
    status: str
    total_questions: int
    completed_questions: int
    created_at: str
    updated_at: str | None = None


class InterviewSessionDetailRead(BaseModel):
    schema_version: str = "1"
    id: int
    report_id: int
    job_title: str
    status: str
    total_questions: int
    completed_questions: int
    questions: list[InterviewQuestionRead] = Field(default_factory=list)
    created_at: str
    updated_at: str | None = None


class InterviewSessionListResponse(BaseModel):
    schema_version: str = "1"
    items: list[InterviewSessionRead]


class InterviewSessionCreateResponse(BaseModel):
    schema_version: str = "1"
    session: InterviewSessionRead


class InterviewAnswerSubmitResponse(BaseModel):
    schema_version: str = "1"
    id: int
    status: str
    answer_text: str | None = None
    answer_score: int | None = None
    answer_feedback: dict | None = None
    attempt_count: int = 0
