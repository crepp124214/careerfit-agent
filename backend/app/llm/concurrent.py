"""并发 LLM 调用模块"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from app.agents.state import CareerFitState
from app.llm.client import LLMClient, LLMClientError
from app.llm.schemas import (
    LLMInterviewQuestion,
    LLMLearningTask,
    LLMNextBestAction,
    LLMReportEnhancement,
    LLMResumeSuggestion,
)

logger = logging.getLogger(__name__)


def _strip_code_fence(text: str) -> str:
    """移除 markdown code fence"""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


async def _call_llm_async(
    client: LLMClient,
    prompt: str,
    task_name: str,
) -> tuple[str, str]:
    """异步调用 LLM"""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, client.complete, prompt)
        return result, task_name
    except Exception as exc:
        logger.error(f"LLM task {task_name} failed: {exc}")
        raise


async def generate_resume_suggestions_async(
    state: CareerFitState,
    client: LLMClient,
) -> list[LLMResumeSuggestion]:
    """异步生成简历建议"""
    gaps = state.get("gaps", [])
    strengths = state.get("strengths", [])

    prompt = f"""基于以下信息生成简历优化建议。

能力缺口：
{json.dumps([{"skill": g.get("skill"), "reason": g.get("reason")} for g in gaps[:5]], ensure_ascii=False)}

已有优势：
{json.dumps([{"skill": s.get("skill")} for s in strengths[:5]], ensure_ascii=False)}

要求：
1. 针对每个缺口和优势提供具体的简历优化建议
2. 建议必须基于现有证据进行增强表达，不得新增事实
3. 标注每条建议的风险等级
4. 输出严格 JSON 格式

只输出 JSON 数组，不要 Markdown。格式：
[
  {{"title": "...", "suggestion": "...", "jd_requirement": "...", "resume_evidence": "...", "risk_level": "low"}}
]
"""

    try:
        result, _ = await _call_llm_async(client, prompt, "resume_suggestions")
        cleaned_result = _strip_code_fence(result)
        data = json.loads(cleaned_result)
        return [LLMResumeSuggestion(**item) for item in data]
    except Exception as exc:
        logger.warning(f"Failed to generate resume suggestions: {exc}")
        return []


async def generate_interview_questions_async(
    state: CareerFitState,
    client: LLMClient,
) -> list[LLMInterviewQuestion]:
    """异步生成面试题"""
    score_items = state.get("match_result", {}).get("score_items", [])
    gaps = state.get("gaps", [])

    prompt = f"""基于以下信息生成差异化面试题。

评分项：
{json.dumps([{"skill": item.get("skill"), "level": item.get("level")} for item in score_items[:10]], ensure_ascii=False)}

能力缺口：
{json.dumps([{"skill": g.get("skill"), "gap_type": g.get("gap_type", "missing_skill")} for g in gaps[:5]], ensure_ascii=False)}

要求：
1. 按技能类别生成不同类型的面试题
2. 问题应该具体且有针对性
3. 输出严格 JSON 格式

只输出 JSON 数组，不要 Markdown。格式：
[
  {{"skill": "...", "question": "..."}}
]
"""

    try:
        result, _ = await _call_llm_async(client, prompt, "interview_questions")
        cleaned_result = _strip_code_fence(result)
        data = json.loads(cleaned_result)
        return [LLMInterviewQuestion(**item) for item in data]
    except Exception as exc:
        logger.warning(f"Failed to generate interview questions: {exc}")
        return []


async def generate_learning_plan_async(
    state: CareerFitState,
    client: LLMClient,
) -> list[LLMLearningTask]:
    """异步生成学习计划"""
    gaps = state.get("gaps", [])

    prompt = f"""基于以下能力缺口制定学习计划。

能力缺口：
{json.dumps([{"skill": g.get("skill"), "reason": g.get("reason")} for g in gaps[:5]], ensure_ascii=False)}

要求：
1. 为每个高优先级缺口制定学习路径
2. 包含具体练习和验收标准
3. 不要给泛泛的建议
4. 输出严格 JSON 格式

只输出 JSON 数组，不要 Markdown。格式：
[
  {{"skill": "...", "task": "..."}}
]
"""

    try:
        result, _ = await _call_llm_async(client, prompt, "learning_plan")
        cleaned_result = _strip_code_fence(result)
        data = json.loads(cleaned_result)
        return [LLMLearningTask(**item) for item in data]
    except Exception as exc:
        logger.warning(f"Failed to generate learning plan: {exc}")
        return []


async def generate_next_best_action_async(
    state: CareerFitState,
    client: LLMClient,
) -> LLMNextBestAction:
    """异步生成下一步行动"""
    gaps = state.get("gaps", [])
    score = state.get("match_result", {}).get("final_score", 0)

    prompt = f"""基于当前评分和能力缺口，选择最高影响力的下一步行动。

当前总分：{score}

能力缺口：
{json.dumps([{"skill": g.get("skill"), "priority": g.get("priority", "medium")} for g in gaps[:5]], ensure_ascii=False)}

要求：
1. 选择一个最值得立即投入的行动
2. 行动必须有明确的技能目标
3. 解释为什么这个行动影响最大
4. 输出严格 JSON 格式

只输出 JSON 对象，不要 Markdown。格式：
{{"title": "...", "description": "...", "target_skill": "..."}}
"""

    try:
        result, _ = await _call_llm_async(client, prompt, "next_best_action")
        cleaned_result = _strip_code_fence(result)
        data = json.loads(cleaned_result)
        return LLMNextBestAction(**data)
    except Exception as exc:
        logger.warning(f"Failed to generate next best action: {exc}")
        return LLMNextBestAction(
            title="创建下一版简历并重新分析",
            description="当前主能力已有证据，下一步优化表达和结构。",
        )


async def generate_report_enhancement_concurrent(
    state: CareerFitState,
    client: LLMClient,
) -> LLMReportEnhancement:
    """并发生成报告增强内容"""
    logger.info("Starting concurrent LLM enhancement generation")

    try:
        results = await asyncio.gather(
            generate_resume_suggestions_async(state, client),
            generate_interview_questions_async(state, client),
            generate_learning_plan_async(state, client),
            generate_next_best_action_async(state, client),
            return_exceptions=True,
        )

        resume_suggestions = results[0] if not isinstance(results[0], Exception) else []
        interview_questions = results[1] if not isinstance(results[1], Exception) else []
        learning_plan = results[2] if not isinstance(results[2], Exception) else []
        next_best_action = (
            results[3]
            if not isinstance(results[3], Exception)
            else LLMNextBestAction(
                title="创建下一版简历并重新分析",
                description="当前主能力已有证据，下一步优化表达和结构。",
            )
        )

        enhancement = LLMReportEnhancement(
            resume_suggestions=resume_suggestions,
            interview_questions=interview_questions,
            learning_plan=learning_plan,
            next_best_action=next_best_action,
        )

        logger.info(
            f"Concurrent LLM enhancement completed: "
            f"{len(resume_suggestions)} suggestions, "
            f"{len(interview_questions)} questions, "
            f"{len(learning_plan)} learning tasks"
        )

        return enhancement

    except Exception as exc:
        logger.error(f"Concurrent LLM enhancement failed: {exc}")
        return LLMReportEnhancement(
            resume_suggestions=[],
            interview_questions=[],
            learning_plan=[],
            next_best_action=LLMNextBestAction(
                title="创建下一版简历并重新分析",
                description="当前主能力已有证据，下一步优化表达和结构。",
            ),
        )
