from app.agents.nodes import rag_retriever
from app.agents.state import CareerFitState


def test_rag_retriever_with_precomputed_results():
    state: CareerFitState = {
        "raw_jd": "Need FastAPI and Python",
        "raw_resume": "I know FastAPI",
        "jd_profile": {"required_skills": ["FastAPI", "Python"]},
        "rag_results": {
            "FastAPI": {
                "documents": [{"doc_id": 1, "title": "FastAPI 技能定义", "content_snippet": "...", "score": 0.9}],
                "available": True,
            },
            "Python": {
                "documents": [],
                "available": False,
                "reason": "知识库证据不足",
            },
        },
    }

    result = rag_retriever(state)

    assert "rag_results" in result
    assert result["rag_results"]["FastAPI"]["available"] is True
    assert result["rag_results"]["Python"]["available"] is False


def test_rag_retriever_without_precomputed_results():
    state: CareerFitState = {
        "raw_jd": "Need FastAPI and Python",
        "raw_resume": "I know FastAPI",
        "jd_profile": {"required_skills": ["FastAPI", "Python"]},
    }

    result = rag_retriever(state)

    assert "rag_results" in result
    assert "FastAPI" in result["rag_results"]
    assert result["rag_results"]["FastAPI"]["available"] is False
    assert result["rag_results"]["FastAPI"]["reason"] == "知识库证据不足"


def test_rag_retriever_empty_skills():
    state: CareerFitState = {
        "raw_jd": "Some JD",
        "raw_resume": "Some resume",
        "jd_profile": {"required_skills": []},
    }

    result = rag_retriever(state)

    assert result["rag_results"] == {}


def test_rag_retriever_no_jd_profile():
    state: CareerFitState = {
        "raw_jd": "Some JD",
        "raw_resume": "Some resume",
    }

    result = rag_retriever(state)

    assert result["rag_results"] == {}
