# CareerFit Agent TODOS

日期：2026-05-04
版本：v9（清理过时事项；Phase 2G 为当前执行范围）

## 适用范围与文件优先级

- 本文件不覆盖 `CLAUDE.md`。如有冲突，以 `CLAUDE.md` 中的"当前核心产品约束"、"Phase 1 验收门"、"前端实现约束"、"隐私与安全约束"为准。
- Phase 1 范围分类与 `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md` 中的 T1–T13 任务清单一一对应；Phase 2+ 范围以对应 `docs/superpowers/plans/2026-05-*` 实施计划为准。
- 任何范围变化必须同步更新本文件、实施计划、测试计划与设计文档（`CLAUDE.md` 实施文档实时更新约束）。

## Phase 1 in-scope（不延后）

以下事项原本可能因主路径优先级被列为延后，但在双门重写后已明确归入 Phase 1，必须随计划完成。

### 总体当前进度（含 Phase 2）

- [x] **前端 Phase 1.A（T1–T7）**：全部完成。77 测试通过，typecheck clean，Docker 化就绪，10/10 验收门 PASS。
- [x] **后端 Phase 1.B（T8–T11）**：由 Codex 完成。15 测试通过，可信主路径端到端闭环。
- [x] **全栈集成（T12–T13）**：已完成。全栈 Docker Compose 三容器 healthy，README 中文版就绪，双验收门全部通过。第三轮联调修复：Agent Trace 中间态 evidence 脱敏、报告页适配真实后端 snake_case 响应、favicon 404 修复、healthcheck localhost→127.0.0.1。
- [x] **Phase 2A 学习任务闭环**：已完成，学习任务后端、前端状态机和验证门通过。
- [x] **Phase 2B 历史趋势与版本对比**：功能与测试已完成；Docker fullstack 复验因本机 Docker daemon 未运行保留未完成。
- [x] **Phase 2C 多模型后端代理**：已完成，LLM 配置、client、fallback、PII 审计记录已落地。
- [x] **Phase 2D RAG 知识库**：功能与测试已完成；Docker fullstack 复验和文档 diff 仍需补跑。
- [x] **Phase 2E 面试训练闭环**：功能、前端构建和浏览器端到端测试已完成；Docker 与文档 diff 仍需补跑。
- [x] **Phase 2F 报告导出**：Markdown 导出与打印/PDF HTML 已完成。
- [ ] **Phase 2G 多 Agent 可信分析**：已完成设计、实施计划、测试计划与外部测试计划同步；代码实现尚未开始。

### 前端 Phase 1.A（T1–T7）

- 13 条 Vue Router 路由全部铺出，缺一不可。
- 工作台、Jobs/Resumes 列表与详情、分析提交、报告、HistoryView、VersionDiffView、LearningTasksView、AgentTraceView、SettingsView 全部支持空/加载/错误/部分数据状态机。
- 共享组件 TDD：`AppButton`、`RiskPill`（双通道）、`BackendNotReadyNotice`、`NextBestActionCallout`、`IntegrityGuardBanner`、`EvidenceCard`、`ScoringDimensionCard`、`ScoringOverviewCard`、`SuggestionCard`、`AgentTraceTimeline`、`AgentTraceRow`。
- `availability` Pinia store 消费 `/api/capabilities`；`frontend-only` 与 `fullstack` 两种模式均覆盖。
- 后端缺口必须用 `BackendNotReadyNotice` 用户可见占位；禁止 mock 数据。
- `useLocalStorageRef` + PII 白名单 + 内存回落；`careerfit:pref:*` 命名空间严格限定。
- 完整响应式：1440 / 1280 / 1024 / 768 / 480 五档。
- 完整无障碍：键盘可达 + ARIA + WCAG AA（axe-core 校验工作台、报告、Jobs、Settings 四视图）。
- 关键交互动效 200–300ms 过渡，禁止硬切换。
- `frontend/Dockerfile` 多阶段（nginx 运行）+ `docker-compose.frontend-only.yml` 可独立 `up --build`。

