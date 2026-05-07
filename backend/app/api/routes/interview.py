from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interview import (
    InterviewAnswerSubmit,
    InterviewAnswerSubmitResponse,
    InterviewQuestionUpdate,
    InterviewSessionCreate,
    InterviewSessionCreateResponse,
    InterviewSessionDetailRead,
    InterviewSessionListResponse,
    InterviewSessionRead,
)
from app.services.interview_service import create_session, get_session, list_sessions, submit_answer, update_question

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _session_to_read(session) -> InterviewSessionRead:
    return InterviewSessionRead(
        id=session.id,
        report_id=session.report_id,
        job_title=session.job_title,
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
        total_questions=session.total_questions,
        completed_questions=session.completed_questions,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
    )


@router.post("/sessions", response_model=InterviewSessionCreateResponse)
def create_interview_session(
    payload: InterviewSessionCreate, db: Session = Depends(get_db)
):
    try:
        session = create_session(db, report_id=payload.report_id, include_rag=payload.include_rag)
    except ValueError as exc:
        if "report_not_found" in str(exc):
            raise HTTPException(status_code=404, detail="report_not_found")
        raise
    return InterviewSessionCreateResponse(session=_session_to_read(session))


@router.get("/sessions", response_model=InterviewSessionListResponse)
def list_interview_sessions(
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    sessions = list_sessions(db, status=status, limit=limit, offset=offset)
    return InterviewSessionListResponse(
        items=[_session_to_read(s) for s in sessions]
    )


@router.get("/sessions/{session_id}", response_model=InterviewSessionDetailRead)
def get_interview_session(session_id: int, db: Session = Depends(get_db)):
    session = get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session_not_found")
    from app.schemas.interview import InterviewQuestionRead

    questions = [
        InterviewQuestionRead(
            id=q.id,
            skill=q.skill,
            category=q.category.value if hasattr(q.category, "value") else str(q.category),
            difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
            question=q.question,
            answer_hint=q.answer_hint,
            follow_ups=q.follow_ups or [],
            source=q.source,
            status=q.status.value if hasattr(q.status, "value") else str(q.status),
            notes=q.notes,
            sort_order=q.sort_order,
            answer_text=q.answer_text,
            answer_score=q.answer_score,
            answer_feedback=q.answer_feedback,
            answer_submitted_at=q.answer_submitted_at.isoformat() if q.answer_submitted_at else None,
            attempt_count=q.attempt_count,
        )
        for q in session.questions
    ]
    return InterviewSessionDetailRead(
        id=session.id,
        report_id=session.report_id,
        job_title=session.job_title,
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
        total_questions=session.total_questions,
        completed_questions=session.completed_questions,
        questions=questions,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else None,
    )


@router.patch("/sessions/{session_id}/questions/{question_id}")
def update_interview_question(
    session_id: int,
    question_id: int,
    payload: InterviewQuestionUpdate,
    db: Session = Depends(get_db),
):
    try:
        question = update_question(
            db,
            session_id=session_id,
            question_id=question_id,
            new_status=payload.status,
            notes=payload.notes,
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "question_not_found" in error_msg:
            raise HTTPException(status_code=404, detail="question_not_found")
        if "invalid_transition" in error_msg:
            raise HTTPException(status_code=422, detail=error_msg)
        raise
    return {
        "id": question.id,
        "status": question.status.value if hasattr(question.status, "value") else str(question.status),
        "notes": question.notes,
    }


@router.post("/sessions/{session_id}/questions/{question_id}/submit", response_model=InterviewAnswerSubmitResponse)
def submit_interview_answer(
    session_id: int,
    question_id: int,
    payload: InterviewAnswerSubmit,
    db: Session = Depends(get_db),
):
    try:
        question = submit_answer(
            db,
            session_id=session_id,
            question_id=question_id,
            answer_text=payload.answer_text,
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "question_not_found" in error_msg:
            raise HTTPException(status_code=404, detail="question_not_found")
        if "session_not_found" in error_msg:
            raise HTTPException(status_code=404, detail="session_not_found")
        raise
    return InterviewAnswerSubmitResponse(
        id=question.id,
        status=question.status.value if hasattr(question.status, "value") else str(question.status),
        answer_text=question.answer_text,
        answer_score=question.answer_score,
        answer_feedback=question.answer_feedback,
        attempt_count=question.attempt_count,
    )
