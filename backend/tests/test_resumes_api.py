VALID_RESUME = (
    "Candidate built FastAPI services with SQLAlchemy and PostgreSQL. "
    "They wrote API tests and maintained production backend systems."
)


def test_create_resume_extracts_skills(client):
    response = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": VALID_RESUME},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["candidate_name"] == "Alex Chen"
    assert "FastAPI" in data["profile"]["skills"]
    assert data["profile"]["schema_version"] == "resume-profile-v2"
    assert data["profile"]["evidence"]["fastapi"]


def test_create_resume_rejects_empty_text(client):
    response = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": ""},
    )

    assert response.status_code == 422


def test_list_and_get_resumes(client):
    created = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": VALID_RESUME},
    )
    resume_id = created.json()["id"]

    listing = client.get("/api/resumes")
    detail = client.get(f"/api/resumes/{resume_id}")

    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert detail.status_code == 200
    assert detail.json()["id"] == resume_id


def test_get_missing_resume_returns_404(client):
    response = client.get("/api/resumes/999")

    assert response.status_code == 404
