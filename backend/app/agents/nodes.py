from app.agents.state import CareerFitState
from app.scoring.evidence import assess_integrity_risk
from app.scoring.rules import score_match
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


def jd_parser(state: CareerFitState) -> CareerFitState:
    return {"jd_profile": parse_job_profile(state["raw_jd"])}


def resume_parser(state: CareerFitState) -> CareerFitState:
    return {"resume_profile": parse_resume_profile(state["raw_resume"])}


def match_scorer(state: CareerFitState) -> CareerFitState:
    return {"match_result": score_match(state["jd_profile"], state["resume_profile"])}


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


def resume_optimizer(state: CareerFitState) -> CareerFitState:
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
    return {"resume_suggestions": suggestions}


def interview_coach(state: CareerFitState) -> CareerFitState:
    questions = [
        {"skill": item["skill"], "question": f"请说明你在 {item['skill']} 上最具体的一次实践。"}
        for item in state["match_result"]["score_items"]
    ]
    return {"interview_questions": questions}


def learning_planner(state: CareerFitState) -> CareerFitState:
    learning_plan = [
        {
            "skill": gap["skill"],
            "task": f"完成一个使用 {gap['skill']} 的小型可运行项目，并记录证据。",
        }
        for gap in state.get("gaps", [])
    ]
    return {"learning_plan": learning_plan}


def next_best_action(state: CareerFitState) -> CareerFitState:
    gaps = state.get("gaps", [])
    if gaps:
        first_gap = gaps[0]["skill"]
        action = {
            "title": f"优先补齐 {first_gap} 的可验证证据",
            "description": "先补最影响匹配分的缺口，再创建下一版简历重新分析。",
            "target_skill": first_gap,
        }
    else:
        action = {
            "title": "创建下一版简历并重新分析",
            "description": "当前主能力已有证据，下一步优化表达和结构。",
        }
    return {"next_best_action": action}
