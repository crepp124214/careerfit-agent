import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import KnowledgeDocument
from app.db.session import get_db
from app.main import create_app
from app.rag.embedding import generate_embedding


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


def test_import_knowledge_documents(client):
    payload = {
        "documents": [
            {
                "doc_type": "skill",
                "title": "TestSkill 技能定义",
                "content": "TestSkill 是一个测试技能",
                "metadata": {"schema_version": "1", "skill_name": "TestSkill"},
            }
        ]
    }
    resp = client.post("/api/knowledge/import", json=payload)

    assert resp.status_code == 201 or resp.status_code == 200
    data = resp.json()
    assert data["imported_count"] == 1
    assert data["skipped_count"] == 0
    assert data["schema_version"] == "1"


def test_import_duplicate_documents_idempotent(client):
    payload = {
        "documents": [
            {
                "doc_type": "skill",
                "title": "DuplicateSkill 技能定义",
                "content": "DuplicateSkill 是一个测试技能",
            }
        ]
    }
    client.post("/api/knowledge/import", json=payload)
    resp = client.post("/api/knowledge/import", json=payload)

    data = resp.json()
    assert data["skipped_count"] == 1


def test_search_knowledge(client):
    import_payload = {
        "documents": [
            {
                "doc_type": "skill",
                "title": "FastAPI 技能定义",
                "content": "FastAPI 是一个高性能 Python Web 框架",
            }
        ]
    }
    client.post("/api/knowledge/import", json=import_payload)

    resp = client.get("/api/knowledge/search", params={"q": "FastAPI"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == "1"
    assert len(data["results"]) >= 1
    assert "FastAPI" in data["results"][0]["title"]


def test_search_knowledge_with_doc_type_filter(client):
    import_payload = {
        "documents": [
            {
                "doc_type": "skill",
                "title": "FastAPI 技能定义",
                "content": "FastAPI 是一个高性能 Python Web 框架",
            },
            {
                "doc_type": "interview",
                "title": "FastAPI 面试题",
                "content": "FastAPI 相关面试问题",
            },
        ]
    }
    client.post("/api/knowledge/import", json=import_payload)

    resp = client.get("/api/knowledge/search", params={"q": "FastAPI", "doc_type": "skill"})

    data = resp.json()
    assert all(r["doc_type"] == "skill" for r in data["results"])


def test_search_knowledge_with_limit(client):
    import_payload = {
        "documents": [
            {
                "doc_type": "skill",
                "title": f"FastAPI 文档 {i}",
                "content": f"FastAPI 相关内容 {i}",
            }
            for i in range(5)
        ]
    }
    client.post("/api/knowledge/import", json=import_payload)

    resp = client.get("/api/knowledge/search", params={"q": "FastAPI", "limit": 2})

    data = resp.json()
    assert len(data["results"]) <= 2


def test_search_knowledge_empty_query(client):
    resp = client.get("/api/knowledge/search", params={"q": ""})

    data = resp.json()
    assert data["results"] == []


def test_capabilities_includes_knowledge(client):
    resp = client.get("/api/capabilities")

    data = resp.json()
    assert data["capabilities"]["knowledge"] == "ready"
