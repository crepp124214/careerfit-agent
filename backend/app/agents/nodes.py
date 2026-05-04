from app.agents.state import CareerFitState
from app.llm.schemas import LLMReportEnhancement
from app.llm.service import generate_report_enhancement
from app.scoring.evidence import assess_integrity_risk
from app.scoring.rules import score_match
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


def jd_parser(state: CareerFitState) -> CareerFitState:
    return {"jd_profile": parse_job_profile(state["raw_jd"])}


def resume_parser(state: CareerFitState) -> CareerFitState:
    return {"resume_profile": parse_resume_profile(state["raw_resume"])}


def rag_retriever(state: CareerFitState) -> CareerFitState:
    rag_results = state.get("rag_results", {})
    if rag_results:
        return {"rag_results": rag_results}
    jd_profile = state.get("jd_profile", {})
    required_skills = jd_profile.get("required_skills") or []
    results = {}
    for skill in required_skills:
        results[skill] = {
            "documents": [],
            "available": False,
            "reason": "知识库证据不足",
        }
    return {"rag_results": results}


def match_scorer(state: CareerFitState) -> CareerFitState:
    rag_results = state.get("rag_results")
    return {"match_result": score_match(state["jd_profile"], state["resume_profile"], rag_results=rag_results)}


def gap_analyzer(state: CareerFitState) -> CareerFitState:
    score_items = state["match_result"]["score_items"]
    gaps = [
        {"skill": item["skill"], "reason": "简历缺少可验证证据", "jd_evidence": item["jd_evidence"]}
        for item in score_items
        if not item["resume_evidence"]
    ]
    strengths = [
        {"skill": item["skill"], "resume_evidence": item["resume_evidence"]}
        for item in score_items
        if item["resume_evidence"]
    ]
    return {"gaps": gaps, "strengths": strengths}


def _local_resume_suggestions(state: CareerFitState) -> list[dict]:
    suggestions = []
    for strength in state.get("strengths", []):
        suggestion = f"突出 {strength['skill']} 的项目实践，并保留原始简历中的证据边界。"
        suggestions.append(
            {
                "title": f"强化 {strength['skill']} 表达",
                "suggestion": suggestion,
                "integrity": assess_integrity_risk(suggestion, state["raw_resume"]),
            }
        )
    for gap in state.get("gaps", []):
        suggestions.append(
            {
                "title": f"补齐 {gap['skill']} 证据",
                "suggestion": f"如果确有 {gap['skill']} 经历，补充具体项目背景；否则不要编造。",
                "integrity": {"risk_level": "low", "risk_codes": []},
            }
        )
    return suggestions


def _local_interview_questions(state: CareerFitState) -> list[dict]:
    return [
        {"skill": item["skill"], "question": f"请说明你在 {item['skill']} 上最具体的一次实践。"}
        for item in state["match_result"]["score_items"]
    ]


def _local_learning_plan(state: CareerFitState) -> list[dict]:
    return [
        {
            "skill": gap["skill"],
            "task": f"完成一个使用 {gap['skill']} 的小型可运行项目，并记录证据。",
        }
        for gap in state.get("gaps", [])
    ]


def _local_next_best_action(state: CareerFitState) -> dict:
    gaps = state.get("gaps", [])
    if gaps:
        first_gap = gaps[0]["skill"]
        return {
            "title": f"优先补齐 {first_gap} 的可验证证据",
            "description": "先补最影响匹配分的缺口，再创建下一版简历重新分析。",
            "target_skill": first_gap,
        }
    return {
        "title": "创建下一版简历并重新分析",
        "description": "当前主能力已有证据，下一步优化表达和结构。",
    }


def _enhancement_from_state(state: CareerFitState) -> LLMReportEnhancement | None:
    data = state.get("llm_enhancement")
    if not data:
        return None
    return LLMReportEnhancement.model_validate(data)


def resume_optimizer(state: CareerFitState) -> CareerFitState:
    try:
        enhancement = generate_report_enhancement(state)
    except Exception:
        enhancement = None

    if enhancement is None:
        return {"resume_suggestions": _local_resume_suggestions(state)}

    suggestions = [
        {
            "title": item.title,
            "suggestion": item.suggestion,
            "jd_requirement": item.jd_requirement,
            "resume_evidence": item.resume_evidence,
            "integrity": assess_integrity_risk(item.suggestion, state["raw_resume"]),
        }
        for item in enhancement.resume_suggestions
    ]
    if not suggestions:
        suggestions = _local_resume_suggestions(state)
    return {
        "llm_enhancement": enhancement.model_dump(),
        "resume_suggestions": suggestions,
    }


def interview_coach(state: CareerFitState) -> CareerFitState:
    enhancement = _enhancement_from_state(state)
    if enhancement and enhancement.interview_questions:
        return {
            "interview_questions": [
                {"skill": item.skill, "question": item.question}
                for item in enhancement.interview_questions
            ]
        }
    return {"interview_questions": _local_interview_questions(state)}


def learning_planner(state: CareerFitState) -> CareerFitState:
    enhancement = _enhancement_from_state(state)
    if enhancement and enhancement.learning_plan:
        return {
            "learning_plan": [
                {"skill": item.skill, "task": item.task}
                for item in enhancement.learning_plan
            ]
        }
    return {"learning_plan": _local_learning_plan(state)}


def next_best_action(state: CareerFitState) -> CareerFitState:
    enhancement = _enhancement_from_state(state)
    if enhancement:
        action = enhancement.next_best_action
        return {
            "next_best_action": {
                "title": action.title,
                "description": action.description,
                "target_skill": action.target_skill,
            }
        }
    return {"next_best_action": _local_next_best_action(state)}
