"""
独立的面试题生成 API 路由
支持：面试题生成、准备计划生成、一站式面试包
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interview import (
    InterviewQuestionGenerateRequest,
    InterviewQuestionsResponse,
    InterviewPrepGenerateRequest,
    InterviewPrepPlanRead,
)
from app.services.interview_service import interview_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview", tags=["interview-new"])


@router.post("/questions/generate")
async def generate_interview_questions(
    payload: InterviewQuestionGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    生成独立面试题
    
    支持两种模式：
    1. 手动模式：提供 skills, jd_context, resume_context
    2. 引用模式：提供 source_report_id（自动从报告中提取上下文）
    
    双数据源策略：
    - technical/behavioral/scenario 题型 → 基于 JD 生成
    - project_deep_dive 题型 → 基于简历生成
    """
    try:
        logger.info(
            f"[generate_questions] 收到请求: skills={payload.skills}, "
            f"question_types={payload.question_types}, count={payload.count}, "
            f"source_report_id={payload.source_report_id}"
        )
        
        result = await interview_service.generate_questions(payload, db)
        
        logger.info(f"[generate_questions] 成功生成 {len(result.get('questions', []))} 道题目")
        
        return {
            "success": True,
            "data": result,
        }
    
    except ValueError as exc:
        logger.warning(f"[generate_questions] 参数验证失败: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    
    except Exception as exc:
        logger.error(f"[generate_questions] 内部错误: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(exc)}")


@router.post("/prep-plan/generate")
async def generate_prep_plan(
    payload: InterviewPrepGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    基于选定题目生成准备计划
    
    支持两种模式：
    1. 手动模式：提供 selected_questions 列表
    2. 引用模式：提供 source_session_id（从已生成的面试题会话中获取）
    """
    try:
        logger.info(
            f"[generate_prep_plan] 收到请求: question_ids={payload.question_ids}, "
            f"source_session_id={getattr(payload, 'source_session_id', None)}, "
            f"prep_depth={payload.prep_depth}"
        )
        
        result = await interview_service.generate_prep_plan(payload, db)
        
        prep_plans = result.get("prep_plans", [])
        logger.info(f"[generate_prep_plan] 成功生成 {len(prep_plans)} 份准备计划")
        
        return {
            "success": True,
            "data": result,
        }
    
    except ValueError as exc:
        logger.warning(f"[generate_prep_plan] 参数验证失败: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    
    except Exception as exc:
        logger.error(f"[generate_prep_plan] 内部错误: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(exc)}")


@router.post("/package/generate")
async def generate_interview_package(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    一站式生成面试包（面试题 + 准备计划）
    
    等同于依次调用 questions/generate + prep-plan/generate
    但在服务端原子性执行，确保一致性
    """
    try:
        logger.info("[generate_package] 收到一站式面试包请求")
        
        # TODO: 实现一站式逻辑
        # 目前先返回 501
        raise NotImplementedError("一站式面试包功能开发中，请分别调用 questions/generate 和 prep-plan/generate")
    
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="功能尚未实现，请使用分步接口")
    
    except Exception as exc:
        logger.error(f"[generate_package] 内部错误: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(exc)}")


@router.get("/sessions/{session_id}")
async def get_interview_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    """获取已保存的面试题会话详情"""
    try:
        from app.services.interview_service import interview_service
        
        session = interview_service._get_session(db, session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")
        
        return {
            "success": True,
            "data": {
                "session_id": session.id,
                "report_id": session.report_id,
                "job_title": session.job_title,
                "status": session.status.value if hasattr(session.status, "value") else str(session.status),
                "total_questions": session.total_questions,
                "created_at": session.created_at.isoformat() if session.created_at else "",
            }
        }
    
    except HTTPException:
        raise
    
    except Exception as exc:
        logger.error(f"[get_session] 错误: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
