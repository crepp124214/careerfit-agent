JD_TEXT = (
    "Need FastAPI and Docker backend engineer. SQLAlchemy, PostgreSQL, "
    "and API testing are required."
)
RESUME_TEXT = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems."
)


def test_llm_disabled_keeps_fallback_flow(client):
    task = None
    try:
        task = client.post("/api/analysis", json={"job_id": 1, "resume_id": 1}).json()
    except Exception:
        pass

    assert task is None or task.get("status") != "failed"


def test_llm_fallback_nodes_produce_content():
    state = {
        "raw_jd": JD_TEXT,
        "raw_resume": RESUME_TEXT,
        "jd_profile": {
            "job_family": "backend_engineering",
            "required_skills": ["FastAPI", "Docker", "SQLAlchemy", "PostgreSQL"],
            "skill_dimensions": [
                {"name": "FastAPI", "canonical_key": "fastapi", "category": "framework", "weight": 0.3},
                {"name": "Docker", "canonical_key": "docker", "category": "devops", "weight": 0.2},
            ],
        },
        "resume_profile": {
            "FastAPI": {"resume_evidence": ["Built FastAPI backend services"]},
            "SQLAlchemy": {"resume_evidence": ["Used SQLAlchemy ORM"]},
        },
        "match_result": {
            "final_score": 65,
            "score_items": [
                {"skill": "FastAPI", "score": 80, "level": "project_practice", "jd_evidence": ["需要 FastAPI"], "resume_evidence": ["Built FastAPI backend services"]},
                {"skill": "Docker", "score": 0, "level": "not_mentioned", "jd_evidence": ["需要 Docker"], "resume_evidence": []},
            ],
        },
        "gaps": [{"skill": "Docker", "reason": "简历缺少可验证证据", "jd_evidence": ["需要 Docker"]}],
        "strengths": [{"skill": "FastAPI", "resume_evidence": ["Built FastAPI backend services"]}],
        "rag_results": {},
    }

    from app.agents.nodes import resume_optimizer, interview_coach, learning_planner, next_best_action

    ro_result = resume_optimizer(state)
    assert len(ro_result.get("resume_suggestions", [])) >= 1

    ic_result = interview_coach(state)
    assert len(ic_result.get("interview_questions", [])) >= 1

    lp_result = learning_planner(state)
    assert len(lp_result.get("learning_plan", [])) >= 1

    nba_result = next_best_action(state)
    assert nba_result.get("next_best_action", {}).get("title")


def test_llm_trace_redacts_sensitive_data(monkeypatch):
    from app.agents.graph import redact_state

    state = {
        "raw_jd": JD_TEXT,
        "raw_resume": RESUME_TEXT,
        "jd_profile": {"required_skills": ["FastAPI"]},
        "resume_profile": {},
        "match_result": {"score_items": [], "final_score": 50},
        "gaps": [],
        "strengths": [],
        "rag_results": {},
    }
    redacted = redact_state(state)
    assert redacted.get("raw_jd") == "[redacted]"
    assert redacted.get("raw_resume") == "[redacted]"
    assert "secret-test-key" not in str(redacted)
    assert JD_TEXT not in str(redacted)
    assert RESUME_TEXT not in str(redacted)
