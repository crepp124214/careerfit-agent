import logging
import time
from typing import Any, Callable

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

MAX_LLM_RETRIES = 2
LLM_RETRY_DELAY_S = 1.0


def _build_llm_client_with_retry(max_retries: int = MAX_LLM_RETRIES) -> tuple[Any | None, str]:
    """
    Build LLM client with retry mechanism for better stability

    Returns:
        (client, error_type) - error_type is None if successful
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            settings = get_settings()
            if not settings.llm_enabled:
                logger.warning("[_build_llm_client_with_retry] LLM disabled")
                return None, "llm_disabled"

            client = build_llm_client(settings)
            logger.info(
                "[_build_llm_client_with_retry] Client created successfully "
                "(attempt %d/%d), model=%s",
                attempt, max_retries, settings.llm_model,
            )
            return client, None

        except Exception as exc:
            last_error = exc
            logger.warning(
                "[_build_llm_client_with_retry] Attempt %d/%d failed: %s: %s",
                attempt, max_retries, type(exc).__name__, exc,
            )

            if attempt < max_retries:
                time.sleep(LLM_RETRY_DELAY_S * attempt)

    logger.error(
        "[_build_llm_client_with_retry] All %d attempts failed: %s: %s",
        max_retries, type(last_error).__name__, last_error,
    )
    return None, "connection_failed"


def _make_fallback_meta(agent_role: str, model_name: str | None, client_existed: bool, error_type: str = "unknown") -> dict:
    error_labels = {
        "llm_disabled": "LLM 未启用",
        "connection_failed": "大模型 API 连接失败",
        "parse_failed": "LLM 输出格式解析失败",
        "llm_call_error": "LLM 调用异常",
        "llm_unavailable": "LLM 不可用",
    }
    return {
        "agent_role": agent_role,
        "execution_mode": "rule",
        "model_name": model_name,
        "fallback_used": True,
        "schema_valid": True,
        "retry_count": 0,
        "llm_error": error_type,
        "llm_error_label": error_labels.get(error_type, error_type),
    }


def jd_parser(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

    if client is not None:
        try:
            prompt = build_jd_parse_prompt(state["raw_jd"])
            result, meta = run_structured_agent(
                client=client,
                agent_role="jd_parser",
                prompt=prompt,
                output_model=JDParseOutput,
                fallback=lambda: _jd_parse_fallback(state["raw_jd"]),
                model_name=model_name,
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
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[jd_parser] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    jd_profile = parse_job_profile(state["raw_jd"])
    skills = jd_profile.get("required_skills", [])
    summary = f"提取 {len(skills)} 个技能维度: {', '.join(skills)}" if skills else "未提取到技能维度"
    return {
        "jd_profile": jd_profile,
        "_summary": summary,
        "_execution_meta": _make_fallback_meta("jd_parser", model_name, client is not None, fallback_error_type),
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
    # 先用规则引擎解析，获取权重和证据
    rule_based_profile = parse_job_profile(raw_jd)
    rule_dimensions = {d["canonical_key"]: d for d in rule_based_profile.get("skill_dimensions", [])}
    
    # 构建名称到key的映射（用于LLM输出key不匹配时查找）
    from app.services.job_service import SKILL_CATALOG
    name_to_key = {item["name"].lower(): key for key, item in SKILL_CATALOG.items()}
    alias_to_key = {}
    for key, item in SKILL_CATALOG.items():
        for alias in item.get("aliases", []):
            alias_to_key[alias.lower()] = key
    
    def find_rule_key(llm_key: str, llm_name: str) -> str | None:
        """根据LLM输出的key或name找到对应的规则引擎key"""
        # 直接匹配
        if llm_key in rule_dimensions:
            return llm_key
        # 按名称匹配
        if llm_name.lower() in name_to_key:
            return name_to_key[llm_name.lower()]
        # 按别名匹配
        if llm_key.lower() in alias_to_key:
            return alias_to_key[llm_key.lower()]
        if llm_name.lower() in alias_to_key:
            return alias_to_key[llm_name.lower()]
        return None
    
    dimensions = []
    evidence_map = {}
    for dim in output.dimensions:
        llm_key = dim.canonical_key
        llm_name = dim.name
        
        # 尝试找到对应的规则引擎key
        rule_key = find_rule_key(llm_key, llm_name)
        
        # 使用规则引擎的key（如果找到），否则使用LLM的key
        canonical_key = rule_key if rule_key else llm_key
        
        # 使用规则引擎计算的权重（更合理），如果规则引擎没有该技能，则使用LLM的权重
        rule_dim = rule_dimensions.get(canonical_key) if rule_key else None
        weight = rule_dim["weight"] if rule_dim else dim.weight
        
        dimensions.append({
            "name": dim.name,
            "canonical_key": canonical_key,
            "category": dim.category,
            "weight": weight,
            "required_level": dim.required_level,
            "jd_evidence": dim.jd_evidence,
            "aliases": dim.aliases,
        })
        evidence_map[canonical_key] = dim.jd_evidence

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
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

    if client is not None:
        try:
            prompt = build_resume_parse_prompt(state["raw_resume"])
            result, meta = run_structured_agent(
                client=client,
                agent_role="resume_parser",
                prompt=prompt,
                output_model=ResumeParseOutput,
                fallback=lambda: _resume_parse_fallback(state["raw_resume"]),
                model_name=model_name,
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
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[resume_parser] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

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
        "_execution_meta": _make_fallback_meta("resume_parser", model_name, client is not None, fallback_error_type),
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
    # 先用规则引擎解析，获取项目经验和证据
    rule_based_profile = parse_resume_profile(raw_resume)
    
    # 构建名称到key的映射（用于LLM输出key不匹配时查找）
    from app.services.job_service import SKILL_CATALOG
    name_to_key = {item["name"].lower(): key for key, item in SKILL_CATALOG.items()}
    alias_to_key = {}
    for key, item in SKILL_CATALOG.items():
        for alias in item.get("aliases", []):
            alias_to_key[alias.lower()] = key
    
    def normalize_skill_key(llm_key: str) -> str:
        """将LLM输出的skill_key标准化为规则引擎的key"""
        if not llm_key:
            return llm_key
        # 直接匹配
        if llm_key.lower() in name_to_key:
            return name_to_key[llm_key.lower()]
        if llm_key.lower() in alias_to_key:
            return alias_to_key[llm_key.lower()]
        return llm_key.lower().replace(" ", "_").replace("/", "_")
    
    skills = []
    evidence = dict(rule_based_profile.get("evidence", {}))  # 从规则引擎获取证据
    
    for item in output.skills:
        normalized_key = normalize_skill_key(item.skill_key)
        skill_entry = {
            "skill_key": normalized_key,
            "evidence": item.evidence,
            "expression_level": item.expression_level,
        }
        skills.append(skill_entry)
        # LLM 的证据可能更详细，优先使用 LLM 的，但保留规则引擎的证据作为补充
        if normalized_key and item.evidence:
            existing = evidence.get(normalized_key, [])
            if isinstance(existing, list):
                # 合并证据，去重
                combined = list(dict.fromkeys(existing + list(item.evidence)))
                evidence[normalized_key] = combined
            else:
                evidence[normalized_key] = list(item.evidence)

    return {
        "schema_version": "resume-profile-v2",
        "skills": skills,
        "projects": rule_based_profile.get("projects", []),  # 使用规则引擎提取的项目
        "domain_keywords": rule_based_profile.get("domain_keywords", []),
        "evidence": evidence,
    }


def rag_query_planner(state: CareerFitState) -> CareerFitState:
    jd_profile = state.get("jd_profile", {})
    settings = get_settings()
    model_name = settings.llm_model
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

    if client is not None:
        try:
            prompt = build_rag_query_plan_prompt(jd_profile)
            result, meta = run_structured_agent(
                client=client,
                agent_role="rag_query_planner",
                prompt=prompt,
                output_model=RagQueryPlanOutput,  # type: ignore
                fallback=lambda: _rag_query_plan_fallback(jd_profile),
                model_name=model_name,
            )
            plan = [q.model_dump() if hasattr(q, "model_dump") else q for q in result.queries]
            return {
                "rag_query_plan": plan,
                "_summary": f"规划 {len(plan)} 条检索查询",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[rag_query_planner] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[rag_query_planner] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    plan = _rag_query_plan_fallback(jd_profile)
    return {
        "rag_query_plan": plan,
        "_summary": f"规划 {len(plan)} 条检索查询",
        "_execution_meta": _make_fallback_meta("rag_query_planner", model_name, client is not None, fallback_error_type),
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
    settings = get_settings()
    model_name = settings.llm_model
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

    if client is not None:
        try:
            prompt = build_gap_analysis_prompt(state["match_result"])
            result, meta = run_structured_agent(
                client=client,
                agent_role="gap_analyzer",
                prompt=prompt,
                output_model=GapAnalysisOutput,
                fallback=lambda: GapAnalysisOutput(**_local_gap_analysis(state)),
                model_name=model_name,
            )
            gaps = _convert_gap_items(result.gaps)
            strengths = _convert_strength_items(result.strengths)
            if gaps:
                gap_skills = [g["skill"] for g in gaps]
                summary = f"{len(gaps)} 项缺口: {', '.join(gap_skills)}"
            else:
                summary = "无能力缺口"
            return {"gaps": gaps, "strengths": strengths, "_summary": summary, "_execution_meta": meta}
        except AgentLLMError as exc:
            logger.warning("[gap_analyzer] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[gap_analyzer] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    local_result = _local_gap_analysis(state)
    gaps = local_result["gaps"]
    strengths = local_result["strengths"]
    if gaps:
        gap_skills = [g["skill"] for g in gaps]
        summary = f"{len(gaps)} 项缺口: {', '.join(gap_skills)}"
    else:
        summary = "无能力缺口"
    return {"gaps": gaps, "strengths": strengths, "_summary": summary,
            "_execution_meta": _make_fallback_meta("gap_analyzer", model_name, client is not None, fallback_error_type)}


def _local_gap_analysis(state: CareerFitState) -> dict:
    score_items = state["match_result"]["score_items"]
    gaps = []
    strengths = []
    for item in score_items:
        score = item.get("score", 0)
        level = item.get("level", "not_mentioned")
        jd_level = item.get("jd_required_level", "project_practice")
        weight = item.get("weight", 0.7)

        if not item.get("resume_evidence"):
            gap_type = "missing_skill"
            priority = "high" if weight >= 0.7 else "medium"
        elif score < 50:
            gap_type = "weak_evidence"
            priority = "high" if weight >= 0.7 else "medium"
        elif level in ("mentioned", "basic_usage") and jd_level in ("project_practice", "deep_experience"):
            gap_type = "expression_gap"
            priority = "medium" if weight >= 0.5 else "low"
        elif score < 60 and jd_level == "deep_experience":
            gap_type = "knowledge_insufficient"
            priority = "medium"
        else:
            gap_type = None

        if gap_type:
            gaps.append({
                "skill": item["skill"],
                "skill_key": item.get("skill_key", item["skill"]),
                "gap_type": gap_type,
                "reason": _gap_reason(gap_type, item),
                "priority": priority,
                "jd_evidence": item.get("jd_evidence", []),
            })
        else:
            strengths.append({
                "skill": item["skill"],
                "resume_evidence": item.get("resume_evidence", []),
            })

    return {"gaps": gaps, "strengths": strengths}


def _gap_reason(gap_type: str, item: dict) -> str:
    reasons = {
        "missing_skill": f"简历中未提及 {item['skill']} 的任何经验",
        "weak_evidence": f"{item['skill']} 证据薄弱（得分{item.get('score', 0)}%），JD要求{item.get('jd_required_level', '')}",
        "expression_gap": f"{item['skill']} 有相关经验但表达不够充分",
        "knowledge_insufficient": f"{item['skill']} 知识深度可能不足，JD要求深度经验",
    }
    return reasons.get(gap_type, "存在能力缺口")


def _convert_gap_items(gaps: list) -> list[dict]:
    converted = []
    for item in gaps:
        if isinstance(item, dict):
            converted.append({
                "skill": item.get("skill", item.get("skill_key", "")),
                "skill_key": item.get("skill_key", item.get("skill", "")),
                "gap_type": item.get("gap_type", "missing_skill"),
                "reason": item.get("reason", ""),
                "priority": item.get("priority", "medium"),
                "jd_evidence": item.get("jd_evidence", []),
            })
        else:
            converted.append({
                "skill": getattr(item, "skill_key", "") or getattr(item, "skill", ""),
                "skill_key": getattr(item, "skill_key", ""),
                "gap_type": getattr(item, "gap_type", "missing_skill"),
                "reason": getattr(item, "reason", ""),
                "priority": getattr(item, "priority", "medium"),
                "jd_evidence": getattr(item, "jd_evidence", []),
            })
    return converted


def _convert_strength_items(strengths: list) -> list[dict]:
    converted = []
    for item in strengths:
        if isinstance(item, dict):
            converted.append({
                "skill": item.get("skill", item.get("skill_key", "")),
                "resume_evidence": item.get("resume_evidence", []),
            })
        else:
            converted.append({
                "skill": getattr(item, "skill", ""),
                "resume_evidence": getattr(item, "resume_evidence", []),
            })
    return converted


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
        gap_type = gap.get("gap_type", "missing_skill")
        skill = gap["skill"]
        if gap_type == "missing_skill":
            suggestion = f"JD要求 {skill} 但简历中未提及。如果确有相关经历，请补充具体项目背景；否则不要编造。"
        elif gap_type == "weak_evidence":
            suggestion = f"你在 {skill} 上的证据较薄弱，建议补充更具体的项目细节和技术深度描述。"
        elif gap_type == "expression_gap":
            suggestion = f"你有 {skill} 的相关经验，但表达不够充分。建议使用STAR法则重新组织描述，突出技术难点和成果。"
        elif gap_type == "knowledge_insufficient":
            suggestion = f"JD要求 {skill} 的深度经验，建议补充架构设计、性能优化等高阶实践描述（如果有真实经历）。"
        else:
            suggestion = f"如果确有 {skill} 经历，补充具体项目背景；否则不要编造。"
        suggestions.append(
            {
                "title": f"补齐 {skill} 证据",
                "suggestion": suggestion,
                "integrity": {"risk_level": "low", "risk_codes": []},
            }
        )
    return suggestions


def _local_interview_questions(state: CareerFitState) -> list[dict]:
    score_items = state.get("match_result", {}).get("score_items", [])
    gaps = state.get("gaps", [])
    gap_skills = {g.get("skill", g.get("skill_key", "")) for g in gaps}

    if score_items:
        questions = []
        for item in score_items:
            skill = item["skill"]
            is_gap = skill in gap_skills
            if is_gap:
                questions.append({
                    "skill": skill,
                    "question": f"请说明你在 {skill} 上最具体的一次实践，包括遇到的技术难点和解决方案。",
                    "difficulty": "medium",
                    "type": "behavioral",
                    "purpose": f"验证 {skill} 实践经验的真实性",
                    "source": "resume_based",
                })
            else:
                questions.append({
                    "skill": skill,
                    "question": f"请详细解释 {skill} 的核心原理和你在项目中的最佳实践。",
                    "difficulty": "hard",
                    "type": "technical",
                    "purpose": f"验证 {skill} 的技术深度",
                    "source": "jd_based",
                })
        return questions

    interview_input = state.get("_interview_input", {})
    skills = interview_input.get("skills", [])
    if skills:
        return [
            {
                "skill": s,
                "question": f"请详细说明你在 {s} 方面的技术深度和项目经验。",
                "difficulty": "medium",
                "type": "technical",
                "purpose": f"评估 {s} 的掌握程度",
                "source": "jd_based",
            }
            for s in skills
        ]

    return [{
        "skill": "general",
        "question": "请介绍你最自豪的技术项目。",
        "difficulty": "easy",
        "type": "behavioral",
        "purpose": "了解候选人的技术热情和项目经验",
        "source": "jd_based",
    }]


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
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

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
                model_name=model_name,
            )
            suggestions = _convert_resume_suggestions(result.suggestions, state)
            return {
                "resume_suggestions": suggestions,
                "_summary": f"生成 {len(suggestions)} 条优化建议",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[resume_optimizer] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[resume_optimizer] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    suggestions = _local_resume_suggestions(state)
    return {
        "resume_suggestions": suggestions,
        "_summary": f"生成 {len(suggestions)} 条优化建议",
        "_execution_meta": _make_fallback_meta("resume_optimizer", model_name, client is not None, fallback_error_type),
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
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

    if client is not None:
        try:
            score_items = state.get("match_result", {}).get("score_items", [])
            gaps = state.get("gaps", [])
            interview_input = state.get("_interview_input", {})

            if not score_items and interview_input:
                skills = interview_input.get("skills", [])
                score_items = [
                    {"skill": s, "level": "unknown", "resume_evidence": [], "score": 0}
                    for s in skills
                ]
                gap_skills = set(skills[:len(skills)//2])
                gaps = [
                    {"skill_key": s, "skill": s, "gap_type": "weak_evidence", "priority": "medium"}
                    for s in gap_skills
                ]

            prompt = build_interview_prompt(
                score_items=score_items,
                gaps=gaps,
            )

            interview_input_context = ""
            if interview_input:
                jd_ctx = interview_input.get("jd_context", "")
                resume_ctx = interview_input.get("resume_context", "")
                q_types = interview_input.get("question_types", [])
                difficulty = interview_input.get("difficulty", "mixed")
                count = interview_input.get("count", 10)
                if jd_ctx or resume_ctx:
                    interview_input_context = f"\n## 额外上下文：\nJD: {jd_ctx[:500]}\n简历: {resume_ctx[:500]}\n题型偏好: {q_types}\n难度: {difficulty}\n数量: {count}\n"
                prompt = prompt + interview_input_context

            result, meta = run_structured_agent(
                client=client,
                agent_role="interview_coach",
                prompt=prompt,
                output_model=InterviewQuestionOutput,  # type: ignore
                fallback=lambda: InterviewQuestionOutput(questions=_local_interview_questions(state)),
                model_name=model_name,
            )
            questions = _convert_interview_questions(result.questions)
            return {
                "interview_questions": questions,
                "_summary": f"生成 {len(questions)} 道面试题",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[interview_coach] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[interview_coach] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    questions = _local_interview_questions(state)
    return {
        "interview_questions": questions,
        "_summary": f"生成 {len(questions)} 道面试题",
        "_execution_meta": _make_fallback_meta("interview_coach", model_name, client is not None, fallback_error_type),
    }


def _convert_interview_questions(questions: list) -> list[dict]:
    converted = []
    for item in questions:
        if isinstance(item, dict):
            converted.append({
                "skill": item.get("skill", ""),
                "question": item.get("question", ""),
                "difficulty": item.get("difficulty", "medium"),
                "type": item.get("type", "technical"),
                "purpose": item.get("purpose", ""),
                "what_it_tests": item.get("what_it_tests", []),
                "ideal_answer_hints": item.get("ideal_answer_hints", []),
                "source": item.get("source", "jd_based"),
            })
        else:
            converted.append({
                "skill": getattr(item, "skill", ""),
                "question": getattr(item, "question", ""),
                "difficulty": getattr(item, "difficulty", "medium"),
                "type": getattr(item, "type", "technical"),
                "purpose": getattr(item, "purpose", ""),
                "what_it_tests": getattr(item, "what_it_tests", []),
                "ideal_answer_hints": getattr(item, "ideal_answer_hints", []),
                "source": getattr(item, "source", "jd_based"),
            })
    return converted


def learning_planner(state: CareerFitState) -> CareerFitState:
    settings = get_settings()
    model_name = settings.llm_model
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

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
                model_name=model_name,
            )
            plan = _convert_learning_tasks(result.tasks)
            return {
                "learning_plan": plan,
                "_summary": f"生成 {len(plan)} 项学习任务",
                "_execution_meta": meta,
            }
        except AgentLLMError as exc:
            logger.warning("[learning_planner] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[learning_planner] LLM 调用异常: %s: %s", type(exc).__name__, exc)
            fallback_error_type = "llm_call_error"

    plan = _local_learning_plan(state)
    return {
        "learning_plan": plan,
        "_summary": f"生成 {len(plan)} 项学习任务",
        "_execution_meta": _make_fallback_meta("learning_planner", model_name, client is not None, fallback_error_type),
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
    client, error_type = _build_llm_client_with_retry()
    fallback_error_type = error_type or "llm_unavailable"

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
                model_name=model_name,
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
        except AgentLLMError as exc:
            logger.warning("[next_best_action] LLM JSON 格式错误: %s | errors=%s", str(exc), exc.validation_errors[:3])
            fallback_error_type = "parse_failed"
        except Exception as exc:
            logger.warning("[next_best_action] LLM 调用失败，回退到规则引擎: %s", exc)
            fallback_error_type = "llm_call_error"

    nba = _local_next_best_action(state)
    return {
        "next_best_action": nba,
        "_summary": nba["title"],
        "_execution_meta": _make_fallback_meta("next_best_action", model_name, client is not None, fallback_error_type),
    }
