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
from app.services.export_service import generate_markdown_report


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
        score_breakdown={"skill_score": 77, "project_score": 57, "domain_score": 0, "basic_requirement_score": 60, "expression_score": 80, "integrity_risk_penalty": 0},
        strengths=[{"skill": "FastAPI", "resume_evidence": ["Built FastAPI services"]}],
        gaps=[{"skill": "RAG", "reason": "No RAG experience"}],
        resume_suggestions=[{"original": "Built API", "optimized": "Designed and implemented RESTful API", "risk_level": "low"}],
        interview_questions=[{"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"}],
        learning_plan=[{"skill": "RAG", "task": "Build a RAG system"}],
        next_best_action={"action": "Add RAG project", "reason": "RAG is required"},
        evidence=[{"skill": "FastAPI", "score": 80, "jd_evidence": ["Need FastAPI"], "resume_evidence": ["Built FastAPI"], "knowledge_evidence": [{"available": True, "title": "FastAPI 技能定义"}]}],
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)
    return report


def test_export_markdown(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp = test_client.get(f"/api/reports/{report.task_id}/export?format=markdown")

    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    content = resp.text
    assert "大模型应用开发工程师" in content
    assert "55" in content
    assert "FastAPI" in content


def test_export_markdown_content_completeness(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp = test_client.get(f"/api/reports/{report.task_id}/export?format=markdown")
    content = resp.text

    assert "评分详情" in content
    assert "技能评分" in content
    assert "优势" in content
    assert "缺口" in content
    assert "简历优化建议" in content
    assert "面试题" in content
    assert "学习任务" in content
    assert "下一步建议" in content


def test_export_pdf(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp = test_client.get(f"/api/reports/{report.task_id}/export?format=pdf")

    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "大模型应用开发工程师" in resp.text


def test_export_not_found(client):
    test_client, _ = client

    resp = test_client.get("/api/reports/9999/export?format=markdown")

    assert resp.status_code == 404


def test_export_unsupported_format(client):
    test_client, db_factory = client
    db = db_factory()
    report = _seed_report(db)

    resp = test_client.get(f"/api/reports/{report.task_id}/export?format=docx")

    assert resp.status_code == 422


def test_generate_markdown_no_pii():
    job = JobDescription(title="Test", raw_text="Secret JD content with PII: john@example.com")
    resume = ResumeVersion(candidate_name="Test", version_label="v1", raw_text="Secret resume with SSN: 123-45-6789")
    report = AnalysisReport(
        task_id=1,
        final_score=50,
        score_breakdown={},
        evidence=[],
    )
    md = generate_markdown_report(report, job, resume)

    assert "Secret JD content" not in md
    assert "Secret resume with SSN" not in md
    assert "john@example.com" not in md
    assert "123-45-6789" not in md
