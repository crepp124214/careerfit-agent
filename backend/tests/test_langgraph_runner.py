from app.agents.graph import run_workflow
from app.agents.langgraph_runner import run_workflow_langgraph


MOCK_JD = """岗位：数据分析师
要求：熟练使用 SQL 进行数据提取
"""

MOCK_RESUME = """使用 Python 和 pandas 清洗 20 万行运营数据。"""


def test_langgraph_runner_returns_trace():
    state, trace = run_workflow_langgraph({
        "raw_jd": MOCK_JD,
        "raw_resume": MOCK_RESUME,
        "rag_results": {},
    })

    node_names = {t["node_name"] for t in trace}
    assert len(trace) > 0
    assert "next_best_action" in node_names
    assert "jd_parser" in node_names
    assert "match_scorer" in node_names
    assert all(t["status"] == "success" for t in trace)
    assert "final_score" in str(state.get("match_result", {}))


def test_langgraph_runner_collects_execution_meta():
    state, trace = run_workflow_langgraph({
        "raw_jd": MOCK_JD,
        "raw_resume": MOCK_RESUME,
        "rag_results": {},
    })

    for entry in trace:
        assert "execution_meta" in entry
        meta = entry["execution_meta"]
        assert "execution_mode" in meta
        if entry["status"] == "success":
            assert "summary" in meta
    assert len(trace) == 10


def test_langgraph_runner_redacts_sensitive_data_in_trace():
    state, trace = run_workflow_langgraph({
        "raw_jd": MOCK_JD,
        "raw_resume": MOCK_RESUME,
        "rag_results": {},
    })

    for entry in trace:
        inp = entry.get("input_snapshot", {})
        if "raw_jd" in inp:
            assert inp["raw_jd"] == "[redacted]"
        if "raw_resume" in inp:
            assert inp["raw_resume"] == "[redacted]"


def test_langgraph_runner_emits_events():
    events = []

    def on_event(event):
        events.append(event)

    run_workflow_langgraph(
        {"raw_jd": MOCK_JD, "raw_resume": MOCK_RESUME, "rag_results": {}},
        task_id=42,
        on_event=on_event,
    )

    event_types = {e["type"] for e in events}
    assert "workflow_completed" in event_types
    assert "node_started" in event_types
    assert "node_completed" in event_types
    assert all(e.get("task_id") == 42 for e in events)


def test_run_workflow_env_var_uses_langgraph_by_default(monkeypatch):
    monkeypatch.delenv("CAREERFIT_USE_LANGGRAPH", raising=False)

    state, trace = run_workflow({
        "raw_jd": MOCK_JD,
        "raw_resume": MOCK_RESUME,
        "rag_results": {},
    })

    node_names = {t["node_name"] for t in trace}
    assert len(trace) == 10
    assert "next_best_action" in node_names


def test_run_workflow_env_var_can_fallback_to_sequential(monkeypatch):
    monkeypatch.setenv("CAREERFIT_USE_LANGGRAPH", "0")

    state, trace = run_workflow({
        "raw_jd": MOCK_JD,
        "raw_resume": MOCK_RESUME,
        "rag_results": {},
    })

    assert len(trace) == 10
    assert trace[-1]["node_name"] == "next_best_action"