### 后端 Phase 1.B（T8–T11）

- 目标岗位、简历版本、分析任务、报告、Agent runs 的端到端可信主路径。
- 评分确定性：维度 clamp 0–100、原始因子持久化、LLM 不直接决定数字分。
- Integrity Guard：阻止无证据指标与夸大职责；最终输出前必须运行。
- Agent Trace 脱敏：服务端原始快照与对外响应分离。
- `/api/capabilities`：响应 schema 含 `schema_version`，缺失字段 fallback `pending`，每个后端任务完成后翻 `ready`。
- LangGraph 节点输出 Pydantic 校验；非法 JSON 仅允许 1 次修复重试。
- RAG 检索证据足够时才出结论，否则标记"知识库证据不足"。

### 全栈集成（T12–T13）

- `docker-compose.yml` 全栈启动：postgres + pgvector + backend + frontend（`fullstack` 变体）。
- README 中文版：`frontend-only`、`fullstack` 两种启动方式与验收门 checklist。
- 集成主路径端到端 UI 走查（10 步主路径 + 模式切换 11/12 步）。

## 决策点（不允许静默选）

以下事项有合理但相互冲突的选项，必须显式决策并记录在实施计划对应任务的"决策记录"区。

| 决策点 | 选项 A | 选项 B | 当前默认 |
|---|---|---|---|
| LangGraph 接入方式 | 真 LangGraph 编排器 | 本地顺序 runner + 兼容 workflow boundary | 选 B，但保留切换边界（`CLAUDE.md` 依赖与技术取舍） |
| 测试 DB | SQLite + 行为差异显式覆盖 | PostgreSQL Docker 集成 + 不跑 SQLite | 双轨：单测用 SQLite，集成测试用 PostgreSQL |
| Agent trace 服务端原始快照保留期 | 仅本地开发保留 | 始终保留并显式 TTL（如 7 天） | 选 A，生产部署前再决议 |
| 前端 UI 库 | 无 UI 库纯手写 | 引入轻量库（如 Reka UI / Radix Vue） | 选 B：Reka UI（Phase 4 D4 审批通过） |
| 前端图表库 | Chart.js | ECharts | 选 B：ECharts（Phase 4 D5 审批通过） |
| 前端动效库 | 仅 CSS transitions | VueUse Motion / GSAP | 默认 CSS，复杂动效再决议 |
| 后端 SQLAlchemy 异步 vs 同步 | 全异步 | 同步 + worker 边界 | 选 B：同步 Phase 1（Phase 4 D6 审批通过） |

每次决策须写明：选择哪个、理由、影响范围、回滚条件。

## Phase 1.5 收口（Phase 2A 前置门）

以下事项必须在 Phase 2A 功能实现前完成或记录阻塞原因。

