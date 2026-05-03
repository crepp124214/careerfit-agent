from app.scoring.rules import score_match


def test_score_match_returns_bounded_score_with_evidence():
    jd_profile = {
        "required_skills": ["FastAPI", "SQLAlchemy"],
        "evidence": {
            "FastAPI": ["Need FastAPI backend services."],
            "SQLAlchemy": ["Use SQLAlchemy for persistence."],
        },
        "domain_keywords": ["backend"],
        "basic_requirements": ["testing"],
    }
    resume_profile = {
        "skills": ["FastAPI"],
        "projects": ["Built FastAPI services with API tests"],
        "evidence": {"FastAPI": ["Built FastAPI services with API tests"]},
        "domain_keywords": ["backend"],
    }

    result = score_match(jd_profile, resume_profile)

    assert 0 <= result["final_score"] <= 100
    assert result["score_breakdown"]["skill_score"] > 0
    assert {item["skill"] for item in result["score_items"]} == {"FastAPI", "SQLAlchemy"}
    assert all(item["jd_evidence"] for item in result["score_items"])


def test_score_match_empty_input_scores_zero():
    result = score_match({}, {})

    assert result["final_score"] == 0
    assert result["score_breakdown"]["skill_score"] == 0
