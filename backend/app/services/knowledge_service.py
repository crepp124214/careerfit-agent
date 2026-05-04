from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument
from app.rag.embedding import generate_embeddings
from app.rag.retrieval import retrieve_by_skill
from app.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeSearchResult


def import_documents(
    db: Session, documents: list[KnowledgeDocumentCreate]
) -> tuple[int, int]:
    existing_pairs = set(
        (row.title, row.doc_type)
        for row in db.query(KnowledgeDocument).all()
    )

    new_docs: list[KnowledgeDocumentCreate] = []
    skipped = 0
    for doc in documents:
        if (doc.title, doc.doc_type) in existing_pairs:
            skipped += 1
            continue
        new_docs.append(doc)

    if not new_docs:
        return 0, skipped

    texts = [doc.content for doc in new_docs]
    embeddings = generate_embeddings(texts)

    imported = 0
    for doc_data, embedding in zip(new_docs, embeddings):
        metadata = dict(doc_data.metadata)
        if "schema_version" not in metadata:
            metadata["schema_version"] = "1"

        db_doc = KnowledgeDocument(
            doc_type=doc_data.doc_type,
            title=doc_data.title,
            content=doc_data.content,
            metadata_=metadata,
            embedding_json=embedding,
        )
        if hasattr(KnowledgeDocument, "embedding"):
            db_doc.embedding = embedding
        db.add(db_doc)
        imported += 1

    db.commit()
    return imported, skipped


def search_documents(
    db: Session,
    query: str,
    doc_type: str | None = None,
    limit: int = 5,
) -> list[KnowledgeSearchResult]:
    if not query.strip():
        return []

    raw_results = retrieve_by_skill(db, query, top_k=limit, doc_type=doc_type)
    return [
        KnowledgeSearchResult(
            id=r["doc_id"],
            doc_type=r["doc_type"],
            title=r["title"],
            content_snippet=r["content_snippet"],
            score=r["score"],
            metadata=r.get("metadata", {}),
        )
        for r in raw_results
    ]
