from app.scoring.evidence import find_resume_evidence
from app.scoring.rubric import LEVEL_WEIGHTS, clamp_score


SCORING_VERSION = "deterministic-v1"


def _score_skill(skill: str, resume_profile: dict) -> tuple[str, float, list[str]]:
    evidence = find_resume_evidence(skill, resume_profile)
    if not evidence:
        return "not_mentioned", LEVEL_WEIGHTS["not_mentioned"], []
    joined = " ".join(evidence).lower()
    if any(term in joined for term in ["scale", "production", "生产", "性能", "架构"]):
        return "deep_experience", LEVEL_WEIGHTS["deep_experience"], evidence
    if any(term in joined for term in ["built", "project", "项目", "服务", "system"]):
        return "project_practice", LEVEL_WEIGHTS["project_practice"], evidence
    return "mentioned", LEVEL_WEIGHTS["mentioned"], evidence


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def score_match(jd_profile: dict, resume_profile: dict) -> dict:
    required_skills = jd_profile.get("required_skills") or []
    if not required_skills:
        return {
            "scoring_version": SCORING_VERSION,
            "final_score": 0,
            "score_breakdown": {
                "skill_score": 0,
                "project_score": 0,
                "domain_score": 0,
                "basic_requirement_score": 0,
                "expression_score": 0,
                "integrity_risk_penalty": 0,
            },
            "score_items": [],
        }

    score_items = []
    skill_weights = []
    for skill in required_skills:
        level, weight, resume_evidence = _score_skill(skill, resume_profile)
        skill_weights.append(weight)
        score_items.append(
            {
                "skill": skill,
                "level": level,
                "score": clamp_score(weight * 100),
                "jd_evidence": (jd_profile.get("evidence") or {}).get(skill, []),
                "resume_evidence": resume_evidence,
            }
        )

    skill_score = _average(skill_weights) * 100
    project_score = 100 if resume_profile.get("projects") else max(0, skill_score - 20)
    jd_domains = set(jd_profile.get("domain_keywords") or [])
    resume_domains = set(resume_profile.get("domain_keywords") or [])
    domain_score = 100 if jd_domains and jd_domains <= resume_domains else (50 if jd_domains & resume_domains else 0)
    basic_requirement_score = 100 if jd_profile.get("basic_requirements") else 60
    expression_score = 80 if resume_profile.get("skills") else 0
    integrity_risk_penalty = 0

    final_score = clamp_score(
        skill_score * 0.35
        + project_score * 0.25
        + domain_score * 0.15
        + basic_requirement_score * 0.10
        + expression_score * 0.10
        - integrity_risk_penalty * 0.05
    )

    return {
        "scoring_version": SCORING_VERSION,
        "final_score": final_score,
        "score_breakdown": {
            "skill_score": clamp_score(skill_score),
            "project_score": clamp_score(project_score),
            "domain_score": clamp_score(domain_score),
            "basic_requirement_score": clamp_score(basic_requirement_score),
            "expression_score": clamp_score(expression_score),
            "integrity_risk_penalty": clamp_score(integrity_risk_penalty),
        },
        "score_items": score_items,
    }
