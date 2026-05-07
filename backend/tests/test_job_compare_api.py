import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import JobDescription
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


def _seed_jobs(db_session):
    job1 = JobDescription(title="大模型应用开发工程师", raw_text="需要 FastAPI、Python、Docker 技能", profile={"skill_dimensions": [{"name": "FastAPI", "category": "backend", "required_level": "project_practice", "weight": 0.5}, {"name": "Python", "category": "programming", "required_level": "project_practice", "weight": 0.5}]})
    db_session.add(job1)
    job2 = JobDescription(title="数据分析师", raw_text="需要 SQL、数据可视化、统计方法", profile={"skill_dimensions": [{"name": "SQL", "category": "data_analysis", "required_level": "project_practice", "weight": 0.4}, {"name": "数据可视化", "category": "data_analysis", "required_level": "basic_usage", "weight": 0.3}, {"name": "统计方法", "category": "statistics", "required_level": "basic_usage", "weight": 0.3}]})
    db_session.add(job2)
    db_session.commit()
    return job1, job2


def test_compare_two_jobs(client):
    test_client, db_factory = client
    db = db_factory()
    job1, job2 = _seed_jobs(db)

    resp = test_client.post("/api/jobs/compare", json={"job_ids": [job1.id, job2.id]})

    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == "1"
    assert len(data["items"]) == 2
    assert data["items"][0]["job_id"] == job1.id
    assert data["items"][0]["job_title"] == "大模型应用开发工程师"
    assert len(data["items"][0]["dimensions"]) == 2
    assert data["items"][1]["job_id"] == job2.id
    assert len(data["items"][1]["dimensions"]) == 3


def test_compare_job_not_found(client):
    test_client, _ = client

    resp = test_client.post("/api/jobs/compare", json={"job_ids": [1, 999]})

    assert resp.status_code == 404


def test_compare_too_few_jobs(client):
    test_client, _ = client

    resp = test_client.post("/api/jobs/compare", json={"job_ids": [1]})

    assert resp.status_code == 422


def test_compare_too_many_jobs(client):
    test_client, _ = client

    resp = test_client.post("/api/jobs/compare", json={"job_ids": [1, 2, 3, 4, 5, 6]})

    assert resp.status_code == 422


def test_compare_dimension_structure(client):
    test_client, db_factory = client
    db = db_factory()
    job1, _ = _seed_jobs(db)
    job2 = JobDescription(title="后端开发", raw_text="需要 FastAPI", profile={"skill_dimensions": [{"name": "FastAPI", "category": "backend", "required_level": "project_practice", "weight": 1.0}]})
    db.add(job2)
    db.commit()

    resp = test_client.post("/api/jobs/compare", json={"job_ids": [job1.id, job2.id]})

    assert resp.status_code == 200
    dim = resp.json()["items"][1]["dimensions"][0]
    assert dim["name"] == "FastAPI"
    assert dim["category"] == "backend"
    assert dim["required_level"] == "project_practice"
    assert dim["weight"] == 1.0
