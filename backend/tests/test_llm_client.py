import json

import httpx
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_llm_capability_defaults_to_unavailable():
    get_settings.cache_clear()

    settings = get_settings()
    client = TestClient(create_app())

    assert settings.llm_enabled is False
    assert client.get("/api/capabilities").json()["capabilities"]["llm"] == "unavailable"


def test_llm_capability_ready_when_required_config_is_present(monkeypatch):
    monkeypatch.setenv("CAREERFIT_LLM_ENABLED", "true")
    monkeypatch.setenv("CAREERFIT_LLM_API_KEY", "test-key")
    monkeypatch.setenv("CAREERFIT_LLM_MODEL", "test-model")
    get_settings.cache_clear()

    client = TestClient(create_app())

    assert client.get("/api/capabilities").json()["capabilities"]["llm"] == "ready"


def test_chat_completions_request_shape(monkeypatch):
    from app.llm.client import LLMClient

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers.get("authorization")
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    client = LLMClient(
        base_url="https://api.example.com/v1",
        api_key="secret",
        model="model-a",
        api_style="chat_completions",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.complete("请输出 JSON")

    assert captured["url"] == "https://api.example.com/v1/chat/completions"
    assert captured["authorization"] == "Bearer secret"
    assert captured["body"]["model"] == "model-a"
    assert captured["body"]["messages"][0]["content"] == "请输出 JSON"


def test_responses_request_shape():
    from app.llm.client import LLMClient

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers.get("authorization")
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"output_text": "{}"})

    client = LLMClient(
        base_url="https://api.example.com/v1",
        api_key="secret",
        model="model-a",
        api_style="responses",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.complete("请输出 JSON")

    assert captured["url"] == "https://api.example.com/v1/responses"
    assert captured["authorization"] == "Bearer secret"
    assert captured["body"] == {"model": "model-a", "input": "请输出 JSON"}


def test_parse_valid_llm_json():
    from app.llm.schemas import parse_llm_enhancement

    payload = {
        "resume_suggestions": [
            {
                "title": "强化 FastAPI 表达",
                "suggestion": "突出已有 FastAPI 项目，不新增事实。",
                "jd_requirement": "需要 FastAPI",
                "resume_evidence": "Built FastAPI backend services",
                "risk_level": "low",
            }
        ],
        "interview_questions": [{"skill": "FastAPI", "question": "请说明一次 FastAPI 实践。"}],
        "learning_plan": [{"skill": "Docker", "task": "完成 Docker 化练习。"}],
        "next_best_action": {
            "title": "补齐 Docker 证据",
            "description": "先补充可验证项目。",
            "target_skill": "Docker",
        },
    }

    enhancement = parse_llm_enhancement(json.dumps(payload, ensure_ascii=False))

    assert enhancement.resume_suggestions[0].title == "强化 FastAPI 表达"
    assert enhancement.next_best_action.title == "补齐 Docker 证据"


def test_generate_enhancement_retries_once_for_invalid_json(monkeypatch):
    from app.llm.schemas import LLMReportEnhancement
    from app.llm.service import generate_report_enhancement

    calls = []
    valid_payload = json.dumps(
        {
            "resume_suggestions": [],
            "interview_questions": [],
            "learning_plan": [],
            "next_best_action": {"title": "下一步", "description": "继续迭代"},
        },
        ensure_ascii=False,
    )

    class FakeClient:
        def complete(self, prompt: str) -> str:
            calls.append(prompt)
            return "not json" if len(calls) == 1 else valid_payload

    monkeypatch.setattr("app.llm.service.build_llm_client", lambda settings: FakeClient())
    monkeypatch.setenv("CAREERFIT_LLM_CONCURRENT_ENABLED", "false")

    from app.core.config import get_settings
    get_settings.cache_clear()

    enhancement, model_name = generate_report_enhancement(
        {
            "strengths": [],
            "gaps": [],
            "match_result": {"score_items": []},
        },
        enabled=True,
    )

    assert isinstance(enhancement, LLMReportEnhancement)
    assert model_name is not None
    assert len(calls) == 2
