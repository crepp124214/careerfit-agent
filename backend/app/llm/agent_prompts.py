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
    return f"""你是一个专业的HR技术分析师。请仔细分析以下岗位描述（JD），提取结构化的技能要求信息。

## 岗位描述原文：
```
{raw_jd}
```

## 输出要求：

### 1. job_family（岗位族）
从以下选项中选择最匹配的一个：
- software_engineering（软件开发）
- data_analysis（数据分析）
- product_manager（产品经理）
- ui_ux_design（UI/UX设计）
- devops_engineer（DevOps）
- machine_learning（机器学习）
- other（其他）

### 2. dimensions（技能维度列表）
为每个关键技能创建一个维度对象，包含以下字段：

```json
{{
  "name": "技能显示名称",
  "canonical_key": "标准化英文key（小写下划线）",
  "category": "类别（technical_soft/business/domain）",
  "weight": 0.8,
  "required_level": "project_practice",
  "jd_evidence": ["原文中的具体证据句子1", "原文中的具体证据句子2"],
  "aliases": ["别名1", "别名2"]
}}
```

#### required_level 取值说明：
- mentioned: 仅提及，了解即可
- basic_usage: 基础使用能力
- project_practice: 项目实践经验（大多数核心技能的要求）
- deep_experience: 深度经验/专家级别

#### weight 权重建议：
- 核心硬技能：0.8-1.0
- 重要技能：0.6-0.8
- 加分项：0.3-0.6

### 3. evidence_summary
用一句话总结提取到的关键信息。

## ⚠️ 关键约束：

### canonical_key 标准化规则（必须严格遵守）：
1. **复合技能必须拆分**：如果JD提到"Django/Flask框架"，必须拆分为两个独立维度：
   - `django`（name="Django框架"）
   - `flask`（name="Flask框架"）
   
2. **数据库同理**：如果JD提到"PostgreSQL/MySQL"，必须拆分为：
   - `postgresql`（name="PostgreSQL数据库"）
   - `mysql`（name="MySQL数据库"）

3. **标准化key对照表**（优先使用这些key）：
   - Python → `python`
   - Java → `java`
   - Go/Golang → `golang`
   - JavaScript/JS → `javascript`
   - TypeScript/TS → `typescript`
   - C++ → `cpp`
   - C# → `csharp`
   - Rust → `rust`
   - Django → `django`
   - Flask → `flask`
   - FastAPI → `fastapi`
   - Spring/Spring Boot → `spring`
   - Express → `express`
   - React → `react`
   - Vue/Vue.js → `vue`
   - Angular → `angular`
   - PostgreSQL/Postgres → `postgresql`
   - MySQL → `mysql`
   - MongoDB → `mongodb`
   - Redis → `redis`
   - SQL → `sql`
   - Elasticsearch → `elasticsearch`
   - Docker → `docker`
   - Kubernetes/K8s → `kubernetes`
   - AWS → `aws`
   - 阿里云 → `aliyun`
   - CI/CD → `ci_cd`
   - Git → `git`
   - Linux → `linux`
   - 机器学习/ML → `machine_learning`
   - 深度学习 → `deep_learning`
   - 数据分析 → `data_analysis`
   - 数据可视化 → `data_visualization`
   - 统计方法 → `statistics`
   - A/B测试 → `ab_testing`
   - 大语言模型/LLM → `llm`
   - RAG → `rag`
   - LangChain → `langchain`
   - Prompt Engineering → `prompt_engineering`
   - 软件测试/测试 → `testing`
   - 业务分析 → `business_analysis`
   - 安全/网络安全 → `security`

4. 如果技能不在对照表中，使用英文小写下划线格式
5. **严禁**将多个技能合并为一个维度（如 `django_flask_framework` 是错误的）

## 示例输出格式：
```json
{{
  "job_family": "software_engineering",
  "dimensions": [
    {{
      "name": "Python编程语言",
      "canonical_key": "python",
      "category": "technical",
      "weight": 0.9,
      "required_level": "project_practice",
      "jd_evidence": ["熟练掌握Python编程语言"],
      "aliases": ["Python", "Py"]
    }},
    {{
      "name": "Django框架",
      "canonical_key": "django",
      "category": "technical",
      "weight": 0.8,
      "required_level": "project_practice",
      "jd_evidence": ["有Django/Flask框架经验"],
      "aliases": ["Django"]
    }},
    {{
      "name": "Flask框架",
      "canonical_key": "flask",
      "category": "technical",
      "weight": 0.7,
      "required_level": "project_practice",
      "jd_evidence": ["有Django/Flask框架经验"],
      "aliases": ["Flask"]
    }},
    {{
      "name": "PostgreSQL数据库",
      "canonical_key": "postgresql",
      "category": "technical",
      "weight": 0.7,
      "required_level": "project_practice",
      "jd_evidence": ["熟悉PostgreSQL/MySQL数据库设计和优化"],
      "aliases": ["PostgreSQL", "Postgres", "PG"]
    }},
    {{
      "name": "MySQL数据库",
      "canonical_key": "mysql",
      "category": "technical",
      "weight": 0.6,
      "required_level": "project_practice",
      "jd_evidence": ["熟悉PostgreSQL/MySQL数据库设计和优化"],
      "aliases": ["MySQL"]
    }}
  ],
  "evidence_summary": "提取5个核心技术维度"
}}
```

## ⚠️ 重要约束：
1. 只提取JD中明确提及的技能，不要臆测
2. jd_evidence必须引用原文的具体句子或短语
3. **canonical_key必须严格使用标准化对照表中的key**
4. **复合技能（用/或、连接）必须拆分为独立维度**
5. 至少提取2-5个最重要的技能维度
6. 输出纯JSON，不要Markdown代码块标记"""


