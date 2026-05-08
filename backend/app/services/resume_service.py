import re

from sqlalchemy.orm import Session

from app.db.models import ResumeVersion
from app.schemas.resumes import ResumeCreate
from app.services.job_service import SKILL_CATALOG, _find_evidence


# 技能上下文映射：某些短语虽然不直接匹配技能名，但表明掌握了相关技能
SKILL_CONTEXT_MAP = {
    "restful_api": ["RESTful API", "REST API", "RESTful", "API设计", "API开发", "接口设计"],
    "sql": ["SQL查询", "数据库查询", "多表关联", "窗口函数", "慢查询", "查询优化", "索引优化"],
    "testing": ["单元测试", "集成测试", "自动化测试", "测试用例", "pytest", "junit"],
    "ci_cd": ["CI/CD", "持续集成", "持续部署", "Jenkins", "GitLab CI", "GitHub Actions"],
    "linux": ["Linux", "Shell脚本", "Bash", "命令行", "运维"],
    "git": ["Git", "版本控制", "GitFlow", "分支管理", "代码合并"],
}


def parse_resume_profile(raw_text: str) -> dict:
    evidence = {}
    skills = []
    
    # 1. 基于技能目录匹配
    for key, item in SKILL_CATALOG.items():
        matched = []
        for alias in item["aliases"]:
            matched.extend(_find_evidence(raw_text, alias))
        matched = list(dict.fromkeys(matched))
        if matched:
            evidence[key] = matched
            skills.append(item["name"])
    
    # 2. 基于上下文映射补充证据
    for skill_key, context_terms in SKILL_CONTEXT_MAP.items():
        if skill_key not in evidence:  # 只补充未匹配到的技能
            matched = []
            for term in context_terms:
                matched.extend(_find_evidence(raw_text, term))
            matched = list(dict.fromkeys(matched))
            if matched:
                evidence[skill_key] = matched
                # 查找技能名称
                skill_name = SKILL_CATALOG.get(skill_key, {}).get("name", skill_key)
                if skill_name not in skills:
                    skills.append(skill_name)
    
    # 3. 提取项目经验
    projects = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?。！？\n])\s*", raw_text)
        if any(term in sentence for term in ["项目", "构建", "完成", "支持", "分析", "开发", "实现", "搭建"])
    ]
    
    # 去重项目
    projects = list(dict.fromkeys(projects))

    return {
        "schema_version": "resume-profile-v2",
        "skills": skills,
        "projects": projects,
        "domain_keywords": [],
        "evidence": evidence,
    }


def create_resume(db: Session, payload: ResumeCreate) -> ResumeVersion:
    resume = ResumeVersion(
        candidate_name=payload.candidate_name.strip(),
        version_label=payload.version_label.strip(),
        raw_text=payload.raw_text,
        profile=parse_resume_profile(payload.raw_text),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session) -> list[ResumeVersion]:
    return list(db.query(ResumeVersion).order_by(ResumeVersion.created_at.desc()).all())


def get_resume(db: Session, resume_id: int) -> ResumeVersion | None:
    return db.get(ResumeVersion, resume_id)