- [x] 补写 3 条 review-log：`plan-ceo-review` / `plan-design-review` / `plan-eng-review`，含 Hold Scope、设计验收和工程质量门结论。
- [x] 对 T8–T11 的 PII 入口逻辑运行 `gstack:cso` OWASP + STRIDE 安全审计；当前环境没有 `gstack:cso` 可执行入口，已在 review-log 记录失败命令，并按本地 skill 文档完成等价 PII 基线审计。
- [x] 创建 Phase 2A 实施计划：`docs/superpowers/plans/2026-05-03-careerfit-agent-phase-2a-learning-loop.md`。
- [x] 创建 Phase 2A 测试计划：`docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2a-test-plan.md`。
- [x] 同步 Phase 2A 测试计划外部副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2a-test-plan-2026-05-03-careerfit-agent.md`。

## Phase 2A 已完成范围：学习任务与成长闭环

目标：把 Phase 1 的报告结论转化为真实可推进的学习任务，让 `Next Best Action` 不止是建议，而是能落到任务、状态和下一步行动。

### 后端 Phase 2A

- [x] 新增 `learning_tasks` 持久化模型，关联 `analysis_tasks` / `analysis_reports`。
- [x] 新增 `backend/app/schemas/learning.py`，响应字段包含 `schema_version`。
- [x] 新增 `backend/app/services/learning_service.py`，从 `learning_plan`、`gaps`、`next_best_action` 幂等生成任务。
- [x] 新增 `backend/app/api/routes/learning.py`：
  - `GET /api/learning/tasks`
  - `POST /api/learning/tasks/generate`
- [x] 补齐 `PATCH /api/learning/tasks/{id}` 状态更新接口。
- [x] `CAPABILITIES.learning` 从 `unavailable` 翻为 `ready`。
- [x] 学习任务响应不得包含原始简历/JD 文本。
- [x] 状态流转覆盖 `not_started`、`doing`、`done`、`paused`，拒绝非法状态。

### 前端 Phase 2A

- [x] 更新 `frontend/src/api/learning.ts`，匹配真实后端契约。
- [x] 新增 `frontend/src/stores/learning.ts`，支持加载、生成、状态更新。
- [x] `LearningTasksView` 从占位升级为真实状态机：空、加载、错误、部分数据、有数据、后端不可用。
- [x] 工作台和报告页的 `Next Best Action` CTA 指向 `/learning` 或只携带 ID 的 `/learning?taskId=<id>`。
- [x] 前端不得把学习任务详情、简历原文、JD 原文或 Agent trace 原文写入 localStorage / IndexedDB。

### Phase 2A 验证门

- [x] 后端：`cd backend && pytest tests/test_learning_api.py -q && pytest -q`。
- [x] 前端：`cd frontend && npm test && npm run typecheck && npm run build`。
- [x] Docker：`docker compose up --build`，确认 fullstack 模式 `/api/capabilities` 返回 `learning: "ready"`。
- [x] 文档：`git diff --check`。

## Phase 2B 已完成范围：历史趋势与版本对比

目标：把学习任务后的复盘闭环补起来，让用户能看到“有没有变好”和“两个简历版本到底改了什么”。

### Phase 2B 文档与计划

- [x] 用户选择方案 A：历史趋势 + 版本对比。
- [x] 创建 Phase 2B 设计文档：`docs/superpowers/specs/2026-05-03-careerfit-agent-phase-2b-history-diff-design.md`。
- [x] 创建 Phase 2B 实施计划：`docs/superpowers/plans/2026-05-03-careerfit-agent-phase-2b-history-diff.md`。
- [x] 创建 Phase 2B 测试计划：`docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2b-test-plan.md`。
- [x] 同步 Phase 2B 测试计划外部副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2b-test-plan-2026-05-03-careerfit-agent.md`。

### 后端 Phase 2B

- [x] 新增 `GET /api/reports/history`，从已有 `analysis_reports` 派生历史趋势 snapshot。
- [x] 历史趋势支持 `job_id`、`resume_id`、`limit`，不新增派生表。
- [x] 新增 `GET /api/resumes/compare?from_id=&to_id=`，使用确定性行级 diff。
- [x] diff 响应包含 summary、sections 和可选 score context。
- [x] 不在日志、异常详情或 Agent trace 中输出简历原文或 diff 文本。

### 前端 Phase 2B

- [x] 新增 history API/store，把 `/history` 从占位升级为真实趋势视图。
- [x] 新增 resume diff API/store，把 `/diff` 从占位升级为真实版本对比视图。
- [x] `/history` 支持 unavailable、loading、error、empty、partial、ready。
- [x] `/diff` 支持 unavailable、loading、error、empty、partial、ready。
- [x] 图表使用已有 `echarts` / `vue-echarts`，不引入新图表依赖。
- [x] 前端不得把 diff 文本、简历原文、JD 原文写入 localStorage / IndexedDB。

### Phase 2B 验证门

