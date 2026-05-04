import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import (
    AnalysisReport,
    AnalysisTask,
    AnalysisStatus,
    JobDescription,
    ResumeVersion,
)
from app.db.session import get_db
from app.main import create_app


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
        yield test_client, TestingSessionLocal


def _seed_report(db_session):
    job = JobDescription(title="大模型应用开发工程师", raw_text="Need FastAPI and Python")
    db_session.add(job)
    db_session.flush()
    resume = ResumeVersion(candidate_name="李明", version_label="v1", raw_text="I know FastAPI")
    db_session.add(resume)
    db_session.flush()
    task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.success)
    db_session.add(task)
    db_session.flush()
    report = AnalysisReport(
        task_id=task.id,
        final_score=55,
        score_breakdown={},
        interview_questions=[
            {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
            {"skill": "Python", "question": "什么是 Python GIL"},
        ],
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)
    return report


def test_create_interview_session(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})

    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["session"]["report_id"] == report.id
    assert data["session"]["total_questions"] == 2
    assert data["schema_version"] == "1"


def test_create_session_idempotent(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp1 = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})
    resp2 = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})

    assert resp1.json()["session"]["id"] == resp2.json()["session"]["id"]


def test_create_session_report_not_found(client):
    test_client, _ = client

    resp = test_client.post("/api/interview/sessions", json={"report_id": 9999, "include_rag": False})

    assert resp.status_code == 404


def test_list_interview_sessions(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)
    test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})

    resp = test_client.get("/api/interview/sessions")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1


def test_get_interview_session(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)
    create_resp = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})
    session_id = create_resp.json()["session"]["id"]

    resp = test_client.get(f"/api/interview/sessions/{session_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert len(data["questions"]) == 2
    assert data["questions"][0]["skill"] == "FastAPI"
    assert data["questions"][0]["category"] == "basic"


def test_get_session_not_found(client):
    test_client, _ = client

    resp = test_client.get("/api/interview/sessions/9999")

    assert resp.status_code == 404


def test_update_question_status(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)
    create_resp = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})
    session_id = create_resp.json()["session"]["id"]

    detail_resp = test_client.get(f"/api/interview/sessions/{session_id}")
    question_id = detail_resp.json()["questions"][0]["id"]

    resp = test_client.patch(
        f"/api/interview/sessions/{session_id}/questions/{question_id}",
        json={"status": "practicing"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "practicing"


def test_update_question_invalid_transition(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)
    create_resp = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})
    session_id = create_resp.json()["session"]["id"]

    detail_resp = test_client.get(f"/api/interview/sessions/{session_id}")
    question_id = detail_resp.json()["questions"][0]["id"]

    resp = test_client.patch(
        f"/api/interview/sessions/{session_id}/questions/{question_id}",
        json={"status": "completed"},
    )

    assert resp.status_code == 422


def test_update_question_notes(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)
    create_resp = test_client.post("/api/interview/sessions", json={"report_id": report.id, "include_rag": False})
    session_id = create_resp.json()["session"]["id"]

    detail_resp = test_client.get(f"/api/interview/sessions/{session_id}")
    question_id = detail_resp.json()["questions"][0]["id"]

    resp = test_client.patch(
        f"/api/interview/sessions/{session_id}/questions/{question_id}",
        json={"notes": "需要加强系统设计"},
    )

    assert resp.status_code == 200
    assert resp.json()["notes"] == "需要加强系统设计"


def test_capabilities_includes_interview(client):
    test_client, _ = client

    resp = test_client.get("/api/capabilities")

    data = resp.json()
    assert data["capabilities"]["interview"] == "ready"
