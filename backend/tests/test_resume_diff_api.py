RESUME_TEXT_V1 = """Alex Chen
Backend Engineer

Experience:
- Built FastAPI backend services with SQLAlchemy and PostgreSQL
- Wrote API tests for internal systems
- 2 years of Python development"""

RESUME_TEXT_V2 = """Alex Chen
Backend Engineer

Experience:
- Built FastAPI backend services with SQLAlchemy and PostgreSQL
- Led a team of 3 engineers on microservices migration
- Wrote API tests for internal systems
- 3 years of Python development"""


def test_resume_diff_contract(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")

    assert response.status_code == 200
    data = response.json()
    assert "schema_version" in data
    assert data["schema_version"] == "1"
    assert "from_resume" in data
    assert "to_resume" in data
    assert "summary" in data
    assert "sections" in data
    assert "score_context" in data


def test_resume_diff_has_added_removed_unchanged(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")
    sections = response.json()["sections"]

    types = {s["type"] for s in sections}
    assert "unchanged" in types
    assert "added" in types


def test_resume_diff_summary_counts(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")
    summary = response.json()["summary"]

    assert "added_lines" in summary
    assert "removed_lines" in summary
    assert "unchanged_lines" in summary
    assert summary["added_lines"] >= 0
    assert summary["removed_lines"] >= 0
    assert summary["unchanged_lines"] >= 0


def test_resume_diff_not_found_returns_404(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id=99999")

    assert response.status_code == 404


def test_resume_diff_same_id_returns_400(client):
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume['id']}&to_id={resume['id']}")

    assert response.status_code == 400


def test_resume_diff_score_context_without_reports(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")
    score_context = response.json()["score_context"]

    assert score_context["available"] is False
    assert "reason" in score_context


def test_resume_diff_score_context_with_reports(client):
    job = client.post(
        "/api/jobs",
        json={"title": "Backend Engineer", "raw_text": "Need FastAPI and Python experience"},
    ).json()
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

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")
    score_context = response.json()["score_context"]

    assert score_context["available"] is True
    assert "from_score" in score_context
    assert "to_score" in score_context
    assert "from_report_created_at" in score_context
    assert "to_report_created_at" in score_context


def test_resume_diff_sections_have_line_numbers(client):
    resume1 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT_V1},
    ).json()
    resume2 = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v2", "raw_text": RESUME_TEXT_V2},
    ).json()

    response = client.get(f"/api/resumes/compare?from_id={resume1['id']}&to_id={resume2['id']}")
    sections = response.json()["sections"]

    for section in sections:
        assert "type" in section
        assert "text" in section
        if section["type"] == "removed":
            assert "old_line" in section
        elif section["type"] == "added":
            assert "new_line" in section
        else:
            assert "old_line" in section
            assert "new_line" in section
