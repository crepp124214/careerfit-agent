from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    doc_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=500)
    content: str
    metadata: dict = Field(default_factory=lambda: {"schema_version": "1"})


class KnowledgeImportRequest(BaseModel):
    documents: list[KnowledgeDocumentCreate]


class KnowledgeImportResponse(BaseModel):
    schema_version: str = "1"
    imported_count: int
    skipped_count: int


class KnowledgeSearchResult(BaseModel):
    id: int
    doc_type: str
    title: str
    content_snippet: str
    score: float
    metadata: dict = Field(default_factory=dict)


class KnowledgeSearchResponse(BaseModel):
    schema_version: str = "1"
    results: list[KnowledgeSearchResult]
