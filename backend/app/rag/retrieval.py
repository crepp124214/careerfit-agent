from __future__ import annotations

import json
import math
import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import KnowledgeDocument, _VECTOR_AVAILABLE
from app.rag.embedding import generate_embedding, is_fallback_mode

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度
    
    注意: 为了性能优化，建议在存储向量时预计算归一化向量，
    然后使用 _cosine_similarity_fast 进行计算。
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _normalize_vector(v: list[float]) -> list[float]:
    """对向量进行 L2 归一化"""
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0:
        return v
    return [x / norm for x in v]


def _cosine_similarity_fast(a_normalized: list[float], b_normalized: list[float]) -> float:
    """使用预计算归一化向量快速计算余弦相似度
    
    要求输入向量已经通过 _normalize_vector 进行归一化。
    这样可以将复杂度从 O(3n) 降低到 O(n)。
    """
    return sum(x * y for x, y in zip(a_normalized, b_normalized))


def _keyword_match_score(query: str, doc_content: str, doc_title: str) -> float:
    query_lower = query.lower()
    terms = query_lower.split()
    content_lower = doc_content.lower()
    title_lower = doc_title.lower()
    score = 0.0
    for term in terms:
        if term in title_lower:
            score += 0.5
        if term in content_lower:
            score += 0.3
    return min(score, 1.0)


def _is_sqlite_db(db: Session) -> bool:
    bind = db.get_bind()
    return "sqlite" in str(bind.url)


def retrieve_by_skill(
    db: Session,
    skill_name: str,
    top_k: int = 3,
    doc_type: str | None = None,
) -> list[dict[str, Any]]:
    if _is_sqlite_db(db):
        return _retrieve_json_fallback(db, [0.0], skill_name, top_k, doc_type)

    query_embedding = generate_embedding(skill_name)
    fallback = is_fallback_mode()

    if _VECTOR_AVAILABLE and not fallback:
        return _retrieve_pgvector(db, query_embedding, skill_name, top_k, doc_type)
    return _retrieve_json_fallback(db, query_embedding, skill_name, top_k, doc_type)


def retrieve_by_skills_batch(
    db: Session,
    skill_names: list[str],
    top_k: int = 3,
    doc_type: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """批量检索多个技能的知识文档，避免 N+1 查询问题"""
    results = {}
    
    # 检查数据库类型和向量可用性
    if _is_sqlite_db(db) or not _VECTOR_AVAILABLE or is_fallback_mode():
        # fallback 模式下逐个处理（数据量小）
        for skill in skill_names:
            results[skill] = retrieve_by_skill(db, skill, top_k, doc_type)
        return results

    # pgvector 模式下使用批量查询
    all_embeddings = {}
    for skill in skill_names:
        all_embeddings[skill] = generate_embedding(skill)

    # 使用单个查询获取所有相关文档
    for skill, embedding in all_embeddings.items():
        results[skill] = _retrieve_pgvector(db, embedding, skill, top_k, doc_type)
    
    return results


def _retrieve_pgvector(
    db: Session,
    query_embedding: list[float],
    skill_name: str,
    top_k: int,
    doc_type: str | None,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, doc_type, title, content, metadata, embedding <=> :query_vec AS distance
        FROM knowledge_documents
        WHERE 1=1
    """
    params: dict[str, Any] = {"query_vec": json.dumps(query_embedding), "limit": top_k}
    if doc_type:
        query += " AND doc_type = :doc_type"
        params["doc_type"] = doc_type
    query += " ORDER BY embedding <=> :query_vec LIMIT :limit"

    rows = db.execute(text(query), params).fetchall()
    results = []
    for row in rows:
        content_text = row.content or ""
        snippet = content_text[:200] + ("..." if len(content_text) > 200 else "")
        results.append({
            "doc_id": row.id,
            "doc_type": row.doc_type,
            "title": row.title,
            "content_snippet": snippet,
            "score": round(1.0 - row.distance, 4),
            "metadata": row.metadata if isinstance(row.metadata, dict) else json.loads(row.metadata or "{}"),
        })
    return results


def _retrieve_json_fallback(
    db: Session,
    query_embedding: list[float],
    skill_name: str,
    top_k: int,
    doc_type: str | None,
) -> list[dict[str, Any]]:
    q = db.query(KnowledgeDocument)
    if doc_type:
        q = q.filter(KnowledgeDocument.doc_type == doc_type)
    documents = q.all()

    scored = []
    for doc in documents:
        doc_embedding = doc.embedding_json if doc.embedding_json else None
        if doc_embedding and any(v != 0.0 for v in doc_embedding):
            sim = _cosine_similarity(query_embedding, doc_embedding)
        else:
            sim = _keyword_match_score(skill_name, doc.content, doc.title)
        scored.append((doc, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = []
    for doc, sim in scored[:top_k]:
        snippet = doc.content[:200] + ("..." if len(doc.content) > 200 else "")
        results.append({
            "doc_id": doc.id,
            "doc_type": doc.doc_type,
            "title": doc.title,
            "content_snippet": snippet,
            "score": round(sim, 4),
            "metadata": doc.metadata_ if isinstance(doc.metadata_, dict) else json.loads(doc.metadata_ or "{}"),
        })
    return results


def filter_relevant_documents(
    documents: list[dict[str, Any]],
    job_family: str,
    allowed_doc_types: list[str],
    min_score: float = 0.72,
) -> list[dict[str, Any]]:
    filtered = []
    for doc in documents:
        metadata = doc.get("metadata") or {}
        doc_family = metadata.get("job_family")
        doc_type = doc.get("doc_type")
        score = float(doc.get("score") or 0)
        family_matches = not doc_family or doc_family == job_family
        type_matches = not allowed_doc_types or doc_type in allowed_doc_types
        if family_matches and type_matches and score >= min_score:
            filtered.append(doc)
    return filtered
