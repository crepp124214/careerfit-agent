from app.scoring.evidence import find_resume_evidence
from app.scoring.rubric import LEVEL_WEIGHTS, clamp_score


SCORING_VERSION = "deterministic-v2"

# 深度经验关键词 — 表明候选人在该技能上有深入实践
_DEEP_EXPERIENCE_TERMS = [
    "scale", "production", "生产", "性能", "架构", "architect",
    "优化", "高并发", "高可用", "分布式", "微服务",
    "大规模", "千万级", "亿级", "百万级", "qps", "tps",
    "吞吐量", "延迟", "latency", "吞吐量",
    "主导", "负责", "架构设计", "技术选型", "核心开发",
    "从零搭建", "从0到1", "从0搭建", "搭建",
    "开源", "github", "贡献", "committer", "maintainer",
    "源码", "原理", "深入", "精通", "专家",
]

# 项目实践关键词 — 表明候选人有实际项目经验
_PROJECT_PRACTICE_TERMS = [
    "project", "项目", "服务", "system", "系统",
    "开发", "实现", "搭建", "构建", "完成", "交付",
    "应用", "平台", "工具", "框架", "模块", "组件",
    "接口", "api", "rest", "graphql", "grpc",
    "数据库", "缓存", "消息队列", "mq", "kafka", "rabbitmq",
    "部署", "上线", "发布", "迭代", "版本",
    "团队", "协作", "敏捷", "scrum",
]

# 基础使用关键词 — 表明候选人了解但缺乏深度实践
_BASIC_USAGE_TERMS = [
    "熟悉", "了解", "学习", "培训", "课程",
    "用过", "使用过", "接触过", "了解过",
    "入门", "基础", "初级", "basic", "beginner",
]


def _build_knowledge_evidence(
    skill: str, rag_results: dict | None
) -> list[dict]:
    if not rag_results:
        return []
    skill_result = rag_results.get(skill)
    if not skill_result:
        return []
    if skill_result.get("available") is False:
        return [{"available": False, "reason": skill_result.get("reason", "知识库证据不足")}]
    documents = skill_result.get("documents", [])
    if not documents:
        return [{"available": False, "reason": "知识库证据不足"}]
    return [
        {
            "doc_id": doc.get("doc_id"),
            "title": doc.get("title", ""),
            "snippet": doc.get("content_snippet", ""),
            "available": True,
        }
        for doc in documents
    ]


def _score_skill(skill: str, resume_profile: dict) -> tuple[str, float, list[str]]:
    """根据简历证据评估技能掌握程度
    
    评分层次（从高到低）：
    - deep_experience (1.0): 有深度实践经验，涉及性能优化、架构设计、大规模系统等
    - project_practice (0.75): 有实际项目经验，但深度证据不足
    - basic_usage (0.5): 了解并使用过，但缺乏项目实践证据
    - mentioned (0.3): 仅在技能列表中提到，无具体证据
    - not_mentioned (0.0): 未提及
    """
    evidence = find_resume_evidence(skill, resume_profile)
    
    # 对于编程语言类技能，也查找其生态框架的项目证据
    # 例如 Python 的证据也应该包含 Django/Flask 项目的描述
    extended_evidence = list(evidence)
    if skill in ("python", "java", "javascript", "golang"):
        # 定义各语言的生态框架映射
        framework_map = {
            "python": ["django", "flask", "fastapi", "sqlalchemy", "pandas", "numpy", "pytorch", "tensorflow"],
            "java": ["spring", "springboot", "mybatis", "hibernate"],
            "javascript": ["react", "vue", "angular", "express", "nodejs", "next.js"],
            "golang": ["gin", "echo", "beego"],
        }
        related_frameworks = framework_map.get(skill, [])
        
        # 查找该语言生态框架的证据
        all_evidence = resume_profile.get("evidence", {})
        for framework_key, framework_evidence in all_evidence.items():
            if framework_key in related_frameworks:
                for fe in (framework_evidence if isinstance(framework_evidence, list) else [framework_evidence]):
                    if fe not in extended_evidence:
                        extended_evidence.append(f"[通过{framework_key}] {fe}")
    
    if not extended_evidence:
        return "not_mentioned", LEVEL_WEIGHTS["not_mentioned"], []
    
    joined = " ".join(extended_evidence).lower()
    
    # 检查是否有深度经验证据
    deep_score = sum(1 for term in _DEEP_EXPERIENCE_TERMS if term in joined)
    if deep_score >= 2:
        return "deep_experience", LEVEL_WEIGHTS["deep_experience"], extended_evidence
    
    # 检查是否有项目实践证据
    project_score = sum(1 for term in _PROJECT_PRACTICE_TERMS if term in joined)
    if project_score >= 2:
        return "project_practice", LEVEL_WEIGHTS["project_practice"], extended_evidence
    
    # 检查是否仅为基础使用
    basic_score = sum(1 for term in _BASIC_USAGE_TERMS if term in joined)
    if basic_score >= 1:
        return "basic_usage", LEVEL_WEIGHTS["basic_usage"], extended_evidence
    
    # 如果只有原始证据（没有扩展证据），说明只是简单提及
    if not evidence and extended_evidence:
        return "mentioned", LEVEL_WEIGHTS["mentioned"], extended_evidence
    
    # 默认：仅提及
    return "mentioned", LEVEL_WEIGHTS["mentioned"], extended_evidence


