from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument
from app.rag.embedding import generate_embeddings

logger = logging.getLogger(__name__)

SEEDS_DIR = Path(__file__).resolve().parent.parent.parent / "seeds"


def load_seed_data(db: Session, seed_name: str) -> int:
    seed_path = SEEDS_DIR / f"{seed_name}.json"
    if not seed_path.exists():
        logger.warning("Seed file not found: %s", seed_path)
        return 0

    with open(seed_path, encoding="utf-8") as f:
        documents = json.load(f)

    if not documents:
        return 0

    existing = set(
        row[0] for row in db.query(KnowledgeDocument.title, KnowledgeDocument.doc_type).all()
        if row
    )
    existing_pairs = set(
        (row.title, row.doc_type)
        for row in db.query(KnowledgeDocument).all()
    )

    new_docs = []
    texts = []
    for doc_data in documents:
        title = doc_data.get("title", "")
        doc_type = doc_data.get("doc_type", "")
        if (title, doc_type) in existing_pairs:
            continue
        new_docs.append(doc_data)
        texts.append(doc_data.get("content", ""))

    if not new_docs:
        return 0

    embeddings = generate_embeddings(texts)

    imported = 0
    for doc_data, embedding in zip(new_docs, embeddings):
        metadata = doc_data.get("metadata", {})
        if "schema_version" not in metadata:
            metadata["schema_version"] = "1"
        metadata["source_type"] = "seed"

        doc = KnowledgeDocument(
            doc_type=doc_data["doc_type"],
            title=doc_data["title"],
            content=doc_data["content"],
            metadata_=metadata,
            embedding_json=embedding,
        )
        if hasattr(KnowledgeDocument, "embedding"):
            doc.embedding = embedding
        db.add(doc)
        imported += 1

    db.commit()
    logger.info("Imported %d documents from seed %s", imported, seed_name)
    return imported


def load_all_seeds(db: Session) -> int:
    total = 0
    for seed_name in ["backend_dev", "frontend_fullstack", "llm_app_dev", "data_analysis"]:
        total += load_seed_data(db, seed_name)
    return total