def build_resume_parse_prompt(raw_resume: str) -> str:
    return f"""你是一个专业的简历分析师。请仔细分析以下简历内容，提取可验证的技能证据和项目经验。

## 简历原文：
```
{raw_resume}
```

## 输出要求：

### 1. skills（技能列表）
为每个识别到的技能创建一个对象：

```json
{{
  "skill_key": "标准化技能名称（英文小写）",
  "evidence": ["简历中的具体证据句子1", "具体描述2"],
  "expression_level": "project_practice"
}}
```

#### expression_level 取值标准：
- not_mentioned: 未提及
- mentioned: 仅在技能列表中提及，无具体实践
- basic_usage: 有基础使用经历，但缺乏深度
- project_practice: 有完整的项目实践经验（**最常见**）
- deep_experience: 有深度/大规模/生产环境经验

#### 判断依据：
- 看到"参与XX项目"、"使用XX完成YY"、"负责ZZ模块" → project_practice
- 看到"熟悉XX"、"了解XX"、"学习过XX" → mentioned/basic_usage
- 看到"主导XX系统"、"XX万级用户"、"性能优化XX%" → deep_experience

### 2. project_summary
用一句话总结候选人的项目经验背景。

### 3. evidence_summary
用一句话总结提取到的关键技能数量和质量。

## 示例输出格式：
```json
{{
  "skills": [
    {{
      "skill_key": "python",
      "evidence": ["使用Python开发数据分析脚本", "pandas处理百万级数据"],
      "expression_level": "project_practice"
    }},
    {{
      "skill_key": "sql",
      "evidence": ["编写复杂SQL查询", "优化慢查询性能提升50%"],
      "expression_level": "deep_experience"
    }}
  ],
  "project_summary": "3年数据分析经验，擅长SQL和Python",
  "evidence_summary": "提取8个技能，其中3个有深度经验"
}}
```

## ⚠️ 重要约束：
1. **只提取简历中明确存在的内容，绝对不要编造或夸大**
2. evidence必须引用简历原文的具体句子或短语
3. 如果某个技能只在技能列表中提及而无实践描述，标记为mentioned
4. 至少提取3-8个最重要的技能
5. skill_key使用英文小写格式（如python, sql, vue, react）
6. 输出纯JSON，不要Markdown代码块标记"""


