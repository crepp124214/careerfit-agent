from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import LearningTaskStatus


class LearningTaskGenerateRequest(BaseModel):
    task_id: int


class LearningTaskUpdateRequest(BaseModel):
    status: LearningTaskStatus


class LearningTaskRead(BaseModel):
    schema_version: str
    id: int
    source_task_id: int
    source_report_id: int
    title: str
    dimension: str | None = None
    rationale: str
    status: LearningTaskStatus
    evidence_refs: list
    
    # 面试准备计划字段（可选）
    skill: str | None = None
    target_question: str | None = None
    specific_actions: list[str] | None = None
    time_investment: str | None = None
    expected_outcome: str | None = None
    is_interview_prep: bool = False
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
