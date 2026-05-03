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
    dimension: str
    rationale: str
    status: LearningTaskStatus
    evidence_refs: list
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