def build_rag_query_plan_prompt(jd_profile: dict) -> str:
    dimensions = jd_profile.get("skill_dimensions", [])
    dim_text = "\n".join([f"- {d['name']} (key={d.get('canonical_key', d['name'])}): {d.get('jd_evidence', [])}" for d in dimensions])
    return f"""根据以下岗位技能维度，规划知识库检索策略。

技能维度：
{dim_text}

## 输出要求：

生成一个 `queries` 数组，每个查询对象必须包含以下字段：

```json
{{
  "skill_key": "技能的标准化key（使用上面提供的key）",
  "query": "检索查询词（简洁的技术关键词组合）",
  "job_family": "software_engineering",
  "doc_types": ["interview_guide", "skill_reference"]
}}
```

### 字段说明：
- **skill_key**: 必须使用上面技能维度中提供的 key（canonical_key）
- **query**: 检索查询词，应该是该技能相关的技术关键词组合
- **job_family**: 岗位族，固定为 "software_engineering"
- **doc_types**: 文档类型列表，固定为 ["interview_guide", "skill_reference"]

### 示例输出：
```json
{{
  "queries": [
    {{
      "skill_key": "python",
      "query": "Python 后端开发 面试题",
      "job_family": "software_engineering",
      "doc_types": ["interview_guide", "skill_reference"]
    }},
    {{
      "skill_key": "django",
      "query": "Django Web框架 项目经验",
      "job_family": "software_engineering",
      "doc_types": ["interview_guide", "skill_reference"]
    }}
  ]
}}
```

## ⚠️ 重要约束：
1. 为每个技能维度生成一个查询对象
2. skill_key 必须严格使用上面提供的 canonical_key
3. query 应该是该技能相关的技术关键词，用于知识库检索
4. 输出纯JSON，不要Markdown代码块标记"""


def build_gap_analysis_prompt(match_result: dict) -> str:
    score_items = match_result.get("score_items", [])
    
    # 格式化评分项，包含更丰富的上下文
    items_lines = []
    for i in score_items:
        skill = i.get('skill', i.get('skill_key', '未知'))
        score = i.get('score', 0)
        level = i.get('level', 'unknown')
        jd_level = i.get('jd_required_level', 'project_practice')
        jd_evidence = i.get('jd_evidence', [])
        resume_evidence = i.get('resume_evidence', [])
        
        jd_evidence_str = "; ".join(jd_evidence[:2]) if jd_evidence else "无"
        resume_evidence_str = "; ".join(resume_evidence[:2]) if resume_evidence else "无"
        
        items_lines.append(
            f"- {skill}: 得分={score}%, 当前级别={level}, "
            f"JD要求={jd_level}, "
            f"JD证据=[{jd_evidence_str}], "
            f"简历证据=[{resume_evidence_str}]"
        )
    
    items_text = "\n".join(items_lines)
    
    return f"""你是一个专业的职业能力评估分析师。请根据以下详细的评分数据，深入分析候选人的能力缺口和优势。

## 评分详情：
{items_text}

## 分析要求：

### 1. gaps（能力缺口列表）
对每个技能，判断是否存在缺口以及缺口类型：

**缺口类型定义：**
- **missing_skill**: 候选人完全未提及该技能（得分=0）
- **weak_evidence**: 候选人提及了该技能，但证据薄弱（得分<50，或级别低于JD要求）
- **expression_gap**: 候选人有相关经验，但表达不够充分或专业（得分50-75，有证据但不够突出）
- **knowledge_insufficient**: 候选人的知识深度可能不足（得分<60，JD要求deep_experience但候选人只有basic_usage）

**优先级判断：**
- **high**: 核心技能缺口（JD权重>=0.7 且 得分<50）
- **medium**: 重要技能缺口（JD权重>=0.5 且 得分<70）
- **low**: 次要技能缺口（得分<80但非核心）

### 2. strengths（已有优势列表）
识别候选人表现优秀的技能：
- 得分>=80的技能
- 有深度经验证据的技能
- 与JD要求高度匹配的技能

## 输出格式：
```json
{{
  "gaps": [
    {{
      "skill_key": "标准化技能名称",
      "gap_type": "missing_skill|weak_evidence|expression_gap|knowledge_insufficient",
      "reason": "详细说明为什么存在这个缺口，引用具体证据",
      "priority": "high|medium|low"
    }}
  ],
  "strengths": [
    {{
      "skill": "技能名称",
      "resume_evidence": ["具体的简历证据"],
      "reason": "为什么这是优势"
    }}
  ]
}}
```

## ⚠️ 重要约束：
1. **必须基于提供的评分数据进行分析**，不要臆测
2. 每个缺口的 reason 必须引用具体的得分和证据
3. 至少识别1-3个优势和1-5个缺口
4. 如果某个技能得分>=80，不要将其列为缺口
5. 输出纯JSON，不要Markdown代码块标记"""


