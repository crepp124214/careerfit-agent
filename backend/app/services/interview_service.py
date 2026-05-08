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
from app.schemas.interview import InterviewQuestionRead
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


# ========== 新增：独立面试功能服务层（支持多模式工作流）==========

import logging
from typing import List, Optional

from app.agents.langgraph_runner import LangGraphRunner
from app.agents.workflow_mode import WorkflowMode

logger = logging.getLogger(__name__)


class InterviewService:
    """
    独立面试功能服务层 - 支持智能引用机制
    
    职责：
    1. 封装独立面试题生成的业务逻辑
    2. 处理输入验证和数据转换
    3. 支持从分析报告引用上下文
    4. 管理面试题会话
    """

    def __init__(self):
        self._runner_cache = {}

    async def generate_questions(self, request, db: Session) -> dict:
        """
        生成面试题（支持引用分析报告）
        
        支持两种模式：
        1. 引用模式：提供 source_report_id，自动从报告中提取 JD/简历/技能
        2. 手动模式：直接提供 skills, jd_context, resume_context
        
        双数据源策略：
        - technical/behavioral/scenario → 基于 JD 生成
        - project_deep_dive → 基于简历生成
        """
        from app.schemas.interview import InterviewQuestionGenerateRequest, InterviewQuestionRead
        
        if request.source_report_id:
            logger.info(f"[InterviewService] 使用引用模式: report_id={request.source_report_id}")
            report = self._get_report(db, request.source_report_id)
            if not report:
                raise ValueError(f"找不到分析报告: {request.source_report_id}")
            
            # 从报告中自动提取上下文
            skills = request.skills or self._extract_skills(report)
            target_job = getattr(report.task.job, 'title', '') if report.task and hasattr(report.task, 'job') and report.task.job else ""
            
            # 提取 JD 和简历文本
            jd_context = request.jd_context or ""
            resume_context = request.resume_context or ""
            
            # 尝试从任务对象获取原始文本
            if not jd_context and report.task and hasattr(report.task, 'job') and report.task.job:
                jd_context = getattr(report.task.job, 'raw_text', "") or ""
            if not resume_context and report.task and hasattr(report.task, 'resume') and report.task.resume:
                resume_context = getattr(report.task.resume, 'raw_text', "") or ""
            
            context = {
                "skills": skills,
                "target_job": target_job,
                "jd_context": jd_context,
                "resume_context": resume_context,
                "source": f"report_{request.source_report_id}",
            }
            logger.info(f"[InterviewService] 从报告 #{request.source_report_id} 自动提取上下文: skills={len(skills)}项")
            
        else:
            logger.info("[InterviewService] 使用手动模式")
            context = {
                "skills": request.skills or [],
                "target_job": getattr(request, 'target_job', '') or "",
                "jd_context": getattr(request, 'jd_context', '') or "",
                "resume_context": getattr(request, 'resume_context', '') or "",
                "source": "manual",
            }
        
        # 构建初始状态（独立模式）
        question_types = getattr(request, 'question_types', None) or ["technical", "behavioral", "scenario", "project_deep_dive"]
        difficulty = getattr(request, 'difficulty', 'mixed')
        count = getattr(request, 'count', 10)
        
        initial_state = {
            "_interview_input": {
                **context,
                "question_types": question_types,
                "difficulty": difficulty,
                "count": count,
            }
        }
        
        try:
            logger.info("[InterviewService] Starting INTERVIEW_ONLY workflow...")
            runner = LangGraphRunner(mode=WorkflowMode.INTERVIEW_ONLY)
            result_state, trace = runner.run(initial_state)

            questions = result_state.get("interview_questions", [])

            if not questions:
                logger.warning("[InterviewService] Workflow completed but no questions generated, using fallback")
                questions = self._generate_fallback_questions(context)

            question_list = []
            for i, q in enumerate(questions):
                if isinstance(q, dict):
                    question_list.append(InterviewQuestionRead(
                        id=q.get("id", i + 1),
                        skill=q.get("skill", ""),
                        category=q.get("type", "technical"),
                        difficulty=q.get("difficulty", "medium"),
                        question=q.get("question", ""),
                        source=q.get("source", "unknown"),
                        what_it_tests=q.get("what_it_tests"),
                        ideal_answer_hints=q.get("ideal_answer_hints"),
                        follow_up_suggestions=q.get("follow_up_suggestions"),
                        created_at=None,
                    ))

            logger.info(f"[InterviewService] 成功生成 {len(question_list)} 道题目")

            return {
                "questions": [q.model_dump() for q in question_list],
                "session_id": None,
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source": context.get("source", "manual"),
                    "mode": "INTERVIEW_ONLY",
                    "trace_nodes": len(trace) if trace else 0,
                },
            }

        except Exception as exc:
            logger.error(f"[InterviewService] 生成题目失败: {type(exc).__name__}: {exc}", exc_info=True)
            logger.info("[InterviewService] Using fallback question generation...")
            
            fallback_questions = self._generate_fallback_questions(context)
            
            return {
                "questions": [q.model_dump() for q in fallback_questions],
                "session_id": None,
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source": context.get("source", "manual"),
                    "mode": "FALLBACK",
                    "error": str(exc),
                    "trace_nodes": 0,
                },
            }

    async def generate_prep_plan(self, request, db: Session) -> dict:
        """
        基于选定题目生成准备计划
        
        支持两种模式：
        1. 引用会话：提供 source_session_id，从已保存的题目中选取
        2. 手动模式：直接提供 selected_questions 列表
        """
        selected_questions = []
        
        # 尝试从会话获取题目
        session_id = getattr(request, 'source_session_id', None)
        if session_id:
            session = self._get_session(db, session_id)
            if session and hasattr(session, 'questions'):
                question_ids = getattr(request, 'question_ids', None) or []
                if question_ids:
                    selected_questions = [
                        {
                            "id": q.id,
                            "skill": q.skill,
                            "question": q.question,
                            "category": q.category.value if hasattr(q.category, 'value') else str(q.category),
                            "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                        }
                        for q in session.questions
                        if q.id in question_ids
                    ]
                else:
                    selected_questions = [
                        {
                            "id": q.id,
                            "skill": q.skill,
                            "question": q.question,
                            "category": q.category.value if hasattr(q.category, 'value') else str(q.category),
                            "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                        }
                        for q in session.questions
                    ]
        
        # 如果没有从会话获取到，尝试手动列表
        if not selected_questions and hasattr(request, 'selected_questions') and request.selected_questions:
            selected_questions = request.selected_questions
        
        if not selected_questions:
            raise ValueError("未提供有效的题目列表或会话ID")
        
        prep_depth = getattr(request, 'prep_depth', 'standard')
        
        # 构建 PREP_ONLY 模式的初始状态
        initial_state = {
            "interview_questions": selected_questions,
            "_prep_input": {
                "selected_questions": selected_questions,
                "prep_depth": prep_depth,
            }
        }
        
        try:
            # 运行 PREP_ONLY 模式
            runner = LangGraphRunner(mode=WorkflowMode.PREP_ONLY)
            result_state, trace = runner.run(initial_state)
            
            prep_plans = result_state.get("learning_plan", [])
            
            logger.info(f"[InterviewService] 成功生成 {len(prep_plans)} 份准备计划")
            
            return {
                "prep_plans": prep_plans,
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "based_on_questions": len(selected_questions),
                    "mode": "PREP_ONLY",
                },
            }
            
        except Exception as exc:
            logger.error(f"[InterviewService] 生成准备计划失败: {type(exc).__name__}: {exc}", exc_info=True)
            raise ValueError(f"生成准备计划失败: {str(exc)}")

    def _get_report(self, db: Session, report_id: int):
        """查询数据库获取分析报告"""
        from app.db.models import AnalysisReport
        return db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()

    def _extract_skills(self, report) -> List[str]:
        """从 match_result 中提取技能列表"""
        score_items = []
        if hasattr(report, 'score_breakdown') and isinstance(report.score_breakdown, dict):
            score_items = report.score_breakdown.get("score_items", [])
        elif hasattr(report, 'match_result') and isinstance(report.match_result, dict):
            score_items = report.match_result.get("score_items", [])
        
        skills = list(set(
            item.get("skill", item.get("skill_key", ""))
            for item in score_items
            if item and (item.get("skill") or item.get("skill_key"))
        ))
        return skills

    def _get_session(self, db: Session, session_id: int):
        """获取已保存的会话"""
        return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

    def _generate_fallback_questions(self, context: dict) -> List[InterviewQuestionRead]:
        """
        Fallback 题目生成（当 LLM 不可用时使用）
        
        基于技能列表生成通用面试题
        """
        skills = context.get("skills", [])
        jd_context = context.get("jd_context", "")
        resume_context = context.get("resume_context", "")
        
        fallback_questions = []
        
        for i, skill in enumerate(skills[:10], start=1):
            if skill.lower() in ["python", "java", "javascript", "typescript"]:
                question = f"请描述你在 {skill} 项目中的经验，并解释你如何处理代码质量和性能优化？"
                what_it_tests = [f"{skill} 熟练度", "项目经验", "问题解决能力"]
            elif skill.lower() in ["react", "vue", "angular", "前端"]:
                question = f"请介绍一个你使用前端框架开发的复杂组件，说明你的设计思路和技术选型？"
                what_it_tests = ["前端框架熟练度", "组件设计能力", "技术决策"]
            elif skill.lower() in ["机器学习", "深度学习", "ml", "ai"]:
                question = f"请描述你在 {skill} 方面的项目经验，包括数据预处理、模型选择和评估方法？"
                what_it_tests = [f"{skill} 理论基础", "实践经验", "工程化能力"]
            else:
                question = f"请详细说明你在 {skill} 方面的技术栈和实践经验？"
                what_it_tests = [f"{skill} 技术深度", "实际应用", "持续学习"]
            
            source = "jd_based" if jd_context else ("resume_based" if resume_context else "unknown")
            
            fallback_questions.append(InterviewQuestionRead(
                id=i,
                skill=skill,
                category="technical",
                difficulty="medium",
                question=question,
                source=source,
                what_it_tests=what_it_tests,
                ideal_answer_hints=None,
                follow_up_suggestions=None,
                created_at=None,
            ))
        
        logger.info(f"[InterviewService] Generated {len(fallback_questions)} fallback questions")
        return fallback_questions


# 创建全局实例（供路由层使用）
interview_service = InterviewService()


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
