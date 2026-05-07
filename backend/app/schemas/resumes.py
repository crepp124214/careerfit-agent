from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeCreate(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=200)
    version_label: str = Field(default="v1", min_length=1, max_length=100)
    raw_text: str = Field(min_length=20)


class ResumeUploadResponse(BaseModel):
    id: int
    candidate_name: str
    version_label: str
    raw_text: str
    parsed_from: str
    profile: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeRead(BaseModel):
    id: int
    candidate_name: str
    version_label: str
    raw_text: str
    profile: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDiffResumeRef(BaseModel):
    id: int
    version_label: str
    candidate_name: str


class ResumeDiffSummary(BaseModel):
    added_lines: int
    removed_lines: int
    unchanged_lines: int


class ResumeDiffSection(BaseModel):
    type: str
    text: str
    old_line: int | None = None
    new_line: int | None = None


class ResumeScoreContext(BaseModel):
    available: bool
    from_score: int | None = None
    to_score: int | None = None
    from_report_created_at: datetime | None = None
    to_report_created_at: datetime | None = None
    reason: str | None = None


class ResumeDiffResponse(BaseModel):
    schema_version: str = "1"
    from_resume: ResumeDiffResumeRef
    to_resume: ResumeDiffResumeRef
    summary: ResumeDiffSummary
    sections: list[ResumeDiffSection]
    score_context: ResumeScoreContext