- [x] 后端：`cd backend && pytest tests/test_report_history_api.py tests/test_resume_diff_api.py -q && pytest -q`。
- [x] 前端：`cd frontend && npm test && npm run typecheck && npm run build`。
- [ ] Docker：`docker compose up --build`，确认 fullstack 模式 `/history` 与 `/diff` 可访问并使用真实 API。2026-05-04 尝试运行失败，原因是本机 Docker daemon 未运行，待启动 Docker Desktop 后补跑。
- [x] 文档：`git diff --check`。

## Phase 2C 已完成范围：多模型后端代理

目标：通过后端代理接入国内外常用 OpenAI-compatible 大模型 API，同时不泄露 API Key、不让 LLM 改写确定性评分。

### Phase 2C 文档与计划

- [x] 用户确认方案 A：OpenAI-compatible 优先。
- [x] 创建 Phase 2C 设计文档：`docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2c-llm-proxy-design.md`。
- [x] 创建 Phase 2C 实施计划：`docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2c-llm-proxy.md`。
- [x] 创建 Phase 2C 测试计划：`docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2c-test-plan.md`。
- [x] 同步 Phase 2C 测试计划外部副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2c-test-plan-2026-05-04-careerfit-agent.md`。

### 后端 Phase 2C

- [x] 新增 LLM 环境变量配置，默认关闭。
- [x] 支持 `chat_completions` 与 `responses` 两种 API 风格。
- [x] 新增 LLM client、schema、prompt 和 service。
- [x] 只在生成型节点接入 LLM：简历建议、面试题、学习计划、Next Best Action。
- [x] provider 失败或非法 JSON 时回退本地 fallback。
- [x] `/api/capabilities` 增加 `llm` 状态。
- [x] Agent trace 不保存 API Key、prompt 原文、完整 JD 或完整简历。

### Phase 2C 验证门

- [x] 后端：`cd backend && pytest tests/test_llm_client.py tests/test_llm_agent_flow.py -q && pytest -q`。
- [x] 前端：`cd frontend && npm test && npm run typecheck && npm run build`。
- [x] PII：运行 `gstack:cso` 或记录本地等价 OWASP + STRIDE 审计。当前环境无 CLI 入口，已写入 `docs/superpowers/review-logs/2026-05-04-phase-2c-llm-proxy-security-review.md`。
- [x] 文档：`git diff --check`。

## Phase 2D 已完成范围：RAG 知识库

目标：实现 RAG 知识库，让评分有知识库标准作为第三方参考，面试题和学习任务有外部资源推荐。

### Phase 2D 文档与计划

- [x] 用户确认方案：RAG 知识库优先。
- [x] 创建 Phase 2D 设计文档：`docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2d-rag-knowledge-design.md`。
- [x] 创建 Phase 2D 实施计划：`docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2d-rag-knowledge.md`。
- [x] 创建 Phase 2D 测试计划：`docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2d-test-plan.md`。

### 后端 Phase 2D

- [x] 新增 `knowledge_documents` 表和 pgvector 索引。
- [x] 新增 `backend/app/rag/` 目录（embedding、retrieval、loader）。
- [x] 安装 sentence-transformers 依赖（all-MiniLM-L6-v2，384 维）。
- [x] 新增 `POST /api/knowledge/import` 和 `GET /api/knowledge/search` API。
- [x] 新增 `rag_retriever` Agent 节点，在工作流中 `match_scorer` 之前执行检索。
- [x] 评分层 `score_items` 新增 `knowledge_evidence` 字段。
- [x] 检索不到时标记"知识库证据不足"，不编造来源。
- [x] `/api/capabilities` 增加 `knowledge` 状态。
- [x] 三组种子知识库（后端、前端/全栈、大模型应用），至少 20 篇文档。
- [x] Agent trace 不保存 embedding 向量或完整检索结果。

### 前端 Phase 2D

- [x] EvidenceCard 展示 `knowledge_evidence`（有则展示引用，无则展示"知识库证据不足"）。
- [x] availability store 消费 `knowledge` capability。

### Phase 2D 验证门

- [x] 后端：22 个新增测试全部通过（test_knowledge_api、test_rag_retrieval、test_rag_agent_node、test_scoring_with_rag）。
- [x] 前端：typecheck 和 build 通过。
- [ ] Docker：`docker compose up --build`，确认 `/api/capabilities` 返回 `knowledge: "ready"`。2026-05-04 本机 Docker daemon 未运行，待启动 Docker Desktop 后补跑。
- [ ] 文档：`git diff --check`。

## Phase 2E 已完成范围：面试训练闭环

目标：把面试题从只读列表升级为可练习、可追踪、可复盘的面试训练闭环。

### Phase 2E 文档与计划

- [x] 用户确认方案：面试训练闭环。
- [x] 创建 Phase 2E 设计文档：`docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2e-interview-training-design.md`。
- [x] 创建 Phase 2E 实施计划：`docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2e-interview-training.md`。
- [x] 创建 Phase 2E 测试计划：`docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2e-test-plan.md`。

### 后端 Phase 2E

- [x] 新增 `interview_sessions` 和 `interview_questions` 持久化模型。
- [x] 新增 `POST /api/interview/sessions`，从报告生成面试训练会话（幂等）。
- [x] 新增 `GET /api/interview/sessions`，列出会话。
- [x] 新增 `GET /api/interview/sessions/{id}`，获取会话详情含题目列表。
- [x] 新增 `PATCH /api/interview/sessions/{id}/questions/{qid}`，更新题目状态或笔记。
- [x] 题目分类（basic / project_deep_dive / scenario_design）和难度（easy / medium / hard）自动分配。
- [x] RAG 知识库 `interview` 类型文档补充面试题，去重。
- [x] 状态流转校验：not_started → practicing → completed / skipped，拒绝非法跳转。
- [x] `/api/capabilities` 增加 `interview` 状态。

### 前端 Phase 2E

- [x] 新增 `/interview` 面试训练列表页和 `/interview/:id` 详情页路由。
- [x] InterviewListView：会话卡片列表，支持空/加载/错误/后端不可用状态机。
- [x] InterviewDetailView：题目列表，按技能/类别/难度筛选，练习状态切换，笔记输入，进度条。
- [x] 报告页添加"开始面试训练"CTA 按钮。
- [x] availability store 消费 `interview` capability。

### Phase 2E 验证门

- [x] 后端：27 个新增测试全部通过（test_interview_service + test_interview_api）。
- [x] 前端：typecheck 和 build 通过。
- [x] 浏览器端到端测试：面试训练列表页和详情页正常工作，状态切换正确。
- [ ] Docker：待补跑。
- [ ] 文档：`git diff --check`。

## Phase 2F 已完成范围：报告导出

目标：支持将分析报告导出为 Markdown 和 HTML（可打印为 PDF）。

### 后端 Phase 2F

- [x] 新增 `GET /api/reports/{id}/export?format=markdown`，返回 Markdown 文件。
- [x] 新增 `GET /api/reports/{id}/export?format=pdf`，返回 HTML（可浏览器打印为 PDF）。
- [x] Markdown 内容包含评分详情、技能评分、证据链、优势、缺口、建议、面试题、学习任务和下一步建议。
- [x] 导出内容不包含完整简历原文或 JD 原文（PII 脱敏）。

### 前端 Phase 2F

- [x] 报告页添加"导出 Markdown"和"打印 / PDF"按钮。

### Phase 2F 验证门

- [x] 后端：6 个新增测试全部通过（test_export_api）。
- [x] 前端：typecheck 和 build 通过。
- [x] 浏览器端到端测试：导出按钮正常工作。
- [ ] 文档：`git diff --check` 尚未单独记录到 Phase 2F 验证门。

## Phase 2G 当前范围：多 Agent 可信分析与数据分析岗质量修复

目标：修复用户体验报告中暴露的核心可信度问题：数据分析师 JD 只产出单一 Python 维度、RAG 召回后端/大模型应用等无关文档，以及“多 Agent 协作”实际只有一次 LLM 增强调用。

### Phase 2G 文档与计划

- [x] 用户确认问题：当前明面上是多 Agent 协作，但只有分析增强节点实际调用大模型。
- [x] 创建 Phase 2G 设计文档：`docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2g-agent-credibility-design.md`。
- [x] 创建 Phase 2G 实施计划：`docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md`。
- [x] 创建 Phase 2G 测试计划：`docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2g-test-plan.md`。
- [x] 同步 Phase 2G 测试计划外部副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md`。

