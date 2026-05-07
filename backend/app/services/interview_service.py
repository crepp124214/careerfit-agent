from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import (
    AnalysisReport,
    InterviewQuestion,
    InterviewQuestionCategory,
    InterviewQuestionDifficulty,
    InterviewQuestionStatus,
    InterviewSession,
    InterviewSessionStatus,
)
from app.core.config import get_settings
from app.llm.agent_schemas import AnswerScoreOutput
from app.llm.agent_service import run_structured_agent
from app.llm.service import build_llm_client
from app.rag.retrieval import retrieve_by_skill

VALID_TRANSITIONS: dict[str, set[str]] = {
    "not_started": {"practicing", "skipped"},
    "practicing": {"completed", "skipped"},
    "completed": set(),
    "skipped": set(),
}

BASIC_PATTERNS = re.compile(r"请说明|请描述|请解释|什么是|解释|定义|区别|比较")
SCENARIO_PATTERNS = re.compile(r"设计|如何实现|方案|架构|如何构建|如何设计")


def _classify_question(question_text: str) -> str:
    if SCENARIO_PATTERNS.search(question_text):
        return "scenario_design"
    if BASIC_PATTERNS.search(question_text):
        return "basic"
    return "basic"


def _assign_difficulty(skill: str, category: str) -> str:
    if category == "scenario_design":
        return "hard"
    hard_skills = {"LangGraph", "RAG", "Prompt Engineering", "Vector Database"}
    if skill in hard_skills:
        return "medium"
    return "easy"


def _enrich_from_rag(db: Session, skills: list[str]) -> list[dict]:
    rag_questions = []
    seen_questions = set()
    for skill in skills:
        results = retrieve_by_skill(db, skill, top_k=2, doc_type="interview")
        for result in results:
            content = result.get("content_snippet", "")
            title = result.get("title", "")
            if content in seen_questions:
                continue
            seen_questions.add(content)
            sentences = re.split(r"(?<=[.!?。！？])\s*", content)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue
                if "?" in sentence or "？" in sentence or "题" in sentence:
                    rag_questions.append({
                        "skill": skill,
                        "question": sentence,
                        "answer_hint": None,
                        "follow_ups": [],
                        "source": "rag",
                    })
                    break
    return rag_questions


def create_session(db: Session, report_id: int, include_rag: bool = True) -> InterviewSession:
    existing = db.query(InterviewSession).filter(InterviewSession.report_id == report_id).first()
    if existing:
        return existing

    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if report is None:
        raise ValueError("report_not_found")

    task = report.task
    job_title = task.job.title if task and task.job else "未知岗位"

    report_questions = report.interview_questions or []
    skills = list({q.get("skill", "") for q in report_questions if q.get("skill")})

    rag_questions = []
    if include_rag and skills:
        rag_questions = _enrich_from_rag(db, skills)

    all_questions_data = []
    seen_questions = set()
    for q in report_questions:
        question_text = q.get("question", "")
        if question_text in seen_questions:
            continue
        seen_questions.add(question_text)
        category = _classify_question(question_text)
        difficulty = _assign_difficulty(q.get("skill", ""), category)
        all_questions_data.append({
            "skill": q.get("skill", ""),
            "category": category,
            "difficulty": difficulty,
            "question": question_text,
            "answer_hint": None,
            "follow_ups": [],
            "source": "report",
        })

    for q in rag_questions:
        question_text = q.get("question", "")
        if question_text in seen_questions:
            continue
        seen_questions.add(question_text)
        category = _classify_question(question_text)
        difficulty = _assign_difficulty(q.get("skill", ""), category)
        all_questions_data.append({
            "skill": q.get("skill", ""),
            "category": category,
            "difficulty": difficulty,
            "question": question_text,
            "answer_hint": q.get("answer_hint"),
            "follow_ups": q.get("follow_ups", []),
            "source": q.get("source", "rag"),
        })

    session = InterviewSession(
        report_id=report_id,
        job_title=job_title,
        status=InterviewSessionStatus.created,
        total_questions=len(all_questions_data),
        completed_questions=0,
    )
    db.add(session)
    db.flush()

    for idx, q_data in enumerate(all_questions_data):
        question = InterviewQuestion(
            session_id=session.id,
            skill=q_data["skill"],
            category=InterviewQuestionCategory(q_data["category"]),
            difficulty=InterviewQuestionDifficulty(q_data["difficulty"]),
            question=q_data["question"],
            answer_hint=q_data.get("answer_hint"),
            follow_ups=q_data.get("follow_ups", []),
            source=q_data.get("source", "report"),
            status=InterviewQuestionStatus.not_started,
            sort_order=idx,
        )
        db.add(question)

    db.commit()
    db.refresh(session)
    return session


