import difflib

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import AnalysisReport, AnalysisTask, ResumeVersion
from app.schemas.resumes import (
    ResumeDiffResponse,
    ResumeDiffResumeRef,
    ResumeDiffSection,
    ResumeDiffSummary,
    ResumeScoreContext,
)


def compute_line_diff(from_text: str, to_text: str) -> tuple[list[ResumeDiffSection], ResumeDiffSummary]:
    from_lines = from_text.splitlines()
    to_lines = to_text.splitlines()

    matcher = difflib.SequenceMatcher(None, from_lines, to_lines)
    sections: list[ResumeDiffSection] = []
    added = 0
    removed = 0
    unchanged = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                sections.append(
                    ResumeDiffSection(type="unchanged", text=from_lines[i], old_line=i + 1, new_line=j + 1)
                )
                unchanged += 1
        elif tag == "replace":
            for i in range(i1, i2):
                sections.append(
                    ResumeDiffSection(type="removed", text=from_lines[i], old_line=i + 1, new_line=None)
                )
                removed += 1
            for j in range(j1, j2):
                sections.append(
                    ResumeDiffSection(type="added", text=to_lines[j], old_line=None, new_line=j + 1)
                )
                added += 1
        elif tag == "delete":
            for i in range(i1, i2):
                sections.append(
                    ResumeDiffSection(type="removed", text=from_lines[i], old_line=i + 1, new_line=None)
                )
                removed += 1
        elif tag == "insert":
            for j in range(j1, j2):
                sections.append(
                    ResumeDiffSection(type="added", text=to_lines[j], old_line=None, new_line=j + 1)
                )
                added += 1

    summary = ResumeDiffSummary(added_lines=added, removed_lines=removed, unchanged_lines=unchanged)
    return sections, summary


def get_latest_report_for_resume(db: Session, resume_id: int) -> AnalysisReport | None:
    return (
        db.query(AnalysisReport)
        .join(AnalysisTask)
        .filter(AnalysisTask.resume_id == resume_id)
        .filter(AnalysisTask.status == "success")
        .order_by(desc(AnalysisReport.created_at))
        .first()
    )


def compute_score_context(db: Session, from_resume_id: int, to_resume_id: int) -> ResumeScoreContext:
    from_report = get_latest_report_for_resume(db, from_resume_id)
    to_report = get_latest_report_for_resume(db, to_resume_id)

    if from_report is None or to_report is None:
        missing = []
        if from_report is None:
            missing.append("from")
        if to_report is None:
            missing.append("to")
        reason = f"{' 和 '.join(missing)} 版本暂无分析报告"
        return ResumeScoreContext(available=False, reason=reason)

    return ResumeScoreContext(
        available=True,
        from_score=from_report.final_score,
        to_score=to_report.final_score,
        from_report_created_at=from_report.created_at,
        to_report_created_at=to_report.created_at,
    )


def compare_resumes(db: Session, from_id: int, to_id: int) -> ResumeDiffResponse | None:
    from_resume = db.query(ResumeVersion).filter(ResumeVersion.id == from_id).first()
    to_resume = db.query(ResumeVersion).filter(ResumeVersion.id == to_id).first()

    if from_resume is None or to_resume is None:
        return None

    sections, summary = compute_line_diff(from_resume.raw_text, to_resume.raw_text)
    score_context = compute_score_context(db, from_id, to_id)

    return ResumeDiffResponse(
        schema_version="1",
        from_resume=ResumeDiffResumeRef(
            id=from_resume.id,
            version_label=from_resume.version_label,
            candidate_name=from_resume.candidate_name,
        ),
        to_resume=ResumeDiffResumeRef(
            id=to_resume.id,
            version_label=to_resume.version_label,
            candidate_name=to_resume.candidate_name,
        ),
        summary=summary,
        sections=sections,
        score_context=score_context,
    )
