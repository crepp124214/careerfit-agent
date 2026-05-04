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
