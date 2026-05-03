from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import AnalysisReport, LearningTask, LearningTaskStatus


def list_learning_tasks(db: Session) -> list[LearningTask]:
    return list(db.query(LearningTask).order_by(LearningTask.created_at.desc()).all())


def _evidence_refs_for(report: AnalysisReport, skill: str) -> list[dict]:
    refs = []
    for item in report.evidence:
        if item.get("skill") == skill:
            refs.append(
                {
                    "skill": item.get("skill"),
                    "level": item.get("level"),
                    "score": item.get("score"),
                }
            )
    return refs


def _tasks_from_report(report: AnalysisReport) -> list[dict]:
    tasks = []
    for item in report.learning_plan:
        skill = item.get("skill") or "general"
        tasks.append(
            {
                "title": item.get("task") or f"补强 {skill} 的可验证证据",
                "dimension": skill,
                "rationale": "来自分析报告的学习计划。",
                "evidence_refs": _evidence_refs_for(report, skill),
            }
        )

    if tasks:
        return tasks

    for gap in report.gaps:
        skill = gap.get("skill") or "general"
        tasks.append(
            {
                "title": f"补齐 {skill} 的可验证证据",
                "dimension": skill,
                "rationale": gap.get("reason") or "来自分析报告的能力缺口。",
                "evidence_refs": _evidence_refs_for(report, skill),
            }
        )

    if tasks:
        return tasks

    action = report.next_best_action or {}
    title = action.get("title") or "创建下一版简历并重新分析"
    return [
        {
            "title": title,
            "dimension": action.get("target_skill") or "next_best_action",
            "rationale": action.get("description") or "来自报告的下一步行动建议。",
            "evidence_refs": [],
        }
    ]


def generate_learning_tasks(db: Session, task_id: int) -> list[LearningTask]:
    report = db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).one_or_none()
    if report is None:
        raise ValueError("report_not_found")

    existing = (
        db.query(LearningTask)
        .filter(LearningTask.source_report_id == report.id)
        .order_by(LearningTask.id)
        .all()
    )
    if existing:
        return list(existing)

    now = datetime.now(timezone.utc)
    tasks = [
        LearningTask(
            source_task_id=report.task_id,
            source_report_id=report.id,
            title=item["title"],
            dimension=item["dimension"],
            rationale=item["rationale"],
            status=LearningTaskStatus.not_started,
            evidence_refs=item["evidence_refs"],
            task_metadata={"schema_version": "1"},
            created_at=now,
            updated_at=now,
        )
        for item in _tasks_from_report(report)
    ]
    db.add_all(tasks)
    db.commit()
    for task in tasks:
        db.refresh(task)
    return tasks


ALLOWED_TRANSITIONS = {
    LearningTaskStatus.not_started: {LearningTaskStatus.doing, LearningTaskStatus.paused},
    LearningTaskStatus.doing: {LearningTaskStatus.done, LearningTaskStatus.paused},
    LearningTaskStatus.paused: {LearningTaskStatus.doing},
    LearningTaskStatus.done: set(),
}


def update_learning_task_status(
    db: Session, task_id: int, status: LearningTaskStatus
) -> LearningTask:
    task = db.get(LearningTask, task_id)
    if task is None:
        raise ValueError("learning_task_not_found")

    if status != task.status and status not in ALLOWED_TRANSITIONS[task.status]:
        raise ValueError("invalid_status_transition")

    task.status = status
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task
