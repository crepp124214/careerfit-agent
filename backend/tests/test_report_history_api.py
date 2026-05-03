JD_TEXT = (
    "Need FastAPI and SQLAlchemy backend engineer. PostgreSQL, API testing, "
    "and production service experience are required."
)
RESUME_TEXT_V1 = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems."
)
RESUME_TEXT_V2 = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems. Led a team of 3 engineers."
)


def test_report_history_contract(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    task1 = client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume1["id"]}).json()
    task2 = client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume2["id"]}).json()

    response = client.get("/api/reports/history")

    assert response.status_code == 200
    data = response.json()
    assert "schema_version" in data
    assert data["schema_version"] == "1"
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 2

    item = data["items"][0]
    assert "task_id" in item
    assert "report_id" in item
    assert "job_id" in item
    assert "job_title" in item
    assert "resume_id" in item
    assert "resume_label" in item
    assert "final_score" in item
    assert "score_breakdown" in item
    assert "gap_count" in item
    assert "created_at" in item


def test_report_history_ordered_by_created_at_desc(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume1["id"]}).json()
    client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume2["id"]}).json()

    response = client.get("/api/reports/history")
    items = response.json()["items"]

    assert len(items) >= 2
    from datetime import datetime

    dates = [datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) for i in items]
    assert dates == sorted(dates, reverse=True)


def test_report_history_filter_by_job_id(client):
    job1 = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    job2 = client.post("/api/jobs", json={"title": "Frontend Engineer", "raw_text": "Need React and TypeScript"}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()

    client.post("/api/analysis", json={"job_id": job1["id"], "resume_id": resume["id"]}).json()
    client.post("/api/analysis", json={"job_id": job2["id"], "resume_id": resume["id"]}).json()

    response = client.get(f"/api/reports/history?job_id={job1['id']}")
    items = response.json()["items"]

    assert all(i["job_id"] == job1["id"] for i in items)


def test_report_history_filter_by_resume_id(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume1["id"]}).json()
    client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume2["id"]}).json()

    response = client.get(f"/api/reports/history?resume_id={resume1['id']}")
    items = response.json()["items"]

    assert all(i["resume_id"] == resume1["id"] for i in items)


def test_report_history_limit(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()

    for _ in range(5):
        client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume["id"]}).json()

    response = client.get("/api/reports/history?limit=3")
    items = response.json()["items"]

    assert len(items) == 3


def test_report_history_empty_when_no_reports(client):
    response = client.get("/api/reports/history")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


def test_report_history_includes_high_risk_count(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()

    client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume["id"]}).json()

    response = client.get("/api/reports/history")
    items = response.json()["items"]

    assert len(items) >= 1
    assert "high_risk_suggestion_count" in items[0]