def build_resume_suggestion_prompt(gaps: list, strengths: list) -> str:
    # 格式化缺口信息
    gaps_lines = []
    for g in gaps:
        skill = g.get('skill', g.get('skill_key', '未知'))
        gap_type = g.get('gap_type', 'unknown')
        priority = g.get('priority', 'medium')
        reason = g.get('reason', '无原因')
        gaps_lines.append(f"- {skill}: {reason} [类型:{gap_type}, 优先级:{priority}]")
    gaps_text = "\n".join(gaps_lines) if gaps_lines else "- 无明显缺口"
    
    # 格式化优势信息
    strengths_lines = []
    for s in strengths:
        if isinstance(s, dict):
            skill = s.get("skill", s.get("skill_key", "未知"))
            evidence = s.get("resume_evidence", [])
            evidence_str = "; ".join(evidence[:2]) if evidence else "无具体证据"
            reason = s.get("reason", "")
            strengths_lines.append(f"- {skill}: {evidence_str[:100]}{' (' + reason + ')' if reason else ''}")
        else:
            strengths_lines.append(f"- {s}")
    strengths_text = "\n".join(strengths_lines) if strengths_lines else "- 无明显优势"
    
    return f"""你是一个资深的技术简历优化顾问，帮助应届生提升简历质量。请根据候选人的能力缺口和优势，生成**具体、可执行、诚实**的简历优化建议。

## ⚠️ 核心原则：只增强表达，不新增事实！

## 能力缺口分析：
{gaps_text}

## 已有优势（可增强的基础）：
{strengths_text}

## 输出要求：

生成一个 `suggestions` 数组，每条建议包含以下字段：

```json
{{
  "title": "建议标题（简洁有力，如：强化Python项目经验表达）",
  "suggestion": "优化后的具体表述（可直接替换到简历中）",
  "original_basis": "简历中现有的原始描述",
  "jd_requirement": "对应的岗位JD要求",
  "resume_evidence": ["支撑这条建议的原始证据1", "原始证据2"],
  "risk_level": "low",
  "optimization_type": "expression_enhancement"
}}
```

### risk_level 取值标准：
- **low**: ✅ 安全 — 仅重新组织已有证据的语言，使其更专业
- **medium**: ⚠️ 需谨慎 — 补充合理的上下文推断，但不能夸大事实
- **high**: ❌ 不推荐 — 可能涉及编造经历或夸大能力

### optimization_type 取值：
- **expression_enhancement**: 表达优化 — 用更专业的技术词汇替换口语化描述
- **structure_improvement**: 结构调整 — 使用STAR法则或技术栈前置等方式重组信息
- **quantification**: 量化补充 — 添加可量化的指标（仅当原始描述中有数据支撑时）
- **context_addition**: 上下文补充 — 补充技术选型理由、业务背景等

### 建议生成策略：

#### 针对 missing_skill（完全缺失）：
- 诚实告知该技能缺失
- 建议候选人先通过项目/课程积累相关经验
- risk_level: "high"（因为涉及新增技能）
- 示例："JD要求掌握Docker容器化，但简历中未提及。建议先完成一个使用Docker部署的项目，再补充到简历中。"

#### 针对 weak_evidence（证据薄弱）：
- 将简单的"熟悉XX"扩展为具体的项目场景
- 补充技术细节和业务背景
- risk_level: "low" 或 "medium"
- 示例：将"熟悉Python"优化为"使用Python开发XX系统，实现YY功能，处理ZZ数据"

#### 针对 expression_gap（表达不足）：
- 使用STAR法则重组描述
- 突出技术难点和解决方案
- 添加量化的业务价值（如果有数据支撑）
- risk_level: "low"

#### 针对已有优势：
- 进一步强化亮点，使用更有冲击力的动词
- 突出技术深度和业务价值
- 示例：将"参与了XX项目"优化为"主导XX模块开发，解决YY技术难题，提升ZZ性能30%"

### 高质量建议示例：

**输入**：
- 缺口：Python (weak_evidence) — 仅在技能列表提及，无项目实践描述
- 优势证据：["使用Django开发电商后台API", "处理日均10万+请求"]

**输出**：
```json
{{
  "title": "强化Python后端开发经验表达",
  "suggestion": "使用Python + Django框架独立开发电商后台管理系统，设计并实现RESTful API接口20+个，支撑日均10万+请求量。引入Redis缓存策略，将核心接口响应时间从200ms优化至50ms。",
  "original_basis": "使用Django开发电商后台API，处理日均10万+请求",
  "jd_requirement": "熟练掌握Python，有Django/Flask框架经验",
  "resume_evidence": ["使用Django开发电商后台API", "处理日均10万+请求"],
  "risk_level": "low",
  "optimization_type": "quantification"
}}
```

## ⚠️ 重要约束：
1. **绝对禁止编造**任何简历中不存在的事实或数据
2. 每条建议的 suggestion 必须能追溯到 original_basis
3. 如果某个技能确实没有相关经历，**明确告知需要先积累**，不要给出虚假建议
4. 为每个高优先级缺口至少生成1条具体建议
5. 总建议数量控制在4-8条，聚焦最有价值的优化点
6. 建议表述要**具体、专业、可直接使用**，避免泛泛而谈
7. 输出纯JSON，不要Markdown代码块标记"""


