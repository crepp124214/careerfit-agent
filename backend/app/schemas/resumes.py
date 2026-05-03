from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeCreate(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=200)
    version_label: str = Field(default="v1", min_length=1, max_length=100)
    raw_text: str = Field(min_length=20)


class ResumeRead(BaseModel):
    id: int
    candidate_name: str
    version_label: str
    raw_text: str
    profile: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