def list_sessions(
    db: Session,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[InterviewSession]:
    q = db.query(InterviewSession).order_by(InterviewSession.created_at.desc())
    if status:
        q = q.filter(InterviewSession.status == status)
    return q.offset(offset).limit(limit).all()


def get_session(db: Session, session_id: int) -> InterviewSession | None:
    return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()


def update_question(
    db: Session,
    session_id: int,
    question_id: int,
    new_status: str | None = None,
    notes: str | None = None,
) -> InterviewQuestion:
    question = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.id == question_id, InterviewQuestion.session_id == session_id)
        .first()
    )
    if question is None:
        raise ValueError("question_not_found")

    if new_status is not None:
        current = question.status.value if hasattr(question.status, "value") else str(question.status)
        allowed = VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise ValueError(f"invalid_transition:{current}->{new_status}")
        question.status = InterviewQuestionStatus(new_status)

    if notes is not None:
        question.notes = notes

    db.flush()

    session = db.query(InterviewSession).filter(InterviewSession.id == question.session_id).first()
    completed_count = sum(
        1 for q in session.questions
        if q.status in (InterviewQuestionStatus.completed, InterviewQuestionStatus.skipped)
    )
    active_count = sum(
        1 for q in session.questions
        if q.status == InterviewQuestionStatus.practicing
    )
    session.completed_questions = completed_count

    if session.status == InterviewSessionStatus.created and (completed_count > 0 or active_count > 0):
        session.status = InterviewSessionStatus.in_progress
    if session.completed_questions >= session.total_questions:
        session.status = InterviewSessionStatus.completed

    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(question)
    return question


def score_answer(question: InterviewQuestion, answer_text: str) -> dict:
    skill_name = question.skill
    question_text = question.question

    try:
        settings = get_settings()
        client = build_llm_client(settings)
    except Exception:
        client = None

    if client is None:
        return _score_fallback()

    prompt = (
        f"你是一位专业的面试评分官。请根据以下信息对候选人的回答进行评分。\n\n"
        f"面试技能方向：{skill_name}\n"
        f"面试题目：{question_text}\n"
        f"候选人的回答：{answer_text}\n\n"
        f"请从以下三个维度评分：\n"
        f"1. 正确性（correctness）：回答内容是否准确，是否有理解错误\n"
        f"2. 完整性（completeness）：回答是否覆盖了题目的核心要点\n"
        f"3. 表达清晰度（clarity）：表达是否有条理、清晰易懂\n\n"
        f"综合评分（score）：0-100 整数\n"
        f"改进建议（improvement_suggestion）：指出可以如何改进回答"
    )

    try:
        result = run_structured_agent(
            client=client,
            agent_role="面试评分官",
            prompt=prompt,
            output_model=AnswerScoreOutput,
        )
        if result is None:
            return _score_fallback()
        score = max(0, min(100, result.score))
        return {
            "score": score,
            "correctness_feedback": result.correctness_feedback,
            "completeness_feedback": result.completeness_feedback,
            "clarity_feedback": result.clarity_feedback,
            "improvement_suggestion": result.improvement_suggestion,
        }
    except Exception:
        return _score_fallback()


def _score_fallback() -> dict:
    return {
        "score": 50,
        "correctness_feedback": "无法评估正确性，请参考标准答案自行判断。",
        "completeness_feedback": "无法评估完整性，建议覆盖题目的所有核心要点。",
        "clarity_feedback": "无法评估清晰度，建议用自己的话复述核心概念。",
        "improvement_suggestion": "继续练习，尝试用自己的话复述核心概念，并注意结构化表达。",
    }


def submit_answer(
    db: Session,
    session_id: int,
    question_id: int,
    answer_text: str,
) -> InterviewQuestion:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if session is None:
        raise ValueError("session_not_found")

    question = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.id == question_id, InterviewQuestion.session_id == session_id)
        .first()
    )
    if question is None:
        raise ValueError("question_not_found")

    scoring_result = score_answer(question, answer_text)

    question.answer_text = answer_text
    question.answer_score = scoring_result["score"]
    question.answer_feedback = {
        "correctness_feedback": scoring_result["correctness_feedback"],
        "completeness_feedback": scoring_result["completeness_feedback"],
        "clarity_feedback": scoring_result["clarity_feedback"],
        "improvement_suggestion": scoring_result["improvement_suggestion"],
    }
    question.answer_submitted_at = datetime.now(timezone.utc)
    question.attempt_count = (question.attempt_count or 0) + 1

    if question.status == InterviewQuestionStatus.not_started:
        question.status = InterviewQuestionStatus.practicing

    db.flush()

    completed_count = sum(
        1 for q in session.questions
        if q.status in (InterviewQuestionStatus.completed, InterviewQuestionStatus.skipped)
    )
    active_count = sum(
        1 for q in session.questions
        if q.status == InterviewQuestionStatus.practicing
    )
    session.completed_questions = completed_count

    if session.status == InterviewSessionStatus.created and (completed_count > 0 or active_count > 0):
        session.status = InterviewSessionStatus.in_progress
    if session.completed_questions >= session.total_questions:
        session.status = InterviewSessionStatus.completed

    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(question)
    return question