### 后端 Phase 2G

- [ ] 新增独立 Agent 输出 schema：JD 解析、简历解析、RAG query planner、缺口分析、简历建议、面试题、学习路径、Next Best Action、Integrity critic。
- [ ] 新增统一结构化 Agent 执行器：LLM 调用、一次 JSON 修复重试、Pydantic 校验、fallback 元数据。
- [ ] 为 `agent_runs` 增加 `execution_meta` 持久化和 API 响应契约，确保 Agent Trace 执行方式能从后端传到前端。
- [ ] `jd_parser` 从固定技能词精确匹配升级为岗位族 + 技能维度抽取，数据分析岗至少覆盖 SQL、Python、数据可视化、统计/A/B 测试等维度。
- [ ] `resume_parser` 支持数据分析技能证据抽取，并继续禁止新增简历事实。
- [ ] 新增 `rag_query_planner_agent`，为每个技能维度生成检索 query、岗位族过滤和知识类型。
- [ ] `rag_retriever` 增加岗位族过滤、文档类型过滤和相关性阈值；真实 DB 检索边界保留在 `analysis_service` 或显式注入 workflow；低相关结果降级为“知识库证据不足”。
- [ ] 新增数据分析种子知识库，覆盖 SQL、Python 数据处理、统计方法、A/B 测试、数据可视化、机器学习基础、业务分析、面试题型。
- [ ] `match_scorer` 优先消费结构化 `skill_dimensions`，最终数字评分仍保持确定性，不调用 LLM。
- [ ] 拆分当前单次 `generate_report_enhancement()`：简历建议、面试题、学习路径、Next Best Action 改为独立 Agent 产物。
- [ ] 明确 `IntegrityCriticOutput` 只能辅助解释风险，不能替代硬规则 `Integrity Guard` 或决定建议放行。
- [ ] Agent Trace 写入执行方式：`llm`、`rule`、`rag`、`deterministic`，并包含模型名、fallback、schema 校验和重试次数。

