import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import KnowledgeDocument
from app.rag.embedding import generate_embedding, generate_embeddings, EMBEDDING_DIMENSION
from app.rag.retrieval import retrieve_by_skill


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_generate_embedding_returns_correct_dimension():
    vec = generate_embedding("FastAPI")
    assert len(vec) == EMBEDDING_DIMENSION
    assert all(isinstance(v, float) for v in vec)


def test_generate_embeddings_returns_multiple_vectors():
    vecs = generate_embeddings(["FastAPI", "Python"])
    assert len(vecs) == 2
    assert all(len(v) == EMBEDDING_DIMENSION for v in vecs)


def test_generate_embedding_empty_string_returns_zero_vector():
    vec = generate_embedding("")
    assert len(vec) == EMBEDDING_DIMENSION
    assert all(v == 0.0 for v in vec)


def _insert_test_doc(db, title, content, doc_type="skill", skill_name=None):
    metadata = {"schema_version": "1", "source_type": "test"}
    if skill_name:
        metadata["skill_name"] = skill_name
    doc = KnowledgeDocument(
        doc_type=doc_type,
        title=title,
        content=content,
        metadata_=metadata,
        embedding_json=generate_embedding(content),
    )
    db.add(doc)
    db.commit()
    return doc


def test_retrieve_by_skill_returns_results(db):
    _insert_test_doc(db, "FastAPI 技能定义", "FastAPI 是一个高性能 Python Web 框架", "skill", "FastAPI")
    _insert_test_doc(db, "Docker 技能定义", "Docker 是容器化平台", "skill", "Docker")

    results = retrieve_by_skill(db, "FastAPI", top_k=3)

    assert len(results) >= 1
    assert results[0]["doc_type"] == "skill"
    assert "FastAPI" in results[0]["title"]
    assert results[0]["score"] > 0


def test_retrieve_by_skill_no_match_returns_empty(db):
    _insert_test_doc(db, "FastAPI 技能定义", "FastAPI 是一个高性能 Python Web 框架", "skill", "FastAPI")

    results = retrieve_by_skill(db, "QuantumComputing", top_k=3)

    assert len(results) == 0 or all(r["score"] < 0.3 for r in results)


def test_retrieve_by_skill_doc_type_filter(db):
    _insert_test_doc(db, "FastAPI 技能定义", "FastAPI 是一个高性能 Python Web 框架", "skill", "FastAPI")
    _insert_test_doc(db, "后端面试题", "FastAPI 相关面试题", "interview", "FastAPI")

    results = retrieve_by_skill(db, "FastAPI", top_k=3, doc_type="skill")

    assert all(r["doc_type"] == "skill" for r in results)


def test_retrieve_by_skill_top_k_limit(db):
    for i in range(5):
        _insert_test_doc(db, f"FastAPI 文档 {i}", f"FastAPI 相关内容 {i}", "skill", "FastAPI")

    results = retrieve_by_skill(db, "FastAPI", top_k=2)

    assert len(results) <= 2
