import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_jd_parse_preview_returns_structure(client):
    resp = client.post("/api/jobs/parse-preview", json={
        "content": "我们需要一名Python后端开发工程师，熟练掌握FastAPI和PostgreSQL，有Docker经验优先。本科及以上学历，3年以上开发经验。"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert "category" in data


def test_jd_parse_preview_rejects_short_content(client):
    resp = client.post("/api/jobs/parse-preview", json={"content": "short"})
    assert resp.status_code == 422


def test_resume_parse_preview_returns_structure(client):
    resp = client.post("/api/resumes/parse-preview", json={
        "content": "张三，本科毕业于北京大学计算机科学专业。3年后端开发经验，熟练使用Python、FastAPI、PostgreSQL、Docker。参与过电商平台后端架构设计，负责订单系统和支付模块开发。"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)


def test_resume_parse_preview_rejects_short_content(client):
    resp = client.post("/api/resumes/parse-preview", json={"content": "short"})
    assert resp.status_code == 422
