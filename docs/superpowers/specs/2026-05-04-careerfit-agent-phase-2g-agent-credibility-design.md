# CareerFit Agent Phase 2G 多 Agent 可信分析设计

日期：2026-05-04
状态：已由用户批准进入实施计划

## 背景

用户在完整体验网站后指出两个核心问题：

- 匹配分析对数据分析师岗位只产出 `Python` 一个评分维度，遗漏 SQL、数据可视化、统计方法、机器学习、A/B 测试等关键要求。
- 产品明面上呈现为多 Agent 协作，但实际只有 `resume_optimizer` 通过 `generate_report_enhancement()` 调用一次大模型，其余节点多数是规则节点或复用同一次 LLM 结果。

这会让 CareerFit 的核心承诺受损：用户看到的是“多 Agent 证据链分析”，实际得到的是“规则解析 + 单次 LLM 文案增强”。Phase 2G 的目标是修复这个可信度断层，而不是扩大到账号、HR、导师或生产级调度。

## 目标

Phase 2G 要让分析结果在三件事上可信：

1. **多维评分可信**：JD 中的主要能力要求必须被抽取成 5-8 个评分维度，不能被固定技能词表漏掉。
2. **多 Agent 协作可信**：关键语义节点有独立职责、独立结构化输出、独立 schema 校验和独立 trace 记录。
3. **知识库引用可信**：RAG 只能展示与岗位族和技能维度相关的知识库证据；低相关结果必须降级为“知识库证据不足”。

## 非目标

- 不让 LLM 决定最终数字分数。
- 不引入登录、多租户、HR 端或导师端。
- 不引入 Celery、Redis、后台 worker 或复杂调度系统。
- 不在 Agent trace、日志、localStorage 或导出内容中展示完整 JD、完整简历或完整 prompt。
- 不把所有节点强行改成 LLM 节点；确定性评分、RAG 检索执行、Integrity Guard 硬规则仍保持可复现。

## 现状问题

当前 `backend/app/agents/graph.py` 的节点顺序包含：

```text
jd_parser
resume_parser
rag_retriever
match_scorer
gap_analyzer
resume_optimizer
interview_coach
learning_planner
next_best_action
```

但当前大模型调用集中在 `backend/app/llm/service.py` 的 `generate_report_enhancement()`，由 `resume_optimizer` 触发一次，并一次性生成：

- 简历建议
- 面试题
- 学习计划
- Next Best Action

后续 `interview_coach`、`learning_planner`、`next_best_action` 并没有独立调用对应 Agent，只是读取同一个 `llm_enhancement`。这会造成 Trace 名称和真实执行方式不一致。

## 推荐架构

采用“混合式多 Agent”：

- 语义抽取和生成型任务允许使用 LLM。
- 最终评分、Integrity Guard 硬规则、RAG 执行保持确定性。
- 每个 LLM Agent 都必须有本地 fallback，LLM 关闭或失败时主路径仍可运行。

### Agent 职责

| Agent | 执行方式 | 职责 | 不允许做的事 |
|---|---|---|---|
| `jd_parser_agent` | LLM 优先 + 规则 fallback | 抽取岗位族、技能维度、权重、JD 证据 | 不得发明 JD 中不存在的要求 |
| `resume_parser_agent` | LLM 优先 + 规则 fallback | 抽取简历技能、项目、证据片段、表达强度 | 不得新增简历事实 |
| `rag_query_planner_agent` | LLM 优先 + 规则 fallback | 为每个技能维度生成检索 query、岗位族过滤和知识类型 | 不直接返回知识库结论 |
| `rag_retriever` | 确定性 RAG | 执行检索、阈值过滤、岗位族过滤 | 不展示低相关文档 |
| `match_scorer` | 确定性评分 | 计算最终数字分数和分项分数 | 不调用 LLM |
| `gap_analyzer_agent` | LLM 可选 + 规则 fallback | 解释缺口类型：缺技能、弱证据、表达不足、知识库不足 | 不改分数 |
| `resume_optimizer_agent` | LLM 优先 + 规则 fallback | 为每个缺口生成诚实简历建议 | 不绕过 Integrity Guard |
| `interview_coach_agent` | LLM 优先 + 规则 fallback | 按技能类别生成差异化面试题 | 不复用简历建议的同一次 LLM 输出 |
| `learning_planner_agent` | LLM 优先 + 规则 fallback | 生成学习路径、练习、资源和验收标准 | 不给泛泛“做个项目” |
| `next_best_action_agent` | 确定性排序 + LLM 润色 | 选择最高影响下一步行动 | 不选择无证据行动 |
| `integrity_guard_agent` | 硬规则 + LLM critic 可选 | 拦截夸大、无证据、prompt injection、伪积极结论 | 不吞掉风险 |

