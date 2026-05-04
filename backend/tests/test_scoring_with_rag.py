from app.scoring.rules import score_match


def test_score_match_with_rag_results_adds_knowledge_evidence():
    jd_profile = {
        "required_skills": ["FastAPI"],
        "evidence": {"FastAPI": ["Need FastAPI experience"]},
    }
    resume_profile = {
        "skills": ["FastAPI"],
        "projects": ["Built FastAPI services"],
        "evidence": {"FastAPI": ["Built FastAPI services"]},
    }
    rag_results = {
        "FastAPI": {
            "documents": [
                {"doc_id": 1, "title": "FastAPI 技能定义", "content_snippet": "项目实践级别要求能独立设计 API 端点", "score": 0.9}
            ],
            "available": True,
        }
    }

    result = score_match(jd_profile, resume_profile, rag_results=rag_results)

    assert len(result["score_items"]) == 1
    item = result["score_items"][0]
    assert "knowledge_evidence" in item
    assert len(item["knowledge_evidence"]) == 1
    assert item["knowledge_evidence"][0]["available"] is True
    assert item["knowledge_evidence"][0]["doc_id"] == 1
    assert item["knowledge_evidence"][0]["title"] == "FastAPI 技能定义"


def test_score_match_with_rag_unavailable_marks_insufficient():
    jd_profile = {
        "required_skills": ["UnknownSkill"],
        "evidence": {"UnknownSkill": ["Need UnknownSkill"]},
    }
    resume_profile = {
        "skills": [],
        "projects": [],
        "evidence": {},
    }
    rag_results = {
        "UnknownSkill": {
            "documents": [],
            "available": False,
            "reason": "知识库证据不足",
        }
    }

    result = score_match(jd_profile, resume_profile, rag_results=rag_results)

    item = result["score_items"][0]
    assert len(item["knowledge_evidence"]) == 1
    assert item["knowledge_evidence"][0]["available"] is False
    assert item["knowledge_evidence"][0]["reason"] == "知识库证据不足"


def test_score_match_without_rag_results_has_empty_knowledge_evidence():
    jd_profile = {
        "required_skills": ["FastAPI"],
        "evidence": {"FastAPI": ["Need FastAPI"]},
    }
    resume_profile = {
        "skills": ["FastAPI"],
        "projects": ["Built FastAPI services"],
        "evidence": {"FastAPI": ["Built FastAPI services"]},
    }

    result = score_match(jd_profile, resume_profile)

    item = result["score_items"][0]
    assert item["knowledge_evidence"] == []


def test_score_match_rag_does_not_change_score():
    jd_profile = {
        "required_skills": ["FastAPI"],
        "evidence": {"FastAPI": ["Need FastAPI"]},
    }
    resume_profile = {
        "skills": ["FastAPI"],
        "projects": ["Built FastAPI services"],
        "evidence": {"FastAPI": ["Built FastAPI services"]},
    }

    result_without_rag = score_match(jd_profile, resume_profile)
    rag_results = {
        "FastAPI": {
            "documents": [{"doc_id": 1, "title": "FastAPI 技能定义", "content_snippet": "...", "score": 0.9}],
            "available": True,
        }
    }
    result_with_rag = score_match(jd_profile, resume_profile, rag_results=rag_results)

    assert result_without_rag["final_score"] == result_with_rag["final_score"]