def build_interview_prompt(score_items: list, gaps: list) -> str:
    items_text = "\n".join([f"- {i.get('skill', i.get('skill_key'))}: 级别={i.get('level')}, 证据={str(i.get('resume_evidence', []))[:50]}" for i in score_items])
    gaps_text = "\n".join([f"- {g.get('skill_key') or g.get('skill')}: {g.get('gap_type', 'missing_skill')}" for g in gaps]) if gaps else "- 无明显缺口"
    return f"""你是一个资深的技术面试官。根据以下候选人的技能评估结果，生成针对性的面试题。

## 候选人技能评估：
{items_text}

## 能力缺口：
{gaps_text}

## 输出要求：

生成一个questions数组，每个问题对象包含以下字段：

```json
{{
  "skill": "技能名称",
  "question": "具体的面试题内容",
  "difficulty": "medium",
  "type": "behavioral",
  "purpose": "考察目的说明"
}}
```

### difficulty 取值：
- easy: 基础概念题（用于热身）
- medium: 标准技术题（**大多数题目应该是这个级别**）
- hard: 深度/场景题（用于区分候选人）

### type 取值：
- technical: 技术知识题（原理、语法、最佳实践）
- behavioral: 行为经历题（STAR法则，项目经验）
- scenario: 场景设计题（系统设计、方案选择）
- coding: 编程/算法题

### 出题策略：
1. **针对缺口技能**：重点出题，验证是否真的不会
2. **针对优势技能**：出深度题，验证真实水平
3. **每个核心技能至少1-2道题**
4. **混合题型**：不要全是技术题或全是行为题
5. **具体化**：避免"请介绍一下XX"这种泛泛的问题，要具体到场景

### 题目示例：
```json
{{
  "skill": "SQL",
  "question": "你在项目中遇到过慢查询吗？请描述一次具体的优化过程，包括如何定位问题、使用了什么方法、最终提升了多少性能？",
  "difficulty": "hard",
  "type": "behavioral",
  "purpose": "验证SQL优化实战经验的真实性和深度"
}}
```

## ⚠️ 重要约束：
1. 生成5-10道高质量的面试题
2. 问题必须具体可回答，不能太宽泛
3. 每道题都要有明确的考察目的
4. 根据候选人的实际水平调整难度
5. 输出纯JSON，不要Markdown代码块标记"""