### 数据流

```text
raw_jd + raw_resume
  -> jd_parser_agent
  -> resume_parser_agent
  -> rag_query_planner_agent
  -> rag_retriever
  -> match_scorer
  -> gap_analyzer_agent
  -> resume_optimizer_agent
  -> integrity_guard_agent
  -> interview_coach_agent
  -> learning_planner_agent
  -> next_best_action_agent
  -> report_composer
```

`match_scorer` 是可信边界：它只消费结构化输入和证据，不消费 LLM 的最终分数字段。即使 LLM 输出“100 分”，也不能进入最终分数。

## 数据结构

### `AgentExecutionMeta`

每个 trace 节点增加执行元数据：

```json
{
  "execution_mode": "llm | rule | rag | deterministic",
  "agent_role": "jd_parser_agent",
  "model_name": "deepseek-chat",
  "fallback_used": false,
  "schema_valid": true,
  "retry_count": 0,
  "input_summary": "已脱敏摘要",
  "output_summary": "已脱敏摘要"
}
```

如果 LLM 关闭：

```json
{
  "execution_mode": "rule",
  "model_name": null,
  "fallback_used": true,
  "schema_valid": true
}
```

### `SkillDimension`

JD 解析输出不再只是 `required_skills: string[]`，而是结构化维度：

```json
{
  "name": "SQL",
  "canonical_key": "sql",
  "category": "data_analysis",
  "weight": 0.2,
  "required_level": "project_practice",
  "jd_evidence": ["熟练使用 SQL 进行数据提取和分析"],
  "aliases": ["SQL", "数据库查询"]
}
```

规则：

- 每个 `weight` 必须在 0-1 之间。
- 所有维度权重归一化后参与评分。
- `jd_evidence` 为空的维度不得参与最终评分。
- 数据分析师 JD 至少应覆盖 SQL、Python、统计/实验、数据可视化、业务分析中的多个维度；如果 JD 本身缺失，则不强行补齐。

## RAG 相关性规则

RAG 检索增加三层过滤：

1. **岗位族过滤**：数据分析岗优先检索 `data_analysis`、`statistics`、`analytics_interview` 类型文档。
2. **技能维度过滤**：每个维度用独立 query，而不是只用技能名。
3. **相关性阈值**：低于阈值的结果不展示，返回“知识库证据不足”。

如果没有数据分析相关种子文档，系统不能用后端开发或大模型应用文档顶替。

## 前端展示

Agent Trace 不再只展示技术节点名，而是展示用户能理解的执行方式：

- “解析岗位要求（LLM）”
- “解析简历证据（LLM）”
- “规划知识库检索（LLM）”
- “检索知识库（RAG）”
- “计算匹配分数（确定性规则）”
- “检查真实性风险（规则 + LLM 复核）”

展开详情时展示技术名、模型名、fallback、schema 校验和重试次数。默认不展示完整 prompt、完整 JD、完整简历、完整检索结果。

## 验收标准

使用评价报告中的数据分析师场景重新跑分析，必须满足：

- 至少产出 5 个评分维度。
- 维度中包含 SQL、Python、数据可视化、统计/A/B 测试或机器学习中的多个实际 JD 要求。
- RAG 不展示 FastAPI、后端岗位画像、大模型应用等明显无关文档。
- 简历建议、面试题、学习任务不再是单一模板。
- Agent Trace 显示至少 4 个不同执行方式或独立 Agent 产物：LLM、RAG、确定性评分、Integrity Guard。
- LLM 关闭时主路径仍可完成，并明确显示 fallback。

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| LLM 成本和延迟增加 | 只给关键语义节点接 LLM；支持配置开关；失败走 fallback |
| LLM 输出不稳定 | 所有输出走 Pydantic schema；非法 JSON 最多修复一次 |
| LLM 改变评分 | `match_scorer` 不读取 LLM 分数字段 |
| Trace 泄露 PII | trace 只保存脱敏摘要；prompt 和原文不进入对外响应 |
| RAG 仍召回无关内容 | 岗位族过滤 + 阈值 + 低相关降级 |

## 文档同步

本设计需要同步：

- `docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md`
- `docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2g-test-plan.md`
- `TODOS.md`
- 外部测试计划副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md`
