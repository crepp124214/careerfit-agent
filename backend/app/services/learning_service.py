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
    """
    从分析报告中提取学习任务/面试准备计划
    
    支持两种格式：
    1. 新格式：prep_plans（基于面试题的准备计划）- 包含 target_question
    2. 旧格式：tasks（基于缺口的学习任务）
    """
    
    learning_plan = report.learning_plan or []
    
    if not learning_plan:
        # 回退到从gaps生成
        return _tasks_from_gaps(report)
    
    # 检测是否是新格式（prep_plans）
    first_item = learning_plan[0] if learning_plan else {}
    is_new_format = 'target_question' in first_item and 'skill_focus' in first_item
    
    if is_new_format:
        return _convert_prep_plans_to_tasks(learning_plan)
    else:
        return _convert_legacy_tasks(learning_plan, report)


def _convert_prep_plans_to_tasks(prep_plans: list) -> list[dict]:
    """将新格式的 prep_plans 转换为 LearningTask 字典"""
    tasks = []
    
    for plan in prep_plans:
        if not isinstance(plan, dict):
            continue
            
        target_question = plan.get('target_question', '')
        skill_focus = plan.get('skill_focus', '')
        prep_items = plan.get('prep_items', [])
        total_time = plan.get('total_prep_time', '')
        priority = plan.get('priority', 'high')
        confidence_boost = plan.get('confidence_boost', '')
        
        # 将准备项转换为行动步骤列表
        specific_actions = []
        for item in (prep_items or []):
            if not isinstance(item, dict):
                continue
            item_type = item.get('type', 'unknown')
            title = item.get('title', '')
            content = item.get('content', '')[:100]
            time_needed = item.get('time_needed', '')
            
            action_text = f"[{item_type}] {title}"
            if content:
                action_text += f": {content}"
            if time_needed:
                action_text += f" ({time_needed})"
            
            specific_actions.append(action_text)
        
        task = {
            'title': f"准备面试题: {(target_question[:50])}..." if target_question else f"{skill_focus}面试准备",
            'dimension': skill_focus or 'interview_prep',
            'rationale': confidence_boost or f"基于面试题的个性化准备计划",
            'evidence_refs': [],
            
            # 新格式字段
            'skill': skill_focus,
            'target_question': target_question,
            'specific_actions': specific_actions if specific_actions else None,
            'time_investment': total_time,
            'expected_outcome': confidence_boost,
            'is_interview_prep': True,
        }
        
        tasks.append(task)
    
    return tasks if tasks else _fallback_task(report)


def _convert_legacy_tasks(tasks: list, report: AnalysisReport) -> list[dict]:
    """转换旧格式的学习任务"""
    result = []
    for item in tasks:
        skill = item.get('skill') or item.get('target_skill') or "general"
        result.append({
            'title': item.get('task') or item.get('action_title') or f"补强 {skill} 的可验证证据",
            'dimension': skill,
            'rationale': item.get('expected_outcome') or "来自分析报告的学习计划。",
            'evidence_refs': _evidence_refs_for(report, skill),
            
            # 尝试提取可能存在的新字段
            'skill': skill,
            'target_question': None,
            'specific_actions': item.get('specific_actions'),
            'time_investment': item.get('time_investment'),
            'expected_outcome': item.get('expected_outcome'),
            'is_interview_prep': False,
        })
    return result if result else _fallback_task(report)


def _tasks_from_gaps(report: AnalysisReport) -> list[dict]:
    """从 gaps 生成回退任务"""
    gaps = report.gaps or []
    if gaps:
        return [
            {
                'title': f"补齐 {gap.get('skill', gap.get('skill_key', 'general'))} 的能力",
                'dimension': gap.get('skill', 'general'),
                'rationale': gap.get('reason') or '来自分析报告的能力缺口。',
                'evidence_refs': [],
                'is_interview_prep': False,
            }
            for gap in gaps[:5]
        ]
    
    return _fallback_task(report)


def _fallback_task(report: AnalysisReport) -> list[dict]:
    """最终回退：使用 Next Best Action"""
    action = report.next_best_action or {}
    title = action.get('title') or "查看报告中的面试题和建议"
    return [{
        'title': title,
        'dimension': action.get('target_skill') or 'next_best_action',
        'rationale': action.get('description') or '来自报告的下一步行动建议。',
        'evidence_refs': [],
        'is_interview_prep': False,
    }]


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
    raw_items = _tasks_from_report(report)
    
    tasks = [
        LearningTask(
            source_task_id=report.task_id,
            source_report_id=report.id,
            title=item["title"],
            dimension=item["dimension"],
            rationale=item["rationale"],
            status=LearningTaskStatus.not_started,
            evidence_refs=item.get("evidence_refs", []),
            
            # 面试准备计划字段
            skill=item.get("skill"),
            target_question=item.get("target_question"),
            specific_actions=item.get("specific_actions"),
            time_investment=item.get("time_investment"),
            expected_outcome=item.get("expected_outcome"),
            is_interview_prep=item.get("is_interview_prep", False),
            
            task_metadata={"schema_version": "2"},  # 标记为新版本
            created_at=now,
            updated_at=now,
        )
        for item in raw_items
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
