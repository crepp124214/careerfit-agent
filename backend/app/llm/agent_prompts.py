from app.llm.agent_schemas import (
    GapAnalysisOutput,
    InterviewQuestionOutput,
    JDParseOutput,
    LearningPlanOutput,
    NextBestActionOutput,
    RagQueryPlanOutput,
    ResumeParseOutput,
    ResumeSuggestionOutput,
)


def build_jd_parse_prompt(raw_jd: str) -> str:
    return f"""分析以下岗位描述，提取技能维度和岗位族信息。

岗位描述：
{raw_jd}

要求：
1. 识别岗位所属领域（如 data_analysis, software_engineering 等）
2. 提取所有关键技能要求，每个技能包含名称、类别、权重和证据原文
3. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_resume_parse_prompt(raw_resume: str) -> str:
    return f"""分析以下简历内容，提取技能证据和项目经验。

简历内容：
{raw_resume}

要求：
1. 识别所有技术技能和实践经验
2. 为每个技能提供证据片段和熟练程度
3. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。不得新增简历中不存在的事实。"""


def build_rag_query_plan_prompt(jd_profile: dict) -> str:
    dimensions = jd_profile.get("skill_dimensions", [])
    dim_text = "\n".join([f"- {d['name']}: {d.get('jd_evidence', [])}" for d in dimensions])
    return f"""根据以下岗位技能维度，规划知识库检索策略。

技能维度：
{dim_text}

要求：
1. 为每个技能维度生成检索查询词
2. 指定相关文档类型和岗位族过滤条件
3. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_gap_analysis_prompt(match_result: dict) -> str:
    score_items = match_result.get("score_items", [])
    items_text = "\n".join([f"- {i.get('skill', i.get('skill_key'))}: 分数={i.get('score', 0)}, 级别={i.get('level')}" for i in score_items])
    return f"""根据以下评分结果，分析能力缺口。

评分结果：
{items_text}

要求：
1. 识别每个技能的缺口类型（missing_skill, weak_evidence, expression_gap, knowledge_insufficient）
2. 说明缺口的优先级和原因
3. 列出已有的优势
4. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_resume_suggestion_prompt(gaps: list, strengths: list) -> str:
    gaps_text = "\n".join([f"- {g.get('skill_key')}: {g.get('reason')}" for g in gaps])
    strengths_text = "\n".join([f"- {s}" for s in strengths])
    return f"""根据以下能力缺口和优势，生成简历优化建议。

能力缺口：
{gaps_text}

已有优势：
{strengths_text}

要求：
1. 针对每个缺口提供具体的简历优化建议
2. 建议必须基于现有证据进行增强表达，不得新增事实
3. 标注每条建议的风险等级
4. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_interview_prompt(score_items: list, gaps: list) -> str:
    items_text = "\n".join([f"- {i.get('skill', i.get('skill_key'))}: 级别={i.get('level')}" for i in score_items])
    gaps_text = "\n".join([f"- {g.get('skill_key')}: {g.get('gap_type')}" for g in gaps])
    return f"""根据以下评分结果和缺口，生成差异化面试题。

评分项：
{items_text}

能力缺口：
{gaps_text}

要求：
1. 按技能类别生成不同类型的面试题（基础题、项目深挖题、场景设计题）
2. SQL 题应包含查询、关联、窗口函数等
3. 统计/A/B 测试题应包含实验设计和评估方法
4. 可视化题应包含图表选择和指标解释
5. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_learning_plan_prompt(gaps: list, knowledge: dict) -> str:
    gaps_text = "\n".join([f"- {g.get('skill_key')}: {g.get('reason')}" for g in gaps])
    return f"""根据以下能力缺口和学习资源，制定学习计划。

能力缺口：
{gaps_text}

可用知识库资源：
{knowledge}

要求：
1. 为每个高优先级缺口制定学习路径
2. 包含具体练习、推荐资源和验收标准
3. 不要给泛泛的"做个项目"建议
4. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""


def build_next_best_action_prompt(gaps: list, score: int) -> str:
    gaps_text = "\n".join([f"- {g.get('skill_key')}: 优先级={g.get('priority')}" for g in gaps])
    return f"""根据当前评分和能力缺口，选择最高影响力的下一步行动。

当前总分：{score}
能力缺口：
{gaps_text}

要求：
1. 选择一个最值得立即投入的行动
2. 行动必须有明确的技能目标
3. 解释为什么这个行动影响最大
4. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。"""
