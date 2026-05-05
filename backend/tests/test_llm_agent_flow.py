JD_TEXT = (
    "Need FastAPI and Docker backend engineer. SQLAlchemy, PostgreSQL, "
    "and API testing are required."
)
RESUME_TEXT = (
    "Built FastAPI backend services with SQLAlchemy and PostgreSQL. "
    "Wrote API tests for internal systems."
)


def create_analysis(client):
    job = client.post("/api/jobs", json={"title": "Backend Engineer", "raw_text": JD_TEXT}).json()
    resume = client.post(
        "/api/resumes",
        json={"candidate_name": "Alex Chen", "version_label": "v1", "raw_text": RESUME_TEXT},
    ).json()
    return client.post("/api/analysis", json={"job_id": job["id"], "resume_id": resume["id"]}).json()


def test_llm_disabled_keeps_fallback_flow(client):
    task = create_analysis(client)

    report = client.get(f"/api/reports/{task['id']}").json()

    assert task["status"] == "success"
    assert report["final_score"] > 0
    assert report["resume_suggestions"]
    assert report["interview_questions"]
    assert report["learning_plan"]


def test_llm_enabled_uses_mock_enhancement(client, monkeypatch):
    from app.llm.schemas import LLMReportEnhancement

    def fake_enhancement(state):
        return (
            LLMReportEnhancement.model_validate(
                {
                    "resume_suggestions": [
                        {
                            "title": "LLM 强化 FastAPI 表达",
                            "suggestion": "保留已有 FastAPI 事实，补清楚项目边界。",
                            "jd_requirement": "需要 FastAPI",
                            "resume_evidence": "Built FastAPI backend services",
                            "risk_level": "low",
                        }
                    ],
                    "interview_questions": [
                        {"skill": "FastAPI", "question": "LLM 问题：你如何设计 FastAPI 接口？"}
                    ],
                    "learning_plan": [{"skill": "Docker", "task": "LLM 任务：完成 Docker 化练习。"}],
                    "next_best_action": {
                        "title": "LLM 下一步：补齐 Docker 证据",
                        "description": "先做一个可运行 Docker 项目。",
                        "target_skill": "Docker",
                    },
                }
            ),
            "test-model",
        )

    monkeypatch.setattr("app.agents.nodes.generate_report_enhancement", fake_enhancement)

    task = create_analysis(client)
    report = client.get(f"/api/reports/{task['id']}").json()

    assert report["resume_suggestions"][0]["title"] == "LLM 强化 FastAPI 表达"
    assert report["interview_questions"][0]["question"].startswith("LLM 问题")
    assert report["learning_plan"][0]["task"].startswith("LLM 任务")
    assert report["next_best_action"]["title"].startswith("LLM 下一步")
    assert report["score_breakdown"]["skill_score"] > 0


def test_llm_failure_falls_back_to_local_generation(client, monkeypatch):
    def fail_enhancement(state):
        raise RuntimeError("provider down")

    monkeypatch.setattr("app.agents.nodes.generate_report_enhancement", fail_enhancement)

    task = create_analysis(client)
    report = client.get(f"/api/reports/{task['id']}").json()

    assert task["status"] == "success"
    assert report["resume_suggestions"]
    assert not report["resume_suggestions"][0]["title"].startswith("LLM")


def test_llm_trace_does_not_expose_key_prompt_or_raw_text(client, monkeypatch):
    from app.llm.schemas import LLMReportEnhancement

    monkeypatch.setenv("CAREERFIT_LLM_API_KEY", "secret-test-key")

    def fake_enhancement(state):
        return (
            LLMReportEnhancement.model_validate(
                {
                    "resume_suggestions": [],
                    "interview_questions": [],
                    "learning_plan": [],
                    "next_best_action": {"title": "LLM 下一步", "description": "继续"},
                }
            ),
            "test-model",
        )

    monkeypatch.setattr("app.agents.nodes.generate_report_enhancement", fake_enhancement)

    task = create_analysis(client)
    runs = client.get(f"/api/agent-runs/{task['id']}").json()
    rendered = str(runs)

    assert "secret-test-key" not in rendered
    assert "messages" not in rendered
    assert "prompt" not in rendered
    assert JD_TEXT not in rendered
    assert RESUME_TEXT not in rendered
