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


def test_score_match_uses_skill_dimensions_and_resume_evidence_keys():
    jd_profile = {
        "skill_dimensions": [
            {
                "name": "SQL",
                "canonical_key": "sql",
                "category": "data_analysis",
                "weight": 0.5,
                "required_level": "project_practice",
                "jd_evidence": ["熟练 SQL"],
                "aliases": ["SQL"],
            },
            {
                "name": "数据可视化",
                "canonical_key": "data_visualization",
                "category": "data_analysis",
                "weight": 0.5,
                "required_level": "project_practice",
                "jd_evidence": ["使用 ECharts 做可视化"],
                "aliases": ["ECharts"],
            },
        ],
        "evidence": {},
    }
    resume_profile = {
        "skills": ["SQL"],
        "projects": ["使用 SQL 支持销售看板"],
        "evidence": {"sql": ["使用 SQL 支持销售看板"]},
    }

    result = score_match(jd_profile, resume_profile)

    assert len(result["score_items"]) == 2
    assert {item["skill_key"] for item in result["score_items"]} == {"sql", "data_visualization"}
    assert result["score_items"][0]["score"] > result["score_items"][1]["score"]
    assert 0 <= result["final_score"] <= 100