### 前端 Phase 2G

- [ ] Agent Trace 节点名通俗化：例如 `jd_parser` 显示为“解析岗位要求”，技术名保留在详情。
- [ ] Agent Trace 展示真实执行方式：LLM、本地规则、RAG、确定性规则。
- [ ] `frontend/src/api/agentRuns.ts` normalize 层消费后端 `execution_meta`，避免组件测试通过但真实 API 信息丢失。
- [ ] Agent Trace 展示 fallback、schema 校验、JSON 修复重试次数，不展示完整 JD、完整简历、完整 prompt 或 API key。
- [ ] 报告页知识库证据只展示相关文档；无相关文档时显示“知识库证据不足”。
- [ ] 报告页增加分组或折叠策略，避免 Phase 2G 增加更多维度和 trace 信息后继续纵向堆叠。
- [ ] 面试题和学习任务展示非模板化结构字段，避免所有题目/任务长得一样。

### Phase 2G 验证门

- [ ] 后端：`cd backend && pytest tests/test_agent_schemas.py tests/test_multi_agent_llm_flow.py tests/test_data_analysis_dimension_extraction.py tests/test_rag_relevance_filtering.py -q && pytest -q`。
- [ ] 前端：`cd frontend && npm test -- AgentTraceTimeline && npm test -- ReportView && npm test && npm run typecheck && npm run build`。
- [ ] Docker：`docker compose up --build`，使用数据分析师 JD/简历完成一次端到端分析，确认多维评分、RAG 相关性和 Agent Trace 执行方式。
- [ ] PII：运行 `gstack:cso` 或记录本地等价 OWASP + STRIDE 审计；重点检查 LLM prompt、Agent trace、日志、localStorage 不泄露完整 JD/简历/API key。
- [ ] 文档：`git diff --check`。