def build_learning_plan_prompt(gaps: list, knowledge: dict, questions: list = None) -> str:
    """
    基于面试题生成面试准备计划（Interview Prep Plan）
    
    如果有面试题，优先基于面试题生成精准的准备清单
    如果没有面试题，回退到基于缺口的学习计划
    """
    
    # 判断是否有面试题可用
    has_questions = questions and len(questions) > 0
    
    if has_questions:
        return _build_interview_prep_prompt(questions, gaps, knowledge)
    else:
        return _build_gap_based_learning_prompt(gaps, knowledge)


def _build_interview_prep_prompt(questions: list, gaps: list, knowledge: dict) -> str:
    """基于面试题生成面试准备计划"""
    
    # 格式化面试题
    questions_text = ""
    if questions:
        formatted_questions = []
        for i, q in enumerate(questions[:8], 1):
            skill = q.get('skill', '未知技能')
            question_text = q.get('question', '')
            difficulty = q.get('difficulty', 'medium')
            q_type = q.get('type', 'technical')
            
            formatted_questions.append(f"{i}. **[{difficulty.upper()}] {q_type}** {skill}")
            formatted_questions.append(f"   题目: {question_text[:120]}...")
            formatted_questions.append("")
        
        questions_text = "\n".join(formatted_questions)
    
    # 格式化关键缺口（用于补充背景）
    gaps_summary = ""
    high_priority_gaps = [g for g in (gaps or []) if g.get('priority') == 'high']
    if high_priority_gaps:
        gaps_text_list = [f"- {g.get('skill', g.get('skill_key'))}: {g.get('reason', '')[:60]}" 
                         for g in high_priority_gaps[:3]]
        gaps_summary = "\n".join(gaps_text_list)
    else:
        gaps_summary = "- 无高风险缺口"
    
    # 格式化知识资源
    resources_text = "暂无推荐资源"
    if knowledge and isinstance(knowledge, dict):
        available = []
        for key, data in knowledge.items():
            if isinstance(data, dict) and data.get('available'):
                docs = data.get('documents', [])
                for doc in docs[:1]:
                    title = doc.get('title', '')
                    available.append(f"  - [{title}]")
        if available:
            resources_text = "\n".join(available[:5])
    
    return f"""你是一个资深的面试辅导专家。根据以下面试题，为候选人制定**精准的面试准备计划**。

## 🎯 核心目标：
帮助候选人在面试前充分准备，能够自信、流畅地回答每道题目，展现真实能力。

## 📋 需要准备的面试题（{len(questions)}道）：
{questions_text}

## ⚠️ 关键能力缺口（需重点准备）：
{gaps_summary}

## 📚 可用资源：
{resources_text}

## 输出要求：

生成一个 `prep_plans` 数组，**按面试题分组**，每组包含具体的准备步骤：

```json
{{
  "prep_plans": [
    {{
      "target_question": "完整的面试题原文",
      "skill_focus": "考察的核心技能",
      "prep_items": [
        {{
          "type": "knowledge_review",
          "title": "知识复习：XXX",
          "content": "具体要复习的知识点或概念",
          "key_points": ["要点1", "要点2", "要点3"],
          "resources": ["推荐资料1"],
          "time_needed": "30分钟"
        }},
        {{
          "type": "case_preparation", 
          "title": "案例准备：XXX",
          "content": "需要整理的真实项目经验或案例",
          "template": "STAR法则模板（Situation/Task/Action/Result）",
          "checklist": ["检查项1", "检查项2"],
          "time_needed": "1小时"
        }},
        {{
          "type": "practice",
          "title": "模拟练习：XXX",
          "content": "如何进行模拟练习的具体方法",
          "practice_method": "对着镜子练习 / 录音复盘 / 找朋友mock",
          "rounds": 3,
          "time_needed": "45分钟"
        }}
      ],
      "total_prep_time": "约2-3小时",
      "priority": "high",
      "confidence_boost": "从不确定到有信心回答此题"
    }}
  ]
}}
```

### prep_item 的 type 取值及说明：

#### 1. **knowledge_review**（知识复习）
- 适用场景：技术题需要复习理论知识
- 内容：核心概念、原理、最佳实践
- 时间：20-40分钟

#### 2. **case_preparation**（案例准备）
- 适用场景：行为题/项目深挖题需要真实案例
- 内容：STAR法则组织，量化结果
- 时间：1-2小时（最重要！）

#### 3. **practice**（模拟练习）
- 适用场景：所有题型都需要实际演练
- 内容：口头表达、时间控制、流畅度
- 时间：30-60分钟

### priority 取值：
- **high**: ⚡ 必须准备（高频考点或你的弱项）
- **medium**: 📅 建议准备（提升整体表现）

### 准备原则（重要！）：

#### ✅ 要这样做（高质量示例）：

**针对SQL优化面试题的准备计划：**
```json
{{
  "target_question": "你在项目中遇到过慢查询吗？请描述一次具体的优化过程。",
  "skill_focus": "SQL性能优化",
  "prep_items": [
    {{
      "type": "knowledge_review",
      "title": "复习EXPLAIN执行计划解读",
      "content": "理解type/all/rows/Extra/possible_keys等关键字段的含义",
      "key_points": [
        "ALL vs INDEX扫描区别",
        "Using filesort的含义",
        "索引命中规则"
      ],
      "resources": ["MySQL官方文档-EXPLAIN输出格式"],
      "time_needed": "30分钟"
    }},
    {{
      "type": "case_preparation",
      "title": "准备一个真实的慢查询优化案例",
      "content": "从你过往项目中选取一个性能优化的真实案例",
      "template": 
        "情境(S): 在XX项目中，发现XX查询响应时间超过5秒\\n"
        "任务(T): 负责优化该查询，目标降至500ms以内\\n"
        "行动(A): 1)使用EXPLAIN分析... 2)添加复合索引... 3)重写查询...\\n"
        "结果(R): 查询时间从5s降到200ms，日处理效率提升25倍",
      "checklist": [
        "提到EXPLAIN工具使用",
        "有量化的性能数据（提升X%）",
        "说明思考过程（为什么这么做）"
      ],
      "time_needed": "1.5小时"
    }},
    {{
      "type": "practice",
      "title": "模拟面试练习",
      "content": "完整回答3遍，确保在2-3分钟内流畅表述",
      "practice_method": "录音并回听，检查是否清晰、有条理、有时间感",
      "rounds": 3,
      "time_needed": "45分钟"
    }}
  ],
  "total_prep_time": "约2.5小时",
  "priority": "high",
  "confidence_boost": "从'可能答不上'到'能自信流畅地展示优化经验'"
}}
```

#### ❌ 不要这样做（低质量示例）：
```json
{{
  "target_question": "介绍一下你自己",
  "prep_items": [
    {{ "type": "practice", "title": "练习自我介绍", "content": "多练几次" }}
  ]
}}
```
**问题**：太简短，没有指导性

### 输出约束：
1. **每个面试题必须对应一个完整的准备计划**
2. **每题至少包含2-3个prep_items**（知识+案例+练习）
3. **案例准备是重中之重**（behavioral/scenario题尤其重要）
4. **总准备时间要现实**（单题2-4小时，全部准备10-20小时）
5. **提供可操作的checklist和template**
6. **优先处理high priority的题目**
7. **输出纯JSON，不要Markdown代码块标记"""


