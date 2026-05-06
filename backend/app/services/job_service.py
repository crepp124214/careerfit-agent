import re
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jobs import JobCreate


KNOWN_SKILLS = [
    "FastAPI",
    "SQLAlchemy",
    "PostgreSQL",
    "Python",
    "Vue",
    "TypeScript",
    "Docker",
    "pytest",
    "API testing",
    "LangGraph",
    "LangChain",
    "Prompt Engineering",
    "RAG",
    "embedding",
    "pgvector",
    "React",
    "JavaScript",
    "CSS",
    "Redis",
    "Django",
    "Milvus",
    "Chroma",
]

SKILL_CATALOG = {
    "fastapi": {
        "name": "FastAPI",
        "category": "backend",
        "aliases": ["FastAPI"],
    },
    "sqlalchemy": {
        "name": "SQLAlchemy",
        "category": "backend",
        "aliases": ["SQLAlchemy"],
    },
    "postgresql": {
        "name": "PostgreSQL",
        "category": "backend",
        "aliases": ["PostgreSQL"],
    },
    "python": {
        "name": "Python",
        "category": "programming",
        "aliases": ["Python", "pandas", "NumPy", "数据处理"],
    },
    "vue": {
        "name": "Vue",
        "category": "frontend",
        "aliases": ["Vue", "Vue.js"],
    },
    "typescript": {
        "name": "TypeScript",
        "category": "frontend",
        "aliases": ["TypeScript"],
    },
    "docker": {
        "name": "Docker",
        "category": "devops",
        "aliases": ["Docker"],
    },
    "sql": {
        "name": "SQL",
        "category": "data_analysis",
        "aliases": ["SQL", "数据库查询", "多表关联", "窗口函数", "数据提取"],
    },
    "data_visualization": {
        "name": "数据可视化",
        "category": "data_analysis",
        "aliases": ["数据可视化", "Tableau", "Power BI", "ECharts", "看板", "图表"],
    },
    "statistics": {
        "name": "统计方法",
        "category": "statistics",
        "aliases": ["统计", "显著性", "置信区间", "假设检验", "统计检验", "statistical", "statistics", "hypothesis testing", "regression"],
    },
    "ab_testing": {
        "name": "A/B 测试",
        "category": "statistics",
        "aliases": ["A/B 测试", "AB 测试", "实验设计", "对照实验", "A/B test", "A/B tests", "AB test", "AB tests", "A/B testing", "AB testing"],
    },
    "machine_learning": {
        "name": "机器学习",
        "category": "machine_learning",
        "aliases": ["机器学习", "特征分析", "模型", "算法"],
    },
    "business_analysis": {
        "name": "业务分析",
        "category": "business",
        "aliases": ["业务分析", "转化率", "留存", "增长", "指标体系"],
    },
}


CASE_SENSITIVE_SKILLS = {"React", "ReAct", "CSS"}


def _skill_pattern(skill: str) -> re.Pattern[str]:
    """创建技能匹配正则表达式模式
    
    使用 re.escape() 转义技能名称中的特殊字符，防止正则表达式注入攻击。
    """
    # 转义技能名称中的正则特殊字符，防止 ReDoS 攻击
    escaped_skill = re.escape(skill)
    if skill in CASE_SENSITIVE_SKILLS:
        return re.compile(rf"(?<![A-Za-z0-9]){escaped_skill}(?![A-Za-z0-9])")
    return re.compile(rf"(?<![A-Za-z0-9]){escaped_skill}(?![A-Za-z0-9])", re.IGNORECASE)


def _find_evidence(raw_text: str, skill: str) -> list[str]:
    """在文本中查找包含指定技能的句子作为证据
    
    Args:
        raw_text: 原始文本内容
        skill: 要查找的技能名称
        
    Returns:
        包含该技能的句子列表
    """
    evidence: list[str] = []
    separators = r"(?<=[.!?。！？\n])\s*"
    for sentence in re.split(separators, raw_text.strip()):
        sentence = sentence.strip()
        if not sentence:
            continue
        if _skill_pattern(skill).search(sentence):
            evidence.append(sentence)
    return evidence


def parse_job_profile(raw_text: str) -> dict[str, Any]:
    """解析职位描述文本，提取技能维度和证据
    
    Args:
        raw_text: 职位描述原始文本
        
    Returns:
        包含技能维度、权重、证据等的职位画像字典
        
    Example:
        >>> profile = parse_job_profile("We need a Python developer with FastAPI.")
        >>> profile["job_family"]
        'software_engineering'
        >>> len(profile["skill_dimensions"]) > 0
        True
    """
    dimensions: list[dict[str, Any]] = []
    evidence: dict[str, list[str]] = {}
    for key, item in SKILL_CATALOG.items():
        matched = []
        for alias in item["aliases"]:
            matched.extend(_find_evidence(raw_text, alias))
        matched = list(dict.fromkeys(matched))
        if matched:
            evidence[key] = matched
            dimensions.append({
                "name": item["name"],
                "canonical_key": key,
                "category": item["category"],
                "weight": 1.0,
                "required_level": "project_practice",
                "jd_evidence": matched,
                "aliases": item["aliases"],
            })

    normalized_weight = 1 / len(dimensions) if dimensions else 0
    for dimension in dimensions:
        dimension["weight"] = normalized_weight

    legacy_skills = [dimension["name"] for dimension in dimensions]
    job_family = "data_analysis" if any(
        key in evidence for key in ["sql", "data_visualization", "statistics", "ab_testing"]
    ) else "software_engineering"

    return {
        "schema_version": "job-profile-v2",
        "job_family": job_family,
        "skill_dimensions": dimensions,
        "required_skills": legacy_skills,
        "preferred_skills": [],
        "domain_keywords": [job_family],
        "basic_requirements": [],
        "evidence": evidence,
    }


def create_job(db: Session, payload: JobCreate) -> JobDescription:
    """创建新的职位描述
    
    Args:
        db: 数据库会话
        payload: 职位创建数据
        
    Returns:
        创建的职位描述对象
        
    Raises:
        SQLAlchemyError: 数据库操作失败时
    """
    job = JobDescription(
        title=payload.title.strip(),
        raw_text=payload.raw_text,
        profile=parse_job_profile(payload.raw_text),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> list[JobDescription]:
    """获取所有职位列表，按创建时间倒序排列
    
    Args:
        db: 数据库会话
        
    Returns:
        职位描述对象列表
    """
    return list(db.query(JobDescription).order_by(JobDescription.created_at.desc()).all())


def get_job(db: Session, job_id: int) -> JobDescription | None:
    """根据ID获取职位描述
    
    Args:
        db: 数据库会话
        job_id: 职位ID
        
    Returns:
        职位描述对象，如果不存在则返回 None
    """
    return db.get(JobDescription, job_id)
