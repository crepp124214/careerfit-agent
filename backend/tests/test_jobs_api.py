VALID_JD = (
    "We need a backend engineer with FastAPI, SQLAlchemy, PostgreSQL, "
    "API testing, and production service experience."
)


def test_create_job_extracts_skills(client):
    response = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": VALID_JD})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Backend Engineer"
    assert "FastAPI" in data["profile"]["required_skills"]
    assert data["profile"]["schema_version"] == "job-profile-v1"
    assert data["profile"]["evidence"]["FastAPI"]


def test_create_job_rejects_empty_jd(client):
    response = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": ""})

    assert response.status_code == 422


def test_list_and_get_jobs(client):
    created = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": VALID_JD})
    job_id = created.json()["id"]

    listing = client.get("/api/jobs")
    detail = client.get(f"/api/jobs/{job_id}")

    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert detail.status_code == 200
    assert detail.json()["id"] == job_id


def test_get_missing_job_returns_404(client):
    response = client.get("/api/jobs/999")

    assert response.status_code == 404
