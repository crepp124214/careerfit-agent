import logging

from app.agents.state import CareerFitState
from app.core.config import get_settings
from app.llm.agent_prompts import (
    build_jd_parse_prompt,
    build_resume_parse_prompt,
    build_rag_query_plan_prompt,
    build_gap_analysis_prompt,
    build_resume_suggestion_prompt,
    build_interview_prompt,
    build_learning_plan_prompt,
    build_next_best_action_prompt,
)
from app.llm.agent_schemas import (
    JDParseOutput,
    ResumeParseOutput,
    RagQueryPlanOutput,
    GapAnalysisOutput,
    ResumeSuggestionOutput,
    InterviewQuestionOutput,
    LearningPlanOutput,
    NextBestActionOutput,
)
from app.llm.agent_service import AgentLLMError, run_structured_agent
from app.llm.service import build_llm_client
from app.scoring.evidence import assess_integrity_risk
from app.scoring.rules import score_match
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


logger = logging.getLogger(__name__)


def _build_llm_client_or_none():
    try:
        settings = get_settings()
        if not settings.llm_enabled:
            logger.warning("[_build_llm_client_or_none] LLM disabled (llm_enabled=%s)", settings.llm_enabled)
            return None
        client = build_llm_client(settings)
        logger.info("[_build_llm_client_or_none] LLM client created successfully, model=%s", settings.llm_model)
        return client
    except Exception as exc:
        logger.error("[_build_llm_client_or_none] FAILED: %s: %s", type(exc).__name__, exc)
        return None


def _make_fallback_meta(agent_role: str, model_name: str | None, client_existed: bool, error_type: str = "unknown") -> dict:
    return {
        "agent_role": agent_role,
        "execution_mode": "rule",
        "model_name": model_name,
        "fallback_used": True,
        "schema_valid": True,
        "retry_count": 0,
        "llm_error": error_type,
    }


