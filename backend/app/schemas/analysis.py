from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import AnalysisStatus


class AnalysisCreate(BaseModel):
    job_id: int = Field(..., gt=0, description="职位ID，必须为正整数")
    resume_id: int = Field(..., gt=0, description="简历ID，必须为正整数")

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("job_id 必须为正整数")
        return v

    @field_validator("resume_id")
    @classmethod
    def validate_resume_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("resume_id 必须为正整数")
        return v


class AnalysisTaskRead(BaseModel):
    id: int
    job_id: int
    resume_id: int
    status: AnalysisStatus
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
