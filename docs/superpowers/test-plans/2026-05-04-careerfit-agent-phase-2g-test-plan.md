# CareerFit Agent Phase 2G 测试计划

日期：2026-05-04
版本：v1

## 测试目标

Phase 2G 测试验证两件事：

1. 数据分析师场景下，CareerFit 能产出多维度、有证据、有相关知识库引用的可信报告。
2. 产品展示的多 Agent 协作是真实可追踪的：关键语义节点有独立 Agent 产物、独立 schema 校验、独立 trace 元数据和 fallback。

## 后端测试

### Agent schema

运行：

```powershell
cd backend
pytest tests/test_agent_schemas.py -q
```

必须覆盖：

- `SkillDimension.weight` 限制在 0-1。
- `SkillDimension.jd_evidence` 不能为空。
- `JDParseOutput`、`ResumeParseOutput`、`RagQueryPlanOutput`、`GapAnalysisOutput`、`ResumeSuggestionOutput`、`InterviewQuestionOutput`、`LearningPlanOutput`、`NextBestActionOutput`、`IntegrityCriticOutput` 都使用 `extra="forbid"`。
- 非法 LLM 字段会触发 `ValidationError`，不能被静默吞掉。

### 多 Agent LLM 执行器

运行：

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py -q
```

必须覆盖：

- 非法 JSON 最多修复重试一次。
- 修复后仍失败时节点失败，不吞错。
- LLM 关闭时走 fallback，`execution_mode="rule"`。
- LLM 开启时至少记录以下独立 agent role：
  - `jd_parser_agent`
  - `resume_parser_agent`
  - `rag_query_planner_agent`
  - `gap_analyzer_agent`
  - `resume_optimizer_agent`
  - `interview_coach_agent`
  - `learning_planner_agent`
  - `next_best_action_agent`
- `match_scorer` 不调用 LLM。
- 第二次 JSON 修复仍失败时，trace 必须记录 `schema_valid=false`、`retry_count=1`、`error_code`，不得丢失失败节点。

### AgentRun 持久化与 API 契约

运行：

```powershell
cd backend
pytest tests/test_analysis_flow.py::test_agent_run_execution_meta_persisted_and_returned -q
```

必须覆盖：

- `run_workflow` 产出的 `execution_meta` 能落库到 `agent_runs`。
- `GET /api/agent-runs/{task_id}` 返回 `execution_meta`。
- `execution_meta` 至少包含 `execution_mode`、`agent_role`、`fallback_used`、`schema_valid`、`retry_count`。
- 旧 trace 字段 `input_snapshot`、`output_snapshot` 仍然存在，且继续脱敏。

### 数据分析维度抽取

运行：

```powershell
cd backend
pytest tests/test_data_analysis_dimension_extraction.py -q
```

必须覆盖：

- 数据分析师 JD 至少抽取 5 个维度。
- 必须识别 SQL、Python、数据可视化、统计方法、A/B 测试。
- 简历中对应技能必须能抽取证据。
- 旧软件工程岗位样例仍能解析，不因新目录破坏兼容。
- `SQLAlchemy` 不得被误识别为数据分析 SQL。
- 单纯的 React dashboard 前端经历不得被误识别为数据可视化分析能力。

### 评分确定性

运行：

```powershell
cd backend
pytest tests/test_scoring.py tests/test_scoring_with_rag.py -q
```

必须覆盖：

- `score_match()` 优先消费 `skill_dimensions`。
- 没有 `skill_dimensions` 时回退 `required_skills`。
- 最终分数始终 clamp 到 0-100。
- RAG 只作为知识库证据，不改变最终分数。
- LLM 输出不得直接进入最终数字分数。

### RAG 相关性

运行：

```powershell
cd backend
pytest tests/test_rag_relevance_filtering.py tests/test_rag_retrieval.py tests/test_rag_agent_node.py -q
```

必须覆盖：

- 数据分析岗不能召回 FastAPI、后端岗位画像、大模型应用等无关文档。
- 低于阈值的文档被过滤。
- 文档岗位族不匹配时被过滤。
- 无相关文档时返回“知识库证据不足”。
- 数据分析种子文档成功导入。
- `analysis_service` 集成路径必须证明数据分析 JD 的最终报告不包含 FastAPI、后端开发岗位画像或大模型应用等无关文档。

### 生成内容质量

运行：

```powershell
cd backend
pytest tests/test_interview_service.py tests/test_learning_api.py tests/test_llm_agent_flow.py -q
```

必须覆盖：

- 面试题不再全部使用“请说明你在 X 上最具体的一次实践”模板。
- SQL 题包含查询、关联、窗口函数或性能类题型。
- A/B 测试题包含实验设计、指标或显著性。
- 数据可视化题包含图表选择、看板或指标解释。
- 学习任务包含路径、练习、资源或验收标准，不只是“做一个小项目”。
- 简历建议逐维度生成，并包含 JD 要求、简历证据和风险等级。
- 每个高优先级缺口至少生成一条具体建议。
- 学习任务必须包含顺序、练习、资源或验收方式，不能只是“完成一个小项目”。

### Prompt 与 trace PII

运行：

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py::test_prompt_and_trace_do_not_persist_raw_jd_resume -q
```

