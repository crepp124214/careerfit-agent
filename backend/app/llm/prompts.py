from __future__ import annotations

import json

from app.agents.state import CareerFitState


def build_report_enhancement_prompt(state: CareerFitState, *, repair_text: str | None = None) -> str:
    if repair_text is not None:
        return (
            "请把下面内容修复为严格 JSON，只保留指定字段，不要添加 Markdown：\n"
            f"{repair_text}"
        )

    payload = {
        "strengths": state.get("strengths", []),
        "gaps": state.get("gaps", []),
        "score_items": state.get("match_result", {}).get("score_items", []),
    }
    return (
        "你是计算机应届生求职成长助手。请基于结构化匹配结果生成中文建议。"
        "必须诚实，不得编造简历中不存在的经历。只输出严格 JSON，不要 Markdown。"
        "JSON 字段：resume_suggestions、interview_questions、learning_plan、next_best_action。"
        "resume_suggestions 每项包含 title、suggestion、jd_requirement、resume_evidence、risk_level。"
        "interview_questions 每项包含 skill、question。learning_plan 每项包含 skill、task。"
        "next_best_action 包含 title、description、target_skill。\n"
        f"结构化输入：{json.dumps(payload, ensure_ascii=False)}"
    )