### Phase 2G 外延后事项（来自 UX 评估但不进入本阶段）

- [ ] 时间戳格式化：岗位、简历、报告列表显示为相对时间或本地时间格式。
- [ ] 版本名称重复：修复“v1 — 名称 — v1”一类重复拼接。
- [ ] 报告返回入口：报告页增加面包屑或明显返回工作台入口。

## Phase 2+ 延后

以下事项有产品价值，但当前不进入 Phase 2G，避免范围膨胀。

### 后端能力

- 文本输入端到端跑通后，再加 PDF/DOCX 简历解析。
- 任务式 API 稳定后，再引入后台 worker（Celery / RQ / Arq）。
- 本地 Markdown 简历导入。
- 简历导出。
- 知识库扩充更多岗位族（数据科学、安全、嵌入式、运维等；数据分析岗已进入 Phase 2G）。
- 面试回答评分闭环。
- 每周求职进展总结。
- 多模型路由 / 成本观测（基础 fallback 已在 Phase 2C 完成）。

### 前端能力

- 主题深度自定义（仅核心两套 + 切换由 Phase 1 完成；自定义色 / 字号 / 布局延后）。
- 国际化 i18n（Phase 1 仅中文）。
- 离线模式与 PWA。
- 富文本简历编辑器（Phase 1 用纯文本输入）。
- 报告 PDF 版式预览（基础打印/PDF HTML 已在 Phase 2F 完成）。
- 协作分享只读链接（前提是先确定分享是否触发账号边界，默认延后）。

### 架构与运维

- 真实账号系统（登录、注册、SSO）— `CLAUDE.md` 硬边界，禁止在 Phase 1 引入。
- 多用户多租户 — 同上。
- 生产级部署（K8s / 灰度 / 蓝绿） — Phase 2+。
- 监控仪表盘（Sentry / OpenTelemetry / Grafana）。
- CI/CD 全链路（lint / typecheck / test / build / deploy）。
- 容器镜像签名 / SBOM。

## 明确不做的范围（硬边界）

- 登录、注册和多用户账号管理。
- HR 候选人筛选和排序流程。
- 导师、就业老师或管理员看板。
- 支付、通知、日历或企业协作功能。
- 生产级岗位网站爬取。
- 把项目降级成一次性 Demo。

## 跨文件同步检查

每次变更范围或决策时，必须同时检查并更新：

- `CLAUDE.md`（如影响约束或边界）
- `AGENTS.md`（如影响约束或边界）
- `docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`
- `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md`
- `docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md`
- `C:\Users\qwer\.gstack\projects\Newproject\main-test-plan-2026-05-02-careerfit-agent.md`
- `docs/DESIGN.md`（如影响视觉系统或组件契约）
- 本文件

不同步即为违反 `CLAUDE.md` "实施文档实时更新" 节。

### Phase 4 决策审计（2026-05-03 用户审批通过）