必须覆盖：

- 除 `jd_parser_agent` 和 `resume_parser_agent` 的受控解析边界外，其他 Agent prompt 不接收完整 JD/简历。
- repair prompt 不无限制回传模型首次输出，避免二次传播原文或注入内容。
- trace、异常详情、日志、API 响应不包含完整 JD、完整简历、完整 prompt 或 API key。
- RAG `content_snippet` 只能来自知识库标准文档，不得混入用户 JD/简历片段。

## 前端测试

### Agent Trace 展示

运行：

```powershell
cd frontend
npm test -- AgentTraceTimeline
```

必须覆盖：

- 技术节点名映射为中文：
  - `jd_parser` -> “解析岗位要求”
  - `resume_parser` -> “解析简历证据”
  - `rag_query_planner` -> “规划知识库检索”
  - `rag_retriever` -> “检索知识库”
  - `match_scorer` -> “计算匹配分数”
  - `integrity_guard` -> “检查真实性风险”
- 展示执行方式：LLM、本地规则、RAG、确定性规则。
- 展示模型名、fallback、schema 校验、JSON 修复重试次数。
- 不渲染 `raw_jd`、`raw_resume`、完整 prompt 或 API key。
- `frontend/src/api/agentRuns.ts` 必须用真实后端响应 shape 测试 `execution_meta` normalize，不能只靠组件手写 props。
- 移动端 375px 下，多个 badge 和技术字段不得挤爆或遮挡主要报告内容。

### 报告页

运行：

```powershell
cd frontend
npm test -- ReportView
```

必须覆盖：

- 多维评分卡正常渲染。
- 知识库证据不足时显示中文提示。
- 无关知识库文档不出现在报告中。
- 面试题和学习任务展示新增结构字段。
- Next Best Action 仍在报告头部显眼位置。
- 报告页必须有分组或折叠策略，默认不把评分、证据、建议、面试、学习、Trace 全部无层级堆叠。

## 集成回归

### 后端完整回归

运行：

```powershell
cd backend
pytest -q
```

必须通过。

### 前端完整回归

运行：

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

必须通过。

### Docker 回归

运行：

```powershell
docker compose up --build
```

必须验证：

- backend、postgres、frontend healthy。
- `/api/capabilities` 返回 `llm`、`knowledge`、`interview` 可识别状态。
- 创建数据分析师 JD 和简历后能完成分析。
- 报告页显示多维度评分和 Agent Trace 执行方式。

如果 Docker daemon 未运行，必须在最终说明和 `TODOS.md` 中保留未完成原因。

## PII 与安全审计

PII 入口逻辑变更后必须运行 `gstack:cso`。若本机仍无可执行入口，必须写本地等价审计记录，检查：

- LLM prompt 不包含完整 JD/简历原文。
- Agent trace 对外响应不包含完整 JD/简历/prompt/API key。
- 日志不输出 prompt、API key、原文。
- localStorage / IndexedDB 不保存原文。
- Prompt injection 样例不会改变最终评分。

## 手工验收场景

使用以下数据分析师 JD：

```text
岗位：数据分析师
要求：熟练使用 SQL 进行数据提取、清洗和多表关联分析；
熟悉 Python 进行数据处理和自动化分析；
能够使用 Tableau、Power BI 或 ECharts 完成数据可视化；
理解统计方法，能够设计 A/B 测试并评估显著性；
了解机器学习基础，能与算法团队协作完成特征分析。
```

使用以下简历片段：

```text
使用 Python 和 pandas 清洗 20 万行运营数据，完成留存分析。
使用 SQL 编写多表关联查询和窗口函数，支持销售看板。
使用 ECharts 构建包含折线图、漏斗图和转化率指标的数据看板。
参与 A/B 测试结果分析，使用统计检验判断实验效果。
```

验收：

- 报告至少有 5 个评分维度。
- 总分不被单一 Python 维度主导。
- SQL、Python、数据可视化、A/B 测试均有简历证据。
- RAG 不展示后端开发或 FastAPI 文档。
- 面试题至少包含 SQL、A/B 测试、数据可视化三类不同题型。
- Agent Trace 至少展示 LLM、RAG、确定性规则、本地规则或 Integrity Guard 四类执行信息。

## 文档检查

运行：

```powershell
git diff --check
```

必须通过。

## 外部副本

本测试计划更新后必须同步：

```powershell
Copy-Item docs\superpowers\test-plans\2026-05-04-careerfit-agent-phase-2g-test-plan.md C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md
```
