JD_TEXT = (
    "Need FastAPI and SQLAlchemy backend engineer. PostgreSQL, API testing, "
    "and production service experience are required."
)
RESUME_TEXT = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems."
)


def test_analysis_flow_creates_report_and_agent_runs(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT},
    ).json()

    task_response = client.post(
        "/api/analysis", json={"job_id": job["id"], "resume_id": resume["id"]}
    )

    assert task_response.status_code == 201
    task = task_response.json()
    assert task["status"] == "success"

    report_response = client.get(f"/api/reports/{task['id']}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["final_score"] > 0
    assert report["next_best_action"]["title"]
    assert report["score_breakdown"]["skill_score"] > 0
    assert report["evidence"]

    runs_response = client.get(f"/api/agent-runs/{task['id']}")
    assert runs_response.status_code == 200
    runs = runs_response.json()
    assert len(runs) >= 4
    assert runs[0]["node_name"] == "jd_parser"
    assert runs[0]["input_snapshot"]["raw_jd"] == "[redacted]"
    assert JD_TEXT not in str(runs)
    assert RESUME_TEXT not in str(runs)