| 决策 | 选择 | 类型 | 理由 | 影响 | 回滚条件 |
|---|---|---|---|---|---|
| D1 产品形态 | 13 路由工作台 + 工作台首屏「下一步」卡片 | Auto-decide（用户批准） | 与 CLAUDE.md 工作台优先一致 | T1 路由表 + T3 工作台视图 | 用户研究表明工作台导航过载 |
| D2 评分展示 | 评分卡 + 证据并列 | Auto-decide | Design 共识：先看分会损害可信度 | T4 报告视图 + DESIGN.md ScoringDimensionCard | 用户反馈"证据太多看不过来" |
| D3 Agent trace 密度 | 折叠摘要 + 展开看完整节点 | Auto-decide | 平衡可信度与认知负载 | T5 AgentTraceView + DESIGN.md AgentTraceTimeline | 用户主动请求默认展开 |
| D4 UI 库 | Reka UI（轻量 headless） | Auto-decide | 仅引入需要的组件，避免设计系统冲突 | T1 依赖清单 + T2 共享组件 | Reka UI 与 Vue 3 不兼容 |
| D5 图表库 | ECharts | Auto-decide | HistoryView 趋势图主力 | T5 HistoryView | bundle 体积 > 200KB gzip |
| D6 SQLAlchemy 异步/同步 | 同步 Phase 1 | Auto-decide | greenfield 测试更简单；T8 之前无流式/高并发需求 | T8 backend 骨架 + T9 service | Phase 1 出现需要异步流式响应的功能 |
| D7 Agent trace 持久化 | 原始快照 + 对外脱敏分离 | Auto-decide | trace schema 演进比响应需求快 | T11 持久化 + T11 脱敏 | 隐私合规要求不持久化原始 trace |
| D8 Evidence 偏移坐标 | raw + normalized 双坐标 | Auto-decide | 双坐标支持 UI 高亮 + 后端复算 | T9 Evidence schema | 性能基准显示双坐标存储成本 > 30% |
| D9 LangGraph 类型层级 | adapter-only | Auto-decide | 保留可替换性 | T10 AgentRunner 边界 + ADR 0001 | LangGraph 真接入后不再需要边界 |
| D10 Capability 版本化 | schema_version + 四态枚举 | Auto-decide | 未来 capability 翻转和新 agent 能力都需要 | T8 capability 契约 + T2 availability store | 改用纯客户端能力探测 |
| D11 测试 DB 策略 | 双轨：SQLite 单测 + Postgres 集成 | Auto-decide | 与 TODOS.md 已记录决策一致 | 整个测试矩阵 | SQLite/Postgres 行为差异不可调和 |
| D12 DESIGN.md 480px 修订时机 | 随 T1 脚手架同时修 | User Challenge（用户批准 A） | 早对齐五档断点避免 T3-T7 返工 | T1 commit 同时改 DESIGN.md 第 540 行 + 已知缺口 #3 | T1 阻塞超过 1 个 work session |
| C1 BackendNotReadyNotice 必填 props | 是，作为 T2 强制门 | User Challenge（用户批准 A） | 防止退化为空白 div | T2 共享组件契约 + 测试用例 | runtime 校验在 SSR 场景下不兼容 |
| C2 Integrity Guard 伪积极黑名单 | 是，纳入黑名单 | User Challenge（用户批准 A） | 伪积极对求职者更危险 | T10 Integrity Guard + 测试样例（5+5） | 用户反馈黑名单过严，正常乐观表达被拦截 |

### autoplan 通过门后行动清单

- [x] Phase 0/0.5/1/2/3/3.5/4 全部通过审查。
- [x] 修订 `docs/DESIGN.md` 第 540 行 + 已知缺口 #3（D12 决议：480px 断点已写入，与 T1 同步完成）。
- [x] 把 14 项决策同步到 `TODOS.md` "决策点" 节（"决策点"节 + "Phase 4 决策审计"节双重记录）。
- [x] 写 3 条 review-log（plan-ceo-review / plan-design-review / plan-eng-review，含双声标记）。
- [x] 建议下一步：T1–T13 全部完成，Phase 1 已交付。
- [x] 提示：T8–T11 的 PII 入口逻辑必须跑 `gstack:cso` OWASP + STRIDE 安全审计；当前 CLI 入口不可用，已记录并完成本地等价审计。
