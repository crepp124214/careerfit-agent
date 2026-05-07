from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    raw_text: str = Field(min_length=20)


class JobRead(BaseModel):
    id: int
    title: str
    raw_text: str
    profile: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobCompareRequest(BaseModel):
    job_ids: list[int] = Field(min_length=2, max_length=5)


class JobCompareDimension(BaseModel):
    name: str
    category: str
    required_level: str
    weight: float


class JobCompareItem(BaseModel):
    job_id: int
    job_title: str
    dimensions: list[JobCompareDimension] = Field(default_factory=list)


class JobCompareResponse(BaseModel):
    schema_version: str = "1"
    items: list[JobCompareItem]