def _build_gap_based_learning_prompt(gaps: list, knowledge: dict) -> str:
    """回退方案：基于缺口的学习计划（当没有面试题时）"""
    
    gaps_text = ""
    if gaps:
        formatted_gaps = []
        for i, g in enumerate(gaps[:5], 1):
            skill = g.get("skill", g.get("skill_key", "未知"))
            gap_type = g.get("gap_type", "unknown")
            priority = g.get("priority", "medium")
            reason = g.get("reason", "")
            
            formatted_gaps.append(f"{i}. **{skill}** [类型:{gap_type}, 优先级:{priority}]")
            formatted_gaps.append(f"   原因: {reason}")
            formatted_gaps.append("")
        gaps_text = "\n".join(formatted_gaps)
    else:
        gaps_text = "- 无明显能力缺口"
    
    knowledge_text = "暂无推荐资源"
    if knowledge and isinstance(knowledge, dict):
        available_resources = []
        for skill_key, data in knowledge.items():
            if isinstance(data, dict) and data.get('available'):
                docs = data.get('documents', [])
                if docs:
                    for doc in docs[:2]:
                        title = doc.get('title', '未知')
                        available_resources.append(f"  - [{title}]")
        if available_resources:
            knowledge_text = "\n".join(available_resources[:6])
    
    return f"""你是一个务实的职业发展教练。基于当前的能力缺口，给出可执行的改进建议。

## 当前能力缺口：
{gaps_text}

## 可用资源：
{knowledge_text}

## 输出要求：

生成 `tasks` 数组（2-4个高价值任务）：

```json
{{
  "tasks": [
    {{
      "target_skill": "技能名称",
      "action_title": "行动标题",
      "specific_actions": ["步骤1", "步骤2"],
      "expected_outcome": "预期成果",
      "impact_on_matching": "预计提升X分",
      "time_investment": "预估时间",
      "priority": "immediate"
    }}
  ]
}}
```

### 约束：
1. 每个任务必须有≥2个specific_actions且可操作
2. time_investment要现实
3. impact_on_matching尽量量化
4. 最多4个任务
5. 输出纯JSON"""


def build_next_best_action_prompt(gaps: list, score: int) -> str:
    gaps_text = "\n".join([
        f"- {g.get('skill_key') or g.get('skill')}: 优先级={g.get('priority', 'high')}"
        for g in gaps
    ])
    if not gaps_text:
        gaps_text = "- 无明确缺口（当前分数较低，建议全面提升）"
    return f"""根据当前评分和能力缺口，选择最高影响力的下一步行动。

当前总分：{score}
能力缺口：
{gaps_text}

要求：
1. 选择一个最值得立即投入的行动
2. 行动必须有明确的技能目标
3. 解释为什么这个行动影响最大
4. 输出严格 JSON 格式

只输出 JSON，不要 Markdown。格式：
{{"title": "...", "description": "...", "target_skill": "..."}}"""
