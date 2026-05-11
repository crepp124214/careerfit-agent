"""
独立的面试题库 API Schema
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestionGenerateRequest(BaseModel):
    """生成面试题的请求"""

    skills: list[str] = Field(
        default=[],
        max_length=10,
        description="目标技能列表，如 ['SQL', 'Python', 'A/B测试']。引用模式下可省略，自动从报告提取",
    )

    target_job: str = Field(
        default="",
        max_length=100,
        description="目标岗位名称，如'数据分析师'"
    )

    jd_context: str = Field(
        default="",
        max_length=5000,
        description="JD 岗位描述文本（用于生成技术/行为/场景题）"
    )

    resume_context: str = Field(
        default="",
        max_length=5000,
        description="简历或项目经历文本（用于生成项目深挖题）"
    )

    source_report_id: int | None = Field(
        default=None,
        description="分析报告 ID（可选，用于从报告中自动提取上下文）"
    )

    question_types: list[str] | None = Field(
        default=None,
        description="题型过滤，可选：technical, behavioral, scenario, project_deep_dive"
    )

    difficulty: str = Field(
        default="mixed",
        pattern="^(easy|medium|hard|mixed)$",
        description="难度设置"
    )

    count: int = Field(
        default=10,
        ge=3,
        le=20,
        description="生成题目数量"
    )

    model_config = ConfigDict(extra="forbid")


class InterviewQuestion(BaseModel):
    """单道面试题"""
    id: int
    skill: str
    type: str  # technical / behavioral / scenario / project_deep_dive
    difficulty: str  # easy / medium / hard
    question: str
    
    # 可选的增强字段
    what_it_tests: list[str] | None = None
    ideal_answer_hints: list[str] | None = None
    follow_up_suggestions: list[str] | None = None
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== 以下为原有的面试会话管理 Schema（保持向后兼容）==========

class InterviewAnswerSubmit(BaseModel):
    """提交面试题答案"""
    answer_text: str = Field(..., min_length=10, max_length=2000)

    model_config = ConfigDict(extra="forbid")


class InterviewAnswerSubmitResponse(BaseModel):
    """提交答案后的响应"""
    id: int
    status: str
    answer_text: str
    answer_score: float | None = None
    answer_feedback: str | None = None
    attempt_count: int = 1


class InterviewQuestionUpdate(BaseModel):
    """更新面试题状态"""
    status: str | None = Field(default=None, pattern="^(not_started|in_progress|answered|skipped)$")
    notes: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")


class InterviewSessionCreate(BaseModel):
    """创建面试会话"""
    report_id: int = Field(..., gt=0)
    include_rag: bool = Field(default=True, description="是否包含 RAG 检索的知识库证据")

    model_config = ConfigDict(extra="forbid")


class InterviewSessionCreateResponse(BaseModel):
    """创建会话成功响应"""
    session: "InterviewSessionRead"


class InterviewSessionRead(BaseModel):
    """面试会话基本信息"""
    id: int
    report_id: int
    job_title: str
    status: str
    total_questions: int
    completed_questions: int
    created_at: str
    updated_at: str | None = None


class InterviewSessionDetailRead(BaseModel):
    """面试会话详情（含题目列表）"""
    id: int
    report_id: int
    job_title: str
    status: str
    total_questions: int
    completed_questions: int
    questions: list["InterviewQuestionRead"]
    created_at: str
    updated_at: str | None = None


class InterviewSessionListResponse(BaseModel):
    """面试会话列表响应"""
    items: list[InterviewSessionRead]


class InterviewQuestionRead(BaseModel):
    """面试题响应（单个）- 增强版（支持原有会话管理功能）"""
    id: int
    skill: str
    category: str  # technical / behavioral / scenario / project_deep_dive
    difficulty: str  # easy / medium / hard
    question: str
    answer_hint: str | None = None
    follow_ups: list[str] = []
    source: str | None = None  # jd_based / resume_based / rag
    status: str = "not_started"  # not_started / in_progress / answered / skipped
    notes: str | None = None
    sort_order: int = 0
    answer_text: str | None = None
    answer_score: float | None = None
    answer_feedback: str | None = None
    answer_submitted_at: str | None = None
    attempt_count: int = 0
    what_it_tests: list[str] | None = None
    ideal_answer_hints: list[str] | None = None
    follow_up_suggestions: list[str] | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class InterviewQuestionsResponse(BaseModel):
    """面试题列表响应"""
    questions: list[InterviewQuestionRead]
    total_count: int
    generation_meta: dict | None = None  # 包含按类型/难度的统计


class InterviewPrepGenerateRequest(BaseModel):
    """基于选定题目生成准备计划的请求"""
    question_ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="选定的面试题ID列表"
    )
    
    prep_depth: str = Field(
        default="standard",
        pattern="^(quick|standard|comprehensive)$",
        description="准备深度：quick/standard/comprehensive"
    )

    model_config = ConfigDict(extra="forbid")


class InterviewPrepItem(BaseModel):
    """单个准备项"""
    type: str  # knowledge_review / case_preparation / practice
    title: str
    content: str
    key_points: list[str] | None = None
    template: str | None = None
    checklist: list[str] | None = None
    resources: list[dict] | None = None
    method: str | None = None
    rounds: int | None = None
    time_needed: str | None = None
    priority: str  # must_have / critical / recommended


class InterviewPrepPlan(BaseModel):
    """单个面试题的准备计划"""
    target_question_id: int
    target_question: str
    skill_focus: str
    question_type: str
    difficulty: str
    
    prep_items: list[InterviewPrepItem]
    total_prep_time: str
    priority: str  # high / medium / low
    confidence_before: str | None = None
    confidence_after: str | None = None


class InterviewPrepPlanRead(BaseModel):
    """准备计划响应（单个）"""
    id: int
    source_question_ids: list[int]
    skill_focus: str
    total_prep_time: str
    status: str  # not_started / in_progress / completed
    prep_plans: list[InterviewPrepPlan]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
