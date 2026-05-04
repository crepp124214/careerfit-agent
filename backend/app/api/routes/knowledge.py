from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.knowledge import (
    KnowledgeImportRequest,
    KnowledgeImportResponse,
    KnowledgeSearchResponse,
)
from app.services.knowledge_service import import_documents, search_documents

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/import", response_model=KnowledgeImportResponse)
def import_knowledge_endpoint(
    payload: KnowledgeImportRequest, db: Session = Depends(get_db)
):
    imported, skipped = import_documents(db, payload.documents)
    return KnowledgeImportResponse(imported_count=imported, skipped_count=skipped)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge_endpoint(
    q: str = Query(default=""),
    doc_type: str | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    results = search_documents(db, query=q, doc_type=doc_type, limit=limit)
    return KnowledgeSearchResponse(results=results)
