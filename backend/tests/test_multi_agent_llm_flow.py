import pytest
from app.llm.agent_schemas import JDParseOutput
from app.llm.agent_service import run_structured_agent


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)


def test_run_structured_agent_repairs_invalid_json_once():
    client = FakeClient([
        "不是 JSON",
        '{"job_family":"data_analysis","dimensions":[{"name":"SQL","canonical_key":"sql","category":"data_analysis","weight":0.5,"required_level":"project_practice","jd_evidence":["熟练 SQL"],"aliases":["SQL"]}],"evidence_summary":"需要 SQL"}',
    ])

    result, meta = run_structured_agent(
        client=client,
        agent_role="jd_parser_agent",
        prompt="parse jd",
        output_model=JDParseOutput,
    )

    assert result.job_family == "data_analysis"
    assert meta["agent_role"] == "jd_parser_agent"
    assert meta["execution_mode"] == "llm"
    assert meta["schema_valid"] is True
    assert meta["retry_count"] == 1
    assert len(client.calls) == 2


def test_run_structured_agent_uses_fallback_when_disabled():
    fallback_value = JDParseOutput(
        job_family="data_analysis",
        dimensions=[{
            "name": "SQL",
            "canonical_key": "sql",
            "category": "data_analysis",
            "weight": 1,
            "required_level": "project_practice",
            "jd_evidence": ["熟练 SQL"],
            "aliases": ["SQL"],
        }],
        evidence_summary="规则解析结果",
    )

    result, meta = run_structured_agent(
        client=None,
        agent_role="jd_parser_agent",
        prompt="parse jd",
        output_model=JDParseOutput,
        enabled=False,
        fallback=lambda: fallback_value,
    )

    assert result.job_family == "data_analysis"
    assert meta["execution_mode"] == "rule"
    assert meta["fallback_used"] is True
    assert meta["schema_valid"] is True


def test_run_structured_agent_marks_schema_invalid_after_repair_failure():
    client = FakeClient(["不是 JSON", "仍然不是 JSON"])

    with pytest.raises(Exception):
        run_structured_agent(
            client=client,
            agent_role="jd_parser_agent",
            prompt="parse jd",
            output_model=JDParseOutput,
        )

    assert len(client.calls) == 2
