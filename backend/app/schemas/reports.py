from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportRead(BaseModel):
    id: int
    task_id: int
    final_score: int
    score_breakdown: dict
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
    started_at: datetime
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)
