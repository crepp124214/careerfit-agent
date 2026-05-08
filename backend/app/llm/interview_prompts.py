"""
独立的面试题生成Prompt
支持：
1. 完全独立调用（不依赖匹配分析）
2. 多种题型（技术/行为/场景/项目深挖）
3. 基于简历项目经验定制深挖题
"""

def build_interview_questions_prompt_independent(
    skills: list[str],
    target_job: str = "",
    resume_context: str = "",
    question_types: list[str] = None,
    difficulty: str = "mixed",
    count: int = 10
) -> str:
    """
    生成独立面试题的Prompt
    
    Args:
        skills: 目标技能列表 (如 ["SQL", "Python", "A/B测试"])
        target_job: 目标岗位名称 (如 "数据分析师")
        resume_context: 简历或项目经历文本（用于生成项目深挖题）
        question_types: 题型过滤 (如 ["technical", "project_deep_dive"])
        difficulty: 难度 ("easy" / "medium" / "hard" / "mixed")
        count: 生成题目数量
    """
    
    # 默认包含所有题型
    if not question_types:
        question_types = ["technical", "behavioral", "scenario", "project_deep_dive"]
    
    has_project_context = bool(resume_context and len(resume_context) > 50)
    
    skills_text = "\n".join([f"- {skill}" for skill in skills])
    
    types_text = "\n".join([f"- {qt}" for qt in question_types])
    
    # 构建简历上下文部分
    context_section = ""
    if has_project_context:
        context_section = f"""
## 📋 候选人的项目/工作经历（用于生成项目深挖题）：

```
{resume_context[:2000]}
```

**重要**：基于以上真实经历，生成针对性的项目深挖问题。引用具体的项目名称、数据、技术栈。
"""
    else:
        context_section = """
## 📋 候选人背景：
未提供详细简历信息。如果选择生成"项目深挖题"，将基于技能要求生成通用型项目场景题。
"""
    
    return f"""你是一个资深的**技术面试官**和**人才评估专家**。请根据以下要求，生成高质量的面试题库。

## 🎯 目标岗位：{target_job or '通用技术岗位'}

## 💡 目标技能：
{skills_text}

## 🔍 题型要求（请为每种指定类型都出题）：
{types_text}

## ⚙️ 难度设置：{difficulty.upper()}

## 📊 题目数量：约{count}道

{context_section}

---

## 输出格式：

```json
{{
  "questions": [
    {{
      "id": 1,
      "skill": "SQL性能优化",
      "type": "project_deep_dive",
      "difficulty": "hard",
      "question": "在字节跳动实习期间，你提到处理过500万+DAU的用户行为数据。能否详细描述一次你遇到的查询性能问题？你是如何定位瓶颈的？用了什么工具（EXPLAIN? 慢查询日志?）？最终怎么优化的？效果如何量化？",
      
      "what_it_tests": [
        "实际问题解决能力",
        "性能分析思路",
        "技术选型依据",
        "量化结果意识"
      ],
      
      "ideal_answer_hints": [
        "应该提到具体的诊断工具和方法",
        "应该说明为什么选择某种优化方案（索引? 重写查询? 分库分表?）",
        "必须有量化的性能提升数据（如：从5s降到200ms）",
        "能体现出系统性思考而非碰运气"
      ],
      
      "follow_up_suggestions": [
        "如果数据量再增长10倍，你的方案还适用吗？",
        "有没有考虑过读写分离或缓存策略？"
      ]
    }}
  ],
  "generation_meta": {{
    "total_count": 10,
    "by_type": {{
      "technical": 3,
      "behavioral": 2,
      "scenario": 2,
      "project_deep_dive": 3
    }},
    "by_difficulty": {{
      "easy": 2,
      "medium": 5,
      "hard": 3
    }}
  }}
}}
```

---

## 📖 题型详解与示例

### 1️⃣ **technical**（技术知识题）
**考察点**：原理理解、语法掌握、最佳实践

**✅ 好的技术题**：
- "请解释SQL中JOIN的几种类型（INNER/LEFT/RIGHT/CROSS），它们在什么场景下使用？"
- "Python中list和tuple的区别是什么？什么情况下你会选择其中一个？"

**❌ 差的技术题**：
- "你知道SQL吗？"（太泛泛）

---

### 2️⃣ **behavioral**（行为经历题）
**考察点**：软技能、团队协作、抗压能力、成长性
**方法**：STAR法则（情境-任务-行动-结果）

**✅ 好的行为题**：
- "描述一次你在项目中与产品经理意见不一致的情况，你是如何解决的？"
- "讲一个你失败的经历，你从中学到了什么？"

---

### 3️⃣ **scenario**（场景设计题）
**考察点**：系统思维、方案权衡、业务理解

**✅ 好的场景题**：
- "如果要你设计一个实时的用户行为分析系统，数据延迟要求在5秒内，你会怎么设计架构？"
- "A/B测试中发现实验组和对照组的差异不显著，你会怎么排查原因？"

---

### 4️⃣ **project_deep_dive**（项目深挖题）⭐ 核心亮点！
**考察点**：真实项目经验深度、问题解决能力、技术决策过程

**特点**：
- **具体化**：引用候选人的真实项目和数字
- **开放性**：没有标准答案，考察思维过程
- **层次性**：可以从表面问到深层（follow-up ready）
- **真实性**：基于候选人的真实经历，无法编造

#### ✅ 好的项目深挖题示例：

**输入（简历片段）**：
> 在字节跳动做数据分析实习生（2022.07-2022.10）  
> - SQL提取抖音DAU 500万+用户行为数据  
> - 复杂SQL查询分析用户留存率  
> - Python pandas处理A/B测试数据验证改版效果提升12%

**生成的题目**：

```json
{{
  "skill": "SQL + 数据分析",
  "type": "project_deep_dive",
  "difficulty": "hard",
  "question": "在字节跳动实习期间，你负责分析500万+DAU的用户留存数据。能否完整描述一次你的分析流程？从数据提取到最终结论，你用了哪些工具？遇到过数据质量问题吗？如何处理的？最终的分析结果对产品决策有什么影响？",
  
  "what_it_tests": [
    "端到端数据分析能力",
    "数据处理和清洗经验",
    "商业敏感度和数据 storytelling",
    "工具链熟练度"
  ],
  
  "ideal_answer_hints": [
    "应该描述完整的数据管道（提取→清洗→分析→可视化）",
    "应该提到具体的数据质量问题和处理方法（缺失值? 异常值?）",
    "应该说明分析结果如何被使用（推动产品改进? 影响决策?）",
    "能体现出不仅是'跑数'，而是有业务思考"
  ]
}}
```

#### ❌ 差的项目深挖题：

- "你有数据分析经验吗？"（太泛泛，不是深挖）
- "介绍一下你的项目。"（没有针对性）

---

## 🎯 出题策略

### 按难度分配（如果是mixed模式）：
- **easy (20%)**: 基础概念热身题（1-2道）
- **medium (50%)**: 标准技术/行为题（大部分题目）
- **hard (30%)**: 深度/场景/项目深挖题（区分候选人）

### 按题型分配：
- 如果 `has_project_context`：
  - **project_deep_dive (30-40%)**: 重点！基于真实经历
  - **technical (30%)**: 验证基础
  - **behavioral (20%)**: 软技能
  - **scenario (10-20%)**: 系统思维
  
- 如果 `no project_context`:
  - **technical (40%)**: 更多技术题
  - **scenario (30%)**: 场景设计
  - **behavioral (20%)**
  - **project_deep_dive (10%)**: 通用型项目场景题

### 质量标准（每道题必须满足）：

1. **具体可回答**：不能太宽泛（避免"介绍一下XX"）
2. **有明确目的**：`purpose` 或 `what_it_tests` 清晰
3. **层次分明**：easy/medium/hard 区分明显
4. **真实性**：项目深挖题必须基于提供的上下文
5. **可Follow-up**：好的题目可以引出后续深入问题

---

## ⚠️ 重要约束

1. **每种指定的question_type至少生成1-2道题**
2. **总题目数量控制在{count}道左右（±2道）**
3. **项目深挖题必须引用具体的数字/项目名/技术栈**（如果有提供resume_context）
4. **每道题都要有 what_it_tests 和 ideal_answer_hints**
5. **输出纯JSON，不要Markdown代码块标记**
6. **难度要合理分布，不要全是hard**

---

## ✨ 高质量题目 Checklist

在输出前，检查每道题是否满足：

- [ ] 题目长度 > 20字符（太短=太简单）
- [ ] 不是Yes/No问题
- [ ] 有明确的考察维度
- [ ] 项目深挖题引用了具体上下文
- [ ] 提供了ideal_answer_hints（帮助评估者打分）

请开始生成面试题！"""


