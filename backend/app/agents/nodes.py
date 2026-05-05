import logging

from app.agents.state import CareerFitState
from app.core.config import get_settings
from app.llm.schemas import LLMReportEnhancement
from app.llm.service import generate_report_enhancement
from app.scoring.evidence import assess_integrity_risk
from app.scoring.rules import score_match
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


def jd_parser(state: CareerFitState) -> CareerFitState:
    jd_profile = parse_job_profile(state["raw_jd"])
    skills = jd_profile.get("required_skills", [])
    summary = f"提取 {len(skills)} 个技能维度: {', '.join(skills)}" if skills else "未提取到技能维度"
    return {"jd_profile": jd_profile, "_summary": summary}


def resume_parser(state: CareerFitState) -> CareerFitState:
    resume_profile = parse_resume_profile(state["raw_resume"])
    evidence_count = sum(
        len(v.get("resume_evidence", []))
        for v in resume_profile.values()
        if isinstance(v, dict) and "resume_evidence" in v
    )
    if evidence_count == 0:
        score_items_count = len(resume_profile.get("skill_dimensions", []))
        summary = f"识别 {score_items_count} 项技能证据"
    else:
        summary = f"识别 {evidence_count} 项技能证据"
    return {"resume_profile": resume_profile, "_summary": summary}


def rag_retriever(state: CareerFitState) -> CareerFitState:
    rag_results = state.get("rag_results", {})
    if rag_results:
        available_count = sum(1 for v in rag_results.values() if isinstance(v, dict) and v.get("available"))
        if available_count > 0:
            return {"rag_results": rag_results, "_summary": f"找到 {available_count} 条知识库证据"}
        return {"rag_results": rag_results, "_summary": "未找到知识库证据"}
    jd_profile = state.get("jd_profile", {})
    required_skills = jd_profile.get("required_skills") or []
    results = {}
    for skill in required_skills:
        results[skill] = {
            "documents": [],
            "available": False,
            "reason": "知识库证据不足",
        }
    return {"rag_results": results, "_summary": "未找到知识库证据"}


def match_scorer(state: CareerFitState) -> CareerFitState:
    rag_results = state.get("rag_results")
    match_result = score_match(state["jd_profile"], state["resume_profile"], rag_results=rag_results)
    final_score = match_result.get("final_score", 0)
    return {"match_result": match_result, "_summary": f"综合匹配度: {final_score}%"}


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
    if gaps:
        gap_skills = [g["skill"] for g in gaps]
        summary = f"{len(gaps)} 项高风险: {', '.join(gap_skills)}"
    else:
        summary = "无能力缺口"
    return {"gaps": gaps, "strengths": strengths, "_summary": summary}


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
    settings = get_settings()
    model_name = settings.llm_model
    try:
        enhancement, model_name = generate_report_enhancement(state)
    except Exception as exc:
        logging.getLogger(__name__).warning("LLM 调用失败，回退到规则引擎: %s", exc)
        enhancement = None

    if enhancement is None:
        suggestions = _local_resume_suggestions(state)
        return {
            "resume_suggestions": suggestions,
            "_summary": f"生成 {len(suggestions)} 条优化建议",
            "_execution_meta": {
                "agent_role": "resume_optimizer",
                "execution_mode": "rule",
                "model_name": model_name,
                "fallback_used": True,
                "schema_valid": True,
                "retry_count": 0,
            },
        }

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
        "_summary": f"生成 {len(suggestions)} 条优化建议",
        "_execution_meta": {
            "agent_role": "resume_optimizer",
            "execution_mode": "llm",
            "model_name": model_name,
            "fallback_used": False,
            "schema_valid": True,
            "retry_count": 0,
        },
    }


def interview_coach(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    enhancement = _enhancement_from_state(state)
    if enhancement and enhancement.interview_questions:
        questions = [
            {"skill": item.skill, "question": item.question}
            for item in enhancement.interview_questions
        ]
        return {
            "interview_questions": questions,
            "_summary": f"生成 {len(questions)} 道面试题",
            "_execution_meta": {
                "agent_role": "interview_coach",
                "execution_mode": "llm",
                "model_name": model_name,
                "fallback_used": False,
                "schema_valid": True,
                "retry_count": 0,
            },
        }
    questions = _local_interview_questions(state)
    return {
        "interview_questions": questions,
        "_summary": f"生成 {len(questions)} 道面试题",
        "_execution_meta": {
            "agent_role": "interview_coach",
            "execution_mode": "rule",
            "model_name": model_name,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
        },
    }


def learning_planner(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    enhancement = _enhancement_from_state(state)
    if enhancement and enhancement.learning_plan:
        plan = [
            {"skill": item.skill, "task": item.task}
            for item in enhancement.learning_plan
        ]
        return {
            "learning_plan": plan,
            "_summary": f"生成 {len(plan)} 项学习任务",
            "_execution_meta": {
                "agent_role": "learning_planner",
                "execution_mode": "llm",
                "model_name": model_name,
                "fallback_used": False,
                "schema_valid": True,
                "retry_count": 0,
            },
        }
    plan = _local_learning_plan(state)
    return {
        "learning_plan": plan,
        "_summary": f"生成 {len(plan)} 项学习任务",
        "_execution_meta": {
            "agent_role": "learning_planner",
            "execution_mode": "rule",
            "model_name": model_name,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
        },
    }


def next_best_action(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    enhancement = _enhancement_from_state(state)
    if enhancement:
        action = enhancement.next_best_action
        nba = {
            "title": action.title,
            "description": action.description,
            "target_skill": action.target_skill,
        }
        return {
            "next_best_action": nba,
            "_summary": nba["title"],
            "_execution_meta": {
                "agent_role": "next_best_action",
                "execution_mode": "llm",
                "model_name": model_name,
                "fallback_used": False,
                "schema_valid": True,
                "retry_count": 0,
            },
        }
    nba = _local_next_best_action(state)
    return {
        "next_best_action": nba,
        "_summary": nba["title"],
        "_execution_meta": {
            "agent_role": "next_best_action",
            "execution_mode": "rule",
            "model_name": model_name,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
        },
    }