def jd_parser(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_jd_parse_prompt(state["raw_jd"])
            result, meta = run_structured_agent(
                client=client,
                agent_role="jd_parser",
                prompt=prompt,
                output_model=JDParseOutput,
                fallback=lambda: _jd_parse_fallback(state["raw_jd"]),
            )
            jd_profile = _convert_jd_parse_output(result, state["raw_jd"])
            skills = [d["name"] for d in jd_profile.get("skill_dimensions", [])]
            summary = f"提取 {len(skills)} 个技能维度: {', '.join(skills)}" if skills else "未提取到技能维度"
            return {
                "jd_profile": jd_profile,
                "_summary": summary,
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning(
                "[jd_parser] LLM JSON 格式错误（已连接但输出不符合 schema）: %s | errors=%s",
                str(exc), exc.validation_errors[:3],
            )
        except Exception as exc:
            logger.warning("[jd_parser] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    jd_profile = parse_job_profile(state["raw_jd"])
    skills = jd_profile.get("required_skills", [])
    summary = f"提取 {len(skills)} 个技能维度: {', '.join(skills)}" if skills else "未提取到技能维度"
    return {
        "jd_profile": jd_profile,
        "_summary": summary,
        "_execution_meta": _make_fallback_meta("jd_parser", model_name, client is not None, "format_error" if client is not None else "llm_unavailable"),
    }


def _jd_parse_fallback(raw_jd: str) -> JDParseOutput:
    profile = parse_job_profile(raw_jd)
    dimensions = profile.get("skill_dimensions", [])
    return JDParseOutput(
        job_family=profile.get("job_family", "software_engineering"),
        dimensions=[
            {
                "name": d["name"],
                "canonical_key": d["canonical_key"],
                "category": d["category"],
                "weight": d["weight"],
                "required_level": d["required_level"],
                "jd_evidence": d["jd_evidence"],
                "aliases": d["aliases"],
            }
            for d in dimensions
        ],
        evidence_summary=f"规则引擎提取 {len(dimensions)} 个维度",
    )


def _convert_jd_parse_output(output: JDParseOutput, raw_jd: str) -> dict:
    dimensions = []
    evidence_map = {}
    for dim in output.dimensions:
        dimensions.append({
            "name": dim.name,
            "canonical_key": dim.canonical_key,
            "category": dim.category,
            "weight": dim.weight,
            "required_level": dim.required_level,
            "jd_evidence": dim.jd_evidence,
            "aliases": dim.aliases,
        })
        evidence_map[dim.canonical_key] = dim.jd_evidence

    legacy_skills = [dim["name"] for dim in dimensions]

    return {
        "schema_version": "job-profile-v2",
        "job_family": output.job_family,
        "skill_dimensions": dimensions,
        "required_skills": legacy_skills,
        "preferred_skills": [],
        "domain_keywords": [output.job_family],
        "basic_requirements": [],
        "evidence": evidence_map,
    }


def resume_parser(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_resume_parse_prompt(state["raw_resume"])
            result, meta = run_structured_agent(
                client=client,
                agent_role="resume_parser",
                prompt=prompt,
                output_model=ResumeParseOutput,
                fallback=lambda: _resume_parse_fallback(state["raw_resume"]),
            )
            resume_profile = _convert_resume_parse_output(result, state["raw_resume"])
            skills = [s["skill_key"] for s in resume_profile.get("skills", [])]
            summary = f"提取 {len(skills)} 个技能: {', '.join(skills[:5])}" + (
                "..." if len(skills) > 5 else ""
            ) if skills else "未提取到技能"
            return {
                "resume_profile": resume_profile,
                "_summary": summary,
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[resume_parser] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
        except Exception as exc:
            logger.warning("[resume_parser] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    resume_profile = parse_resume_profile(state["raw_resume"])
    skills = []
    for skill_key, evidence_data in resume_profile.items():
        if isinstance(evidence_data, dict):
            skills.append({
                "skill_key": skill_key,
                "evidence": evidence_data.get("resume_evidence", []),
                "expression_level": "project_practice" if evidence_data.get("resume_evidence") else "mentioned",
            })
    skill_keys = [s["skill_key"] for s in skills]
    summary = f"提取 {len(skills)} 个技能: {', '.join(skill_keys[:5])}" + (
        "..." if len(skill_keys) > 5 else ""
    ) if skills else "未提取到技能"
    return {
        "resume_profile": resume_profile,
        "_summary": summary,
        "_execution_meta": {
            "agent_role": "resume_parser",
            "execution_mode": "rule",
            "model_name": model_name,
            "fallback_used": client is not None,
            "schema_valid": True,
            "retry_count": 0,
        },
    }


def _resume_parse_fallback(raw_resume: str) -> ResumeParseOutput:
    profile = parse_resume_profile(raw_resume)
    skills = []
    for skill_key, evidence_data in profile.items():
        if isinstance(evidence_data, dict):
            resume_evidence = evidence_data.get("resume_evidence", [])
            skills.append({
                "skill_key": skill_key,
                "evidence": resume_evidence,
                "expression_level": "project_practice" if resume_evidence else "mentioned",
            })
    return ResumeParseOutput(
        skills=skills,
        project_summary=f"规则引擎提取 {len(skills)} 个技能",
        evidence_summary="fallback",
    )


def _convert_resume_parse_output(output: ResumeParseOutput, raw_resume: str) -> dict:
    skills = []
    evidence = {}
    for item in output.skills:
        skill_entry = {
            "skill_key": item.skill_key,
            "evidence": item.evidence,
            "expression_level": item.expression_level,
        }
        skills.append(skill_entry)
        if item.skill_key:
            evidence[item.skill_key] = item.evidence

    return {
        "schema_version": "resume-profile-v2",
        "skills": skills,
        "projects": [],
        "domain_keywords": [],
        "evidence": evidence,
    }


def rag_query_planner(state: CareerFitState) -> CareerFitState:
    jd_profile = state.get("jd_profile", {})
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_rag_query_plan_prompt(jd_profile)
            result, meta = run_structured_agent(
                client=client,
                agent_role="rag_query_planner",
                prompt=prompt,
                output_model=RagQueryPlanOutput,  # type: ignore
                fallback=lambda: _rag_query_plan_fallback(jd_profile),
            )
            plan = [q.model_dump() if hasattr(q, "model_dump") else q for q in result.queries]
            return {
                "rag_query_plan": plan,
                "_summary": f"规划 {len(plan)} 条检索查询",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[rag_query_planner] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
        except Exception as exc:
            logger.warning("[rag_query_planner] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    plan = _rag_query_plan_fallback(jd_profile)
    return {
        "rag_query_plan": plan,
        "_summary": f"规划 {len(plan)} 条检索查询",
        "_execution_meta": _make_fallback_meta("rag_query_planner", model_name, client is not None, "format_error" if client is not None else "llm_unavailable"),
    }


def _rag_query_plan_fallback(jd_profile: dict) -> list[dict]:
    dimensions = jd_profile.get("skill_dimensions", [])
    if not dimensions:
        skills = jd_profile.get("required_skills", [])
        return [
            {
                "skill_key": s,
                "query": s,
                "job_family": jd_profile.get("job_family", ""),
                "doc_types": [],
            }
            for s in skills
        ]
    return [
        {
            "skill_key": d.get("canonical_key", d["name"]),
            "query": d["name"],
            "job_family": jd_profile.get("job_family", ""),
            "doc_types": [],
        }
        for d in dimensions
    ]


def rag_retriever(state: CareerFitState) -> CareerFitState:
    rag_results = state.get("rag_results", {})
    if rag_results:
        available_count = sum(1 for v in rag_results.values() if isinstance(v, dict) and v.get("available"))
        if available_count > 0:
            return {"rag_results": rag_results, "_summary": f"找到 {available_count} 条知识库证据"}
        return {"rag_results": rag_results, "_summary": "未找到知识库证据"}

    query_plan = state.get("rag_query_plan")
    if not query_plan:
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

    results = {}
    jd_profile = state.get("jd_profile", {})
    job_family = jd_profile.get("job_family", "")

    for query_item in query_plan:
        skill_key = query_item.get("skill_key", "")
        query = query_item.get("query", skill_key)
        doc_types = query_item.get("doc_types", [])

        try:
            from app.rag.retrieval import filter_relevant_documents

            db_session = state.get("_db_session")
            if db_session:
                raw_docs = retrieve_by_skill(
                    db=db_session,
                    skill_name=query,
                    top_k=3,
                )
                relevant = filter_relevant_documents(
                    documents=raw_docs,
                    job_family=job_family,
                    allowed_doc_types=doc_types,
                    min_score=0.72,
                )
                if relevant:
                    results[skill_key] = {
                        "documents": relevant,
                        "available": True,
                        "reason": "found",
                    }
                else:
                    results[skill_key] = {
                        "documents": raw_docs[:1] if raw_docs else [],
                        "available": False,
                        "reason": "知识库证据不足",
                    }
            else:
                results[skill_key] = {
                    "documents": [],
                    "available": False,
                    "reason": "知识库证据不足",
                }
        except Exception as exc:
            logger.warning(f"RAG 检索失败 [{skill_key}]: {exc}")
            results[skill_key] = {
                "documents": [],
                "available": False,
                "reason": "知识库证据不足",
            }

    available_count = sum(1 for v in results.values() if v.get("available"))
    summary = f"找到 {available_count} 条知识库证据" if available_count > 0 else "未找到知识库证据"
    return {"rag_results": results, "_summary": summary}


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


def resume_optimizer(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_resume_suggestion_prompt(
                gaps=state.get("gaps", []),
                strengths=state.get("strengths", []),
            )
            result, meta = run_structured_agent(
                client=client,
                agent_role="resume_optimizer",
                prompt=prompt,
                output_model=ResumeSuggestionOutput,  # type: ignore
                fallback=lambda: ResumeSuggestionOutput(suggestions=_local_resume_suggestions(state)),
            )
            suggestions = _convert_resume_suggestions(result.suggestions, state)
            return {
                "resume_suggestions": suggestions,
                "_summary": f"生成 {len(suggestions)} 条优化建议",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[resume_optimizer] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
        except Exception as exc:
            logger.warning("[resume_optimizer] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    suggestions = _local_resume_suggestions(state)
    return {
        "resume_suggestions": suggestions,
        "_summary": f"生成 {len(suggestions)} 条优化建议",
        "_execution_meta": _make_fallback_meta("resume_optimizer", model_name, client is not None, "format_error" if client is not None else "llm_unavailable"),
    }


def _convert_resume_suggestions(suggestions: list, state: CareerFitState) -> list[dict]:
    converted = []
    for item in suggestions:
        if isinstance(item, dict):
            suggestion_text = item.get("suggestion", "")
            converted.append({
                "title": item.get("title", ""),
                "suggestion": suggestion_text,
                "jd_requirement": item.get("jd_requirement", ""),
                "resume_evidence": item.get("resume_evidence", []),
                "integrity": assess_integrity_risk(suggestion_text, state["raw_resume"]),
            })
        else:
            suggestion_text = getattr(item, "suggestion", str(item))
            converted.append({
                "title": getattr(item, "title", ""),
                "suggestion": suggestion_text,
                "jd_requirement": getattr(item, "jd_requirement", ""),
                "resume_evidence": getattr(item, "resume_evidence", []),
                "integrity": assess_integrity_risk(suggestion_text, state["raw_resume"]),
            })
    return converted


def interview_coach(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            score_items = state.get("match_result", {}).get("score_items", [])
            prompt = build_interview_prompt(
                score_items=score_items,
                gaps=state.get("gaps", []),
            )
            result, meta = run_structured_agent(
                client=client,
                agent_role="interview_coach",
                prompt=prompt,
                output_model=InterviewQuestionOutput,  # type: ignore
                fallback=lambda: InterviewQuestionOutput(questions=_local_interview_questions(state)),
            )
            questions = _convert_interview_questions(result.questions)
            return {
                "interview_questions": questions,
                "_summary": f"生成 {len(questions)} 道面试题",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[interview_coach] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
        except Exception as exc:
            logger.warning("[interview_coach] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    questions = _local_interview_questions(state)
    return {
        "interview_questions": questions,
        "_summary": f"生成 {len(questions)} 道面试题",
        "_execution_meta": _make_fallback_meta("interview_coach", model_name, client is not None, "format_error" if client is not None else "llm_unavailable"),
    }


def _convert_interview_questions(questions: list) -> list[dict]:
    converted = []
    for item in questions:
        if isinstance(item, dict):
            converted.append({
                "skill": item.get("skill", ""),
                "question": item.get("question", ""),
                "difficulty": item.get("difficulty", "medium"),
            })
        else:
            converted.append({
                "skill": getattr(item, "skill", ""),
                "question": getattr(item, "question", ""),
                "difficulty": getattr(item, "difficulty", "medium"),
            })
    return converted


def learning_planner(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_learning_plan_prompt(
                gaps=state.get("gaps", []),
                knowledge=state.get("rag_results", {}),
            )
            result, meta = run_structured_agent(
                client=client,
                agent_role="learning_planner",
                prompt=prompt,
                output_model=LearningPlanOutput,  # type: ignore
                fallback=lambda: LearningPlanOutput(tasks=_local_learning_plan(state)),
            )
            plan = _convert_learning_tasks(result.tasks)
            return {
                "learning_plan": plan,
                "_summary": f"生成 {len(plan)} 项学习任务",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[learning_planner] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
        except Exception as exc:
            logger.warning("[learning_planner] LLM 调用异常: %s: %s", type(exc).__name__, exc)

    plan = _local_learning_plan(state)
    return {
        "learning_plan": plan,
        "_summary": f"生成 {len(plan)} 项学习任务",
        "_execution_meta": _make_fallback_meta("learning_planner", model_name, client is not None, "format_error" if client is not None else "llm_unavailable"),
    }


def _convert_learning_tasks(tasks: list) -> list[dict]:
    converted = []
    for item in tasks:
        if isinstance(item, dict):
            converted.append({
                "skill": item.get("skill", ""),
                "task": item.get("task", ""),
                "estimated_hours": item.get("estimated_hours", 0),
            })
        else:
            converted.append({
                "skill": getattr(item, "skill", ""),
                "task": getattr(item, "task", ""),
                "estimated_hours": getattr(item, "estimated_hours", 0),
            })
    return converted


def next_best_action(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client = _build_llm_client_or_none()

    if client is not None:
        try:
            prompt = build_next_best_action_prompt(
                gaps=state.get("gaps", []),
                score=state.get("match_result", {}).get("overall_score", 0),
            )
            result, meta = run_structured_agent(
                client=client,
                agent_role="next_best_action",
                prompt=prompt,
                output_model=NextBestActionOutput,  # type: ignore
                fallback=lambda: NextBestActionOutput(**_local_next_best_action(state)),
            )
            nba = {
                "title": result.title,
                "description": result.description,
                "target_skill": result.target_skill,
            }
            return {
                "next_best_action": nba,
                "_summary": nba["title"],
                "_execution_meta": meta,
            }
        except Exception as exc:
            logger.warning("下一步行动 LLM 调用失败，回退到规则引擎: %s", exc)

    nba = _local_next_best_action(state)
    return {
        "next_best_action": nba,
        "_summary": nba["title"],
        "_execution_meta": {
            "agent_role": "next_best_action",
            "execution_mode": "rule",
            "model_name": model_name,
            "fallback_used": client is not None,
            "schema_valid": True,
            "retry_count": 0,
        },
    }
