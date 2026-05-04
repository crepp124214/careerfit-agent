import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import (
    AnalysisReport,
    AnalysisTask,
    AnalysisStatus,
    JobDescription,
    ResumeVersion,
    InterviewSession,
    InterviewQuestion,
    InterviewSessionStatus,
    InterviewQuestionStatus,
)
from app.services.interview_service import (
    create_session,
    get_session,
    list_sessions,
    update_question,
    _classify_question,
    _assign_difficulty,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def _create_report_with_questions(db, questions):
    job = JobDescription(title="测试岗位", raw_text="Need Python and FastAPI")
    db.add(job)
    db.flush()
    resume = ResumeVersion(candidate_name="测试", version_label="v1", raw_text="I know Python")
    db.add(resume)
    db.flush()
    task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.success)
    db.add(task)
    db.flush()
    report = AnalysisReport(
        task_id=task.id,
        final_score=50,
        score_breakdown={},
        interview_questions=questions,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def test_classify_question_basic():
    assert _classify_question("请说明你在 FastAPI 上的实践") == "basic"
    assert _classify_question("什么是 RESTful API") == "basic"
    assert _classify_question("解释 Python GIL") == "basic"


def test_classify_question_scenario():
    assert _classify_question("设计一个短链接服务") == "scenario_design"
    assert _classify_question("如何实现分布式限流方案") == "scenario_design"


def test_classify_question_default():
    assert _classify_question("你用过 FastAPI 吗") == "basic"


def test_assign_difficulty():
    assert _assign_difficulty("FastAPI", "basic") == "easy"
    assert _assign_difficulty("RAG", "basic") == "medium"
    assert _assign_difficulty("FastAPI", "scenario_design") == "hard"


def test_create_session(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
        {"skill": "Python", "question": "什么是 Python GIL"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)

    assert session.report_id == report.id
    assert session.total_questions == 2
    assert session.status == InterviewSessionStatus.created
    assert session.completed_questions == 0
    assert len(session.questions) == 2


def test_create_session_idempotent(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    session1 = create_session(db, report_id=report.id, include_rag=False)
    session2 = create_session(db, report_id=report.id, include_rag=False)

    assert session1.id == session2.id


def test_create_session_report_not_found(db):
    with pytest.raises(ValueError, match="report_not_found"):
        create_session(db, report_id=9999, include_rag=False)


def test_create_session_question_classification(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
        {"skill": "Python", "question": "设计一个分布式缓存方案"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)

    q1, q2 = session.questions[0], session.questions[1]
    assert q1.category.value == "basic"
    assert q2.category.value == "scenario_design"
    assert q2.difficulty.value == "hard"


def test_list_sessions(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    create_session(db, report_id=report.id, include_rag=False)

    sessions = list_sessions(db)

    assert len(sessions) == 1


def test_list_sessions_filter_by_status(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    create_session(db, report_id=report.id, include_rag=False)

    sessions = list_sessions(db, status="completed")

    assert len(sessions) == 0


def test_get_session(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    created = create_session(db, report_id=report.id, include_rag=False)

    found = get_session(db, created.id)

    assert found is not None
    assert found.id == created.id


def test_get_session_not_found(db):
    assert get_session(db, 9999) is None


def test_update_question_status(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)
    question = session.questions[0]

    updated = update_question(db, session_id=session.id, question_id=question.id, new_status="practicing")

    assert updated.status == InterviewQuestionStatus.practicing


def test_update_question_invalid_transition(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)
    question = session.questions[0]

    with pytest.raises(ValueError, match="invalid_transition"):
        update_question(db, session_id=session.id, question_id=question.id, new_status="completed")


def test_update_question_notes(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)
    question = session.questions[0]

    updated = update_question(db, session_id=session.id, question_id=question.id, notes="需要加强")

    assert updated.notes == "需要加强"


def test_update_question_progress_tracking(db):
    report = _create_report_with_questions(db, [
        {"skill": "FastAPI", "question": "请说明你在 FastAPI 上的实践"},
        {"skill": "Python", "question": "什么是 Python GIL"},
    ])
    session = create_session(db, report_id=report.id, include_rag=False)
    q1, q2 = session.questions[0], session.questions[1]

    update_question(db, session_id=session.id, question_id=q1.id, new_status="practicing")

    db.refresh(session)
    assert session.status == InterviewSessionStatus.in_progress

    update_question(db, session_id=session.id, question_id=q1.id, new_status="completed")

    db.refresh(session)
    assert session.completed_questions == 1

    update_question(db, session_id=session.id, question_id=q2.id, new_status="practicing")
    update_question(db, session_id=session.id, question_id=q2.id, new_status="completed")

    db.refresh(session)
    assert session.completed_questions == 2
    assert session.status == InterviewSessionStatus.completed


def test_update_question_not_found(db):
    with pytest.raises(ValueError, match="question_not_found"):
        update_question(db, session_id=1, question_id=9999, new_status="practicing")