def build_interview_prep_from_questions_prompt(
    selected_questions: list[dict],
    prep_depth: str = "standard"
) -> str:
    """
    基于选定的面试题生成准备计划
    
    Args:
        selected_questions: 选定的面试题列表（每个包含 skill, question, type, difficulty）
        prep_depth: 准备深度 ("quick" / "standard" / "comprehensive")
    """
    
    questions_text = ""
    for i, q in enumerate(selected_questions, 1):
        skill = q.get('skill', '未知')
        qtype = q.get('type', 'unknown')
        difficulty = q.get('difficulty', 'medium')
        question_text = q.get('question', '')
        
        questions_text += f"{i}. **[{difficulty.upper()}] [{qtype}] {skill}**\n"
        questions_text += f"   题目: {question_text}\n\n"
    
    depth_guide = {
        "quick": "每个题目准备30-60分钟，聚焦核心要点",
        "standard": "每个题目准备1-2小时，包含知识复习+案例+练习",
        "comprehensive": "每个题目准备2-4小时，深度准备到能自信流畅回答"
    }
    
    return f"""你是一个资深的**面试辅导专家**。根据以下选定的面试题，制定精准的面试准备计划。

## 📋 选定的面试题（共{len(selected_questions)}道）：

{questions_text}

## 🎯 准备深度：{prep_depth.upper()}
{depth_guide.get(prep_depth, '')}

---

## 输出要求：

生成一个 `prep_plans` 数组，**每道面试题对应一个完整的准备计划**：

```json
{{
  "prep_plans": [
    {{
      "target_question_id": 1,
      "target_question": "完整的面试题原文",
      "skill_focus": "考察的核心技能",
      "question_type": "technical | behavioral | scenario | project_deep_dive",
      "difficulty": "medium",
      
      "prep_items": [
        {{
          "type": "knowledge_review",
          "title": "知识复习：XXX",
          "content": "具体要复习的知识点",
          "key_points": ["要点1", "要点2"],
          "resources": [{"name": "资源", "url": "链接"}],
          "time_needed": "30分钟",
          "priority": "must_have"
        }},
        {{
          "type": "case_preparation",
          "title": "案例/项目准备：XXX",
          "content": "需要整理的真实案例",
          "template": "STAR模板（Situation/Task/Action/Result）",
          "checklist": ["检查项1", "检查项2"],
          "time_needed": "1小时",
          "priority": "critical"
        }},
        {{
          "type": "practice",
          "title": "模拟练习：XXX",
          "content": "如何进行模拟练习",
          "method": "录音复盘 / 找朋友mock",
          "rounds": 3,
          "time_needed": "45分钟",
          "priority": "recommended"
        }}
      ],
      
      "total_prep_time": "约2小时",
      "priority": "high",
      "confidence_before": "不确定/紧张",
      "confidence_after": "能自信流畅地回答"
    }}
  ]
}}
```

---

## 准备项类型说明：

### 1. **knowledge_review**（知识复习）- priority: must_have
- 适用：所有技术题
- 内容：核心概念、原理、常见陷阱
- 时间：20-40分钟

### 2. **case_preparation**（案例准备）- priority: **critical**
- 适用：行为题、项目深挖题（最重要！）
- 内容：STAR法则组织，量化结果
- 时间：1-2小时
- **这是最关键的部分！**

### 3. **practice**（模拟练习）- priority: recommended
- 适用：所有题型
- 方法：口头表达、时间控制、流畅度
- 时间：30-60分钟

---

## 📌 深度级别调整：

### quick（快速准备）：
- 每题只生成2个prep_items：[case_preparation, practice]
- 总时间：每题45-60分钟
- 适用：时间紧迫，只需过一遍

### standard（标准准备）【推荐】：
- 每题生成3个prep_items：[knowledge_review, case_preparation, practice]
- 总时间：每题1.5-2.5小时
- 适用：正常准备节奏

### comprehensive（深度准备）：
- 每题生成4-5个prep_items：增加 follow-up准备、难点攻克等
- 总时间：每题3-4小时
- 适用：重要面试前的充分准备

---

## ⚠️ 重要约束：

1. **每道选定题目必须有对应的准备计划**
2. **case_preparation 是必需的**（对于behavioral和project_deep_dive题）
3. **提供具体的STAR模板**（不要只说"用STAR法则"，要给例子）
4. **time_needed 要现实**
5. **输出纯JSON**

请开始生成准备计划！"""
