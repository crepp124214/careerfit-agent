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