def _average(values: list[float]) -> float:
    """计算算术平均"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _weighted_average(values: list[float], weights: list[float]) -> float:
    """计算加权平均"""
    if not values or not weights or len(values) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def _iter_dimensions(jd_profile: dict) -> list[dict]:
    dimensions = jd_profile.get("skill_dimensions") or []
    if dimensions:
        return dimensions
    return [
        {
            "name": skill,
            "canonical_key": skill,
            "category": "general",
            "weight": 1,
            "required_level": "project_practice",
            "jd_evidence": (jd_profile.get("evidence") or {}).get(skill, []),
            "aliases": [skill],
        }
        for skill in jd_profile.get("required_skills") or []
    ]


def score_match(jd_profile: dict, resume_profile: dict, rag_results: dict | None = None) -> dict:
    dimensions = _iter_dimensions(jd_profile)
    if not dimensions:
        return {
            "scoring_version": SCORING_VERSION,
            "final_score": 0,
            "score_breakdown": {
                "skill_score": 0,
                "project_score": 0,
                "domain_score": 0,
                "basic_requirement_score": 0,
                "expression_score": 0,
                "integrity_risk_penalty": 0,
            },
            "score_items": [],
        }

    score_items = []
    skill_scores = []
    skill_weights_list = []
    for dimension in dimensions:
        skill_key = dimension["canonical_key"]
        skill_name = dimension["name"]
        dim_weight = dimension.get("weight", 1.0)
        level, weight, resume_evidence = _score_skill(skill_key, resume_profile)
        skill_scores.append(weight)
        skill_weights_list.append(dim_weight)
        score_items.append(
            {
                "skill_key": skill_key,
                "skill": skill_name,
                "category": dimension.get("category", "general"),
                "level": level,
                "score": clamp_score(weight * 100),
                "weight": dim_weight,
                "jd_evidence": dimension.get("jd_evidence", []),
                "resume_evidence": resume_evidence,
                "jd_required_level": dimension.get("required_level", "project_practice"),
                "knowledge_evidence": _build_knowledge_evidence(skill_key, rag_results),
            }
        )

    # 技能匹配得分：基于每个 JD 技能维度的匹配程度加权平均
    skill_score = _weighted_average(skill_scores, skill_weights_list) * 100
    
    # 项目经验得分：基于简历中项目数量和质量
    projects = resume_profile.get("projects", [])
    if len(projects) >= 3:
        project_score = 100
    elif len(projects) >= 2:
        project_score = 85
    elif len(projects) >= 1:
        project_score = 70
    else:
        project_score = max(0, skill_score - 30)
    
    # 领域匹配得分：JD 和简历的领域关键词重叠度
    jd_domains = set(jd_profile.get("domain_keywords") or [])
    resume_domains = set(resume_profile.get("domain_keywords") or [])
    if not jd_domains:
        domain_score = 80  # JD 没有明确领域时给中等分
    elif jd_domains & resume_domains:
        domain_score = 100
    else:
        domain_score = 40
    
    # 基础要求得分：JD 中是否列出基础要求
    basic_reqs = jd_profile.get("basic_requirements", [])
    if not basic_reqs:
        basic_requirement_score = 80
    else:
        basic_requirement_score = 100
    
    # 表达质量得分：简历中技能数量（反映表达丰富度）
    skill_count = len(resume_profile.get("skills", []))
    if skill_count >= 8:
        expression_score = 100
    elif skill_count >= 5:
        expression_score = 85
    elif skill_count >= 3:
        expression_score = 70
    elif skill_count >= 1:
        expression_score = 50
    else:
        expression_score = 0
    
    # 完整性风险扣分
    integrity_risk_penalty = 0

    # 最终得分：加权计算
    final_score = clamp_score(
        skill_score * 0.40      # 技能匹配权重最高
        + project_score * 0.25  # 项目经验
        + domain_score * 0.15   # 领域匹配
        + basic_requirement_score * 0.10  # 基础要求
        + expression_score * 0.10  # 表达质量
        - integrity_risk_penalty * 0.05
    )

    return {
        "scoring_version": SCORING_VERSION,
        "final_score": final_score,
        "score_breakdown": {
            "skill_score": clamp_score(skill_score),
            "project_score": clamp_score(project_score),
            "domain_score": clamp_score(domain_score),
            "basic_requirement_score": clamp_score(basic_requirement_score),
            "expression_score": clamp_score(expression_score),
            "integrity_risk_penalty": clamp_score(integrity_risk_penalty),
        },
        "score_items": score_items,
    }
