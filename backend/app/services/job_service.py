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
    # 编程语言
    "python": {
        "name": "Python",
        "category": "programming",
        "aliases": ["Python", "pandas", "NumPy", "数据处理", "PyTorch", "TensorFlow"],
    },
    "java": {
        "name": "Java",
        "category": "programming",
        "aliases": ["Java", "JVM", "Spring Boot", "Spring", "SpringMVC", "Java EE", "Jakarta EE"],
    },
    "golang": {
        "name": "Go",
        "category": "programming",
        "aliases": ["Go", "Golang", "Go语言"],
    },
    "javascript": {
        "name": "JavaScript",
        "category": "programming",
        "aliases": ["JavaScript", "JS", "ES6", "Node.js", "Nodejs"],
    },
    "typescript": {
        "name": "TypeScript",
        "category": "programming",
        "aliases": ["TypeScript", "TS"],
    },
    "cpp": {
        "name": "C++",
        "category": "programming",
        "aliases": ["C++", "CPP", "C/C++", "STL"],
    },
    "csharp": {
        "name": "C#",
        "category": "programming",
        "aliases": ["C#", "CSharp", ".NET", "ASP.NET"],
    },
    "rust": {
        "name": "Rust",
        "category": "programming",
        "aliases": ["Rust"],
    },
    # 后端框架
    "fastapi": {
        "name": "FastAPI",
        "category": "backend",
        "aliases": ["FastAPI"],
    },
    "django": {
        "name": "Django",
        "category": "backend",
        "aliases": ["Django", "Django REST Framework", "DRF"],
    },
    "flask": {
        "name": "Flask",
        "category": "backend",
        "aliases": ["Flask"],
    },
    "spring": {
        "name": "Spring",
        "category": "backend",
        "aliases": ["Spring", "Spring Boot", "Spring Cloud", "SpringMVC"],
    },
    "express": {
        "name": "Express",
        "category": "backend",
        "aliases": ["Express", "Express.js"],
    },
    # 数据库
    "postgresql": {
        "name": "PostgreSQL",
        "category": "database",
        "aliases": ["PostgreSQL", "Postgres", "PG"],
    },
    "mysql": {
        "name": "MySQL",
        "category": "database",
        "aliases": ["MySQL", "MariaDB"],
    },
    "mongodb": {
        "name": "MongoDB",
        "category": "database",
        "aliases": ["MongoDB", "Mongo", "NoSQL"],
    },
    "redis": {
        "name": "Redis",
        "category": "database",
        "aliases": ["Redis", "缓存", "cache"],
    },
    "sql": {
        "name": "SQL",
        "category": "database",
        "aliases": ["SQL", "数据库查询", "多表关联", "窗口函数", "数据提取", "数据库设计", "索引优化"],
    },
    "elasticsearch": {
        "name": "Elasticsearch",
        "category": "database",
        "aliases": ["Elasticsearch", "ES", "搜索引擎", "ELK"],
    },
    # ORM
    "sqlalchemy": {
        "name": "SQLAlchemy",
        "category": "backend",
        "aliases": ["SQLAlchemy", "ORM"],
    },
    # 前端框架
    "react": {
        "name": "React",
        "category": "frontend",
        "aliases": ["React", "React.js", "ReactJS", "Next.js"],
    },
    "vue": {
        "name": "Vue",
        "category": "frontend",
        "aliases": ["Vue", "Vue.js", "VueJS", "Vue3", "Nuxt.js"],
    },
    "angular": {
        "name": "Angular",
        "category": "frontend",
        "aliases": ["Angular"],
    },
    # DevOps / 云原生
    "docker": {
        "name": "Docker",
        "category": "devops",
        "aliases": ["Docker", "容器化", "container"],
    },
    "kubernetes": {
        "name": "Kubernetes",
        "category": "devops",
        "aliases": ["Kubernetes", "K8s", "容器编排"],
    },
    "aws": {
        "name": "AWS",
        "category": "cloud",
        "aliases": ["AWS", "Amazon Web Services", "EC2", "S3", "Lambda"],
    },
    "aliyun": {
        "name": "阿里云",
        "category": "cloud",
        "aliases": ["阿里云", "Aliyun", "ECS", "OSS", "RDS"],
    },
    "ci_cd": {
        "name": "CI/CD",
        "category": "devops",
        "aliases": ["CI/CD", "Jenkins", "GitLab CI", "GitHub Actions", "持续集成", "持续部署"],
    },
    "git": {
        "name": "Git",
        "category": "devops",
        "aliases": ["Git", "版本控制", "GitFlow"],
    },
    "linux": {
        "name": "Linux",
        "category": "devops",
        "aliases": ["Linux", "Shell", "Bash", "运维", "系统管理"],
    },
    # 数据科学 / AI
    "machine_learning": {
        "name": "机器学习",
        "category": "ai",
        "aliases": ["机器学习", "特征分析", "模型", "算法", "ML", "scikit-learn"],
    },
    "deep_learning": {
        "name": "深度学习",
        "category": "ai",
        "aliases": ["深度学习", "Deep Learning", "神经网络", "CNN", "RNN", "Transformer"],
    },
    "data_analysis": {
        "name": "数据分析",
        "category": "data",
        "aliases": ["数据分析", "数据挖掘", "数据清洗", "ETL", "数据工程"],
    },
    "data_visualization": {
        "name": "数据可视化",
        "category": "data",
        "aliases": ["数据可视化", "Tableau", "Power BI", "ECharts", "看板", "图表", "matplotlib"],
    },
    "statistics": {
        "name": "统计方法",
        "category": "data",
        "aliases": ["统计", "显著性", "置信区间", "假设检验", "统计检验", "statistical", "statistics", "hypothesis testing", "regression"],
    },
    "ab_testing": {
        "name": "A/B 测试",
        "category": "data",
        "aliases": ["A/B 测试", "AB 测试", "实验设计", "对照实验", "A/B test", "AB test", "A/B testing", "AB testing"],
    },
    # 大模型 / AI 工程
    "llm": {
        "name": "大语言模型",
        "category": "ai",
        "aliases": ["LLM", "大语言模型", "大模型", "GPT", "ChatGPT", "Claude"],
    },
    "rag": {
        "name": "RAG",
        "category": "ai",
        "aliases": ["RAG", "检索增强生成", "向量检索", "embedding"],
    },
    "langchain": {
        "name": "LangChain",
        "category": "ai",
        "aliases": ["LangChain", "LangGraph"],
    },
    "prompt_engineering": {
        "name": "Prompt Engineering",
        "category": "ai",
        "aliases": ["Prompt Engineering", "提示工程", "Prompt"],
    },
    # 测试
    "testing": {
        "name": "软件测试",
        "category": "quality",
        "aliases": ["测试", "pytest", "单元测试", "集成测试", "自动化测试", "Selenium", "Cypress"],
    },
    # 业务
    "business_analysis": {
        "name": "业务分析",
        "category": "business",
        "aliases": ["业务分析", "转化率", "留存", "增长", "指标体系", "产品经理", "PM"],
    },
    # 安全
    "security": {
        "name": "安全",
        "category": "security",
        "aliases": ["安全", "网络安全", "信息安全", "渗透测试", "加密", "认证", "授权", "OAuth", "JWT"],
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

    # 根据技能在JD中的重要性分配权重
    # 核心技能（明确强调、多次提及）权重更高
    # 次要技能（顺带提及、可选要求）权重更低
    for dimension in dimensions:
        key = dimension["canonical_key"]
        jd_evidence = dimension.get("jd_evidence", [])
        evidence_count = len(jd_evidence)
        
        # 检查是否是核心要求（有"熟练掌握"、"精通"、"必须"等强调词）
        joined_evidence = " ".join(jd_evidence).lower()
        is_core = any(term in joined_evidence for term in [
            "熟练", "精通", "掌握", "必须", "必备", "核心", "重点",
            "proficient", "master", "expert", "required", "essential", "core", "key"
        ])
        
        # 检查是否是可选要求
        is_optional = any(term in joined_evidence for term in [
            "了解", "熟悉", "加分", "优先", "optional", "preferred", "plus", "bonus", "nice to have"
        ])
        
        if is_core:
            base_weight = 1.0
        elif is_optional:
            base_weight = 0.4
        else:
            base_weight = 0.7
        
        # 根据提及次数微调
        mention_bonus = min(0.2, (evidence_count - 1) * 0.1)
        dimension["weight"] = min(1.0, base_weight + mention_bonus)
    
    # 归一化权重，使总和为1
    total_weight = sum(d["weight"] for d in dimensions)
    if total_weight > 0:
        for dimension in dimensions:
            dimension["weight"] = dimension["weight"] / total_weight

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


def compare_jobs(db: Session, job_ids: list[int]) -> list[dict]:
    jobs: list[JobDescription] = []
    for jid in job_ids:
        job = db.get(JobDescription, jid)
        if job is None:
            raise ValueError(f"job_not_found:{jid}")
        jobs.append(job)

    result = []
    for job in jobs:
        profile = job.profile or {}
        dimensions = profile.get("skill_dimensions", [])
        job_dimensions = []
        for dim in dimensions:
            job_dimensions.append({
                "name": dim.get("name", ""),
                "category": dim.get("category", ""),
                "required_level": dim.get("required_level", "mentioned"),
                "weight": dim.get("weight", 0),
            })
        result.append({
            "job_id": job.id,
            "job_title": job.title,
            "dimensions": job_dimensions,
        })
    return result
