from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import AnalysisStatus


class AnalysisCreate(BaseModel):
    job_id: int
    resume_id: int


class AnalysisTaskRead(BaseModel):
    id: int
    job_id: int
    resume_id: int
    status: AnalysisStatus
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
