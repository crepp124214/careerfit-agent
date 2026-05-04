from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportHistoryItem(BaseModel):
    task_id: int
    report_id: int
    job_id: int
    job_title: str
    resume_id: int
    resume_label: str
    final_score: int
    score_breakdown: dict
    gap_count: int
    high_risk_suggestion_count: int
    created_at: datetime


class ReportHistoryResponse(BaseModel):
    schema_version: str = "1"
    items: list[ReportHistoryItem]


class ReportRead(BaseModel):
    id: int
    task_id: int
    final_score: int
    score_breakdown: dict
    score_items: list = []
    strengths: list
    gaps: list
    resume_suggestions: list
    interview_questions: list
    learning_plan: list
    next_best_action: dict
    evidence: list
    scoring_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunRead(BaseModel):
    id: int
    task_id: int
    node_name: str
    status: str
    input_snapshot: dict
    output_snapshot: dict
    execution_meta: dict = {}
    started_at: datetime
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)
