# CareerFit Agent 测试计划

日期：2026-05-02
版本：v2（双门重写：前端 Phase 1.A + 后端 Phase 1.B）

## 适用约束与文件优先级

- **此文件不覆盖 `CLAUDE.md`**。如有冲突，以 `CLAUDE.md` 中的"Phase 1 验收门"、"实现约束"、"前端实现约束"、"隐私与安全约束"、"评分、RAG 与 Agent 可信度约束"为准。
- 本测试计划必须与 `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md` 中的任务清单（T1–T13）保持一致。
- 本仓库测试计划修改后，必须同步更新外部副本 `C:\Users\qwer\.gstack\projects\Newproject\main-test-plan-2026-05-02-careerfit-agent.md`。

## 测试门与执行顺序

| 门 | 关联计划任务 | 是否阻塞 Phase 1 |
|---|---|---|
| 前端 Phase 1.A 测试门 | T1–T7 | 是 |
| 后端 Phase 1.B 测试门 | T8–T11 | 是 |
| 全栈集成测试门 | T12–T13 | 是 |

执行顺序与计划顺序一致：先跑前端 Phase 1.A 测试门 → 再跑后端 Phase 1.B 测试门 → 最后跑全栈集成测试门。每个门都必须全绿才能继续下一门。

## 受影响页面和路由

按计划 T1 中 13 条 Vue Router 路由列出，每条路由标注是否需要后端能力，以及缺口时的占位行为。

| 路由 | 视图 | 后端依赖 | 后端缺口时行为 |
|---|---|---|---|
| `/` | WorkspaceView | `analyses.list` | `BackendNotReadyNotice` |
| `/jobs` | JobsView | `jobs.list` | `BackendNotReadyNotice` |
| `/jobs/:id` | JobDetailView | `jobs.detail` | `BackendNotReadyNotice` |
| `/resumes` | ResumesView | `resumes.list` | `BackendNotReadyNotice` |
| `/resumes/:id` | ResumeDetailView | `resumes.detail` | `BackendNotReadyNotice` |
| `/analyses/new` | AnalysisRunView | `analyses.create` | 表单可填，提交按钮置 disabled + 提示 |
| `/reports/:taskId` | ReportView | `reports.detail` | `BackendNotReadyNotice` |
| `/history` | HistoryView | `analyses.history` | `BackendNotReadyNotice` |
| `/diff` | VersionDiffView | `resumes.compare` | `BackendNotReadyNotice` |
| `/learning` | LearningTasksView | `learning.list`、`learning.update` | `BackendNotReadyNotice` |
| `/trace/:taskId` | AgentTraceView | `agent_runs.detail` | `BackendNotReadyNotice` |
| `/settings` | SettingsView | 无 | 始终可用（仅本地偏好） |
| `*` | NotFoundView | 无 | 始终可用 |

## 前端 Phase 1.A 测试门

### 路由与导航

- 13 条路由都能渲染对应视图，不出现空白或控制台错误。
- `*` 路由命中 `NotFoundView`，并提供返回工作台的按钮。
- 顶部导航与移动端 `MobileNav` 在桌面/平板/移动端三套断点都能切换且高亮当前路由。
- 路由切换时无大段闪烁；过渡动效遵守 `docs/DESIGN.md` 定义。

### 共享组件 TDD（T2 必跑）

- `AppButton`：默认、hover、focus、active、disabled、loading、error 7 态各有快照测试或断言。
- `RiskPill`：
  - `level=high` 时必须同时渲染 `aria-label="高风险"` 和颜色样式；只渲染颜色不渲染文字时测试必须失败。
  - `level=medium`、`level=low` 同上分别校验 `需关注` 与 `通过`。
  - 风险等级映射来自 `docs/DESIGN.md` 中的 `risk-pill-*.requiresLabel`。
- `BackendNotReadyNotice`：
  - 接受 `feature: string` 和 `waitingFor: string` props 必填。
  - 渲染为 inline banner 或灰底卡片，含明确文案"功能尚未上线 / 等待后端 X 完成"。
  - 测试断言文案中必须出现"功能尚未上线"或"等待后端"中文关键词。
- `NextBestActionCallout`：
  - 接受 `action: { title, rationale, ctaLabel?, ctaTo? }`。
  - 在工作台首屏与报告头部显眼位渲染（位置由调用方控制，但组件自身要支持）。
  - 测试断言渲染 `action.title` 与 `action.rationale`。
- `IntegrityGuardBanner`：
  - 当 `flags.length > 0` 时显示风险标签 + 文字描述 + 跳转到证据的链接；不得只用红色提示。
- `EvidenceCard`、`ScoringDimensionCard`、`SuggestionCard`、`AgentTraceTimeline`、`AgentTraceRow`、`ScoringOverviewCard`：每个组件至少 1 个渲染测试 + 1 个空数据/异常数据测试。

### `availability` 状态机

- `frontend-only` 模式：跳过 `/api/capabilities` 探测，所有 capability 标记为 `unavailable`，所有依赖后端的视图渲染 `BackendNotReadyNotice`。
- `fullstack` 模式：探测成功时按响应填充；任意 capability 标记为 `unavailable` 时该视图必须立即切换到 `BackendNotReadyNotice`。
- 探测失败（网络错误 / 5xx / 超时）：所有 capability fallback 为 `unavailable`，并在工作台顶部显示一次性提示。
- 状态恢复：能力从 `unavailable → ready` 时（用户手动刷新或定时重探），视图必须从占位切换到真实数据。

### 工作台、Jobs、Resumes 视图（T3）

- 工作台空状态：无报告时渲染引导卡片（"先创建目标岗位"）。
- 工作台已有数据状态：渲染最近报告、`NextBestActionCallout`。
- 工作台后端不可用：整页 `BackendNotReadyNotice`，`feature="工作台"`，`waitingFor="分析任务接口"`。
- Jobs 列表加载、错误、空、有数据 4 态分别可见。
- Resumes 列表同上。
- Jobs 详情、Resumes 详情：缺口时渲染 `BackendNotReadyNotice`，禁止 mock 列表。

### 分析提交 + 报告视图（T4）

- 分析提交表单：岗位选择、简历选择、提交按钮 4 态（默认/loading/disabled/error）。
- 后端 `analyses.create` 不可用：表单可填、提交按钮 disabled + tooltip 提示。
- 报告视图：
  - 头部固定显眼位渲染 `NextBestActionCallout`。
  - `ScoringOverviewCard` 显示总分（来自后端确定性评分，不允许前端二次计算）。
  - 每个 `ScoringDimensionCard` 必须能展开到 `EvidenceCard`（关联 JD 证据 + 简历证据）。
  - 缺少证据的评分项渲染弱证据提示 + 风险标签（色 + 文字双通道）。
  - `IntegrityGuardBanner`：有风险时显示标签 + 文字。
  - `AgentTraceTimeline`：节点状态成功/失败/跳过/重试 4 态。
- 报告未就绪 / 任务失败：分别渲染加载与失败状态，不渲染半截数据。

### 周边视图（T5）

- HistoryView、VersionDiffView、LearningTasksView、AgentTraceView 在后端未上线时全部以 `BackendNotReadyNotice` 占位。
- 路由可达、视图骨架渲染（标题、说明文字、占位）。
- 禁止任何 mock 数据；测试中如发现硬编码示例数据必须失败。

### 本地偏好与 PII 白名单（T6）

- `useLocalStorageRef`：
  - 命名空间 `careerfit:pref:*` 限定。
  - 白名单字段 `theme`、`density`、`recentJobIds`、`recentResumeIds`、`lastReportTaskId` 等可读写。
  - 黑名单字段（`raw_jd`、`raw_resume`、`agent_trace_raw`、长度大于 1KB 的任意字符串、被识别为 PII 的对象）必须被拒收，并写入 `console.warn`。
  - 测试覆盖：写入合规字段成功；写入 `raw_jd` 抛错或被忽略；写入 1.1KB 字符串被拒。
- localStorage 不可用（隐身模式 / 浏览器拒绝）：必须回落到内存 store，不抛未捕获异常；测试用 jsdom 的禁用模拟。
- 数据被外部清空（`localStorage.clear()`）：下次刷新页面时视图能优雅恢复（用默认值），不依赖本地数据真实性。
- `SettingsView`：能切换主题、密度等偏好；切换后立即生效，刷新后保持。

### UX 抛光与无障碍

- 完整响应式断点测试：1440 / 1280 / 1024 / 768 / 480 五档；工作台、报告、Jobs、Resumes、Settings、HistoryView 都必须可用，移动端不只"报告可读"。
- 键盘可达：所有按钮、输入框、模态、Trace 行可用 Tab / Enter / Esc 操作；Tab 顺序符合视觉顺序。
- ARIA 标签：所有图标按钮必须有 `aria-label`；`RiskPill` 必须有 `aria-label` 表达风险等级（不依赖颜色）。
- WCAG AA：用 `axe-core` 或等价工具校验工作台、报告、Jobs、Settings 四个核心视图，无致命/严重违规。
- 关键交互动效：状态切换、模态打开/关闭、Trace 展开必须有 200–300ms 过渡，不允许硬切换。

### Docker（T7）

- `docker compose -f docker-compose.frontend-only.yml up --build`：
  - 仅启动 `frontend` 服务（基于多阶段 nginx 镜像）。
  - 容器健康检查通过，浏览器可访问。
  - 进入工作台时 `availability` 状态全为 `unavailable`，所有视图渲染 `BackendNotReadyNotice`。

## 后端 Phase 1.B 测试门

### API 覆盖

| API | 必测场景 |
|---|---|
| `GET /api/capabilities` | 全部 ready、部分 ready、错误时 schema 仍合法 |
| `POST /api/jobs` | 有效 JD、空 JD、格式不完整 JD、解析失败 |
| `GET /api/jobs` | 空列表、有数据列表 |
| `GET /api/jobs/{id}` | 存在、不存在 |
| `POST /api/resumes` | 有效文本简历、空简历、低置信度解析 |
| `GET /api/resumes/compare` | 新增段落、删除段落、修改段落 |
| `POST /api/analysis` | 有效岗位 + 简历、岗位不存在、简历不存在 |
| `GET /api/analysis/{task_id}` | pending、running、success、failed |
| `GET /api/reports/{task_id}` | 完整报告、弱证据报告、不存在 |
| `GET /api/agent-runs/{task_id}` | 成功节点、失败节点、脱敏摘要 |
| `PATCH /api/learning/tasks/{id}` | `not_started -> doing`、`doing -> done`、非法状态流转 |
| `GET /api/knowledge/search` | 命中预期文档、无命中、非法查询 |

`/api/capabilities` 响应 schema（最小契约）：

```json
{
  "schema_version": "1",
  "capabilities": {
    "jobs.list": "ready" | "pending",
    "jobs.detail": "ready" | "pending",
    "resumes.list": "ready" | "pending",
    "resumes.detail": "ready" | "pending",
    "resumes.compare": "ready" | "pending",
    "analyses.create": "ready" | "pending",
    "analyses.list": "ready" | "pending",
    "analyses.history": "ready" | "pending",
    "reports.detail": "ready" | "pending",
    "agent_runs.detail": "ready" | "pending",
    "learning.list": "ready" | "pending",
    "learning.update": "ready" | "pending"
  }
}
```

测试断言：

- 缺失字段必须 fallback 为 `pending`，前端必须把它当作 `unavailable` 渲染。
- 任何 capability 设为 `pending` 时，前端集成测试必须验证对应视图切换到 `BackendNotReadyNotice`。

### 核心单元测试

- 评分公式把所有维度限制在 0-100。
- 真实性风险扣分不能让最终分数变成负数。
- 能力层级映射返回预期数值。
- 证据链校验会拒绝没有 JD 证据的评分项。
- 证据链校验会拒绝没有简历证据的评分项。
- Integrity Guard 会阻止无证据指标。
- Integrity Guard 会阻止无证据领导力描述。
- Integrity Guard 允许安全改写。
- 简历版本比较能识别新增、删除和修改的 bullet。
- 评分原始因子持久化到 `analysis_reports.raw_factors`，便于复现。

### LangGraph 与 Agent 测试

- JD Parser Agent 返回符合 schema 的输出。
- Resume Parser Agent 返回符合 schema 的输出。
- RAG Retriever Agent 返回按类型分组的文档。
- Match Scoring Agent 不使用 LLM 生成最终数字分数。
- Gap Analysis Agent 输出 `missing_skill`、`weak_evidence`、`expression_gap`。
- Integrity Guard Agent 在 Resume Optimizer 最终输出前运行。
- Report Composer Agent 为每个评分项提供证据引用。
- 工作流为每个节点记录 `agent_runs`。
- 节点重试后仍失败时，工作流把任务标记为 failed。
- LLM 返回非法 JSON 时，最多允许一次修复重试；超过则标记节点失败，不得吞错。

### Agent Trace 脱敏

- 服务端原始快照与对外 API 响应分离。
- `GET /api/agent-runs/{task_id}` 返回的内容必须经过脱敏函数处理。
- 脱敏单元测试：原文 JD/简历不出现在响应；评分维度名、节点名、状态保留。
- 后续若返回 trace 摘要，必须含人类可读的"输入摘要 / 输出摘要"，且长度受限。

### RAG 评估

种子文档至少覆盖：

- 大模型应用开发工程师。
- 后端开发工程师。
- 前端/全栈开发工程师。

必须检查：

- 查询 `LangGraph Agent 编排` 能召回 LangGraph 技能标准。
- 查询 `pgvector 索引` 能召回向量数据库标准。
- 查询 `Vue3 项目经验` 能召回前端/全栈标准。
- 查询没有匹配技能时，返回空结果或低置信度结果，而不是编造来源。

### LLM 评估

至少使用：

- 5 份样例 JD。
- 5 份样例简历。
- 5 条不安全简历优化样例。

评估标准：

- Parser 能抽取必备技能，并达到可接受召回率。
- Parser 保留证据片段。
- Integrity Guard 阻止编造事实。
- Report Composer 不生成无证据结论。
- 面试题在可行时引用真实简历项目。

### 数据库与持久化

- `analysis_tasks`、`analysis_reports`、`agent_runs` 三表 JSON 字段必须包含 `schema_version`。
- SQLite 与 PostgreSQL 行为差异：JSON 查询、UUID、时间戳精度的差异必须在集成测试中显式覆盖；如有不一致，按 `CLAUDE.md` 在计划中记录。

## 全栈集成测试门

### `frontend-only` Docker 冒烟（T7）

```text
docker compose -f docker-compose.frontend-only.yml up --build
```

- 浏览器打开前端，所有视图能渲染骨架。
- 由于无后端服务，所有 capability 为 `unavailable`，对应视图渲染 `BackendNotReadyNotice`。
- 控制台无未捕获错误。

### `fullstack` Docker 冒烟（T12）

```text
docker compose up --build
```

- PostgreSQL 启动并启用 pgvector 扩展。
- 后端健康检查通过。
- 前端能打开。
- 后端能连接数据库。
- 初始迁移执行成功。
- 种子知识库导入成功。
- 前端通过 `/api/capabilities` 拉到全部 `ready`，所有依赖后端的视图切换到真实数据状态。

### 集成主路径（T13）

执行一次端到端：

1. 创建目标岗位。
2. 创建简历版本。
3. 执行分析。
4. 查看报告。
5. 确认每个评分项都有证据。
6. 查看真实性风险。
7. 标记学习任务完成。
8. 创建下一版简历。
9. 再次分析。
10. 查看分数趋势。

每一步都必须在浏览器 UI 中真实可见，不允许仅命令行完成；UI 状态机覆盖：加载 → 成功 → 错误 → 部分数据。

## 验证命令基线

按 `CLAUDE.md` 的验证命令基线执行：

- 后端：`cd backend && pytest -q`
- 前端：`cd frontend && npm test`
- Frontend-only Docker：`docker compose -f docker-compose.frontend-only.yml up --build`
- Fullstack Docker：`docker compose up --build`
- 周期性健康：`gstack:health`
- PII 入口变更：`gstack:cso`
- 计划/测试计划变更后：`gstack:qa-only`

如某命令无法运行，必须在执行说明中写清原因，不能把未验证内容说成已通过。

## 关键路径回归（每个里程碑跑一次）

1. 创建目标岗位（前端 → 后端）。
2. 创建简历版本。
3. 执行分析。
4. 查看报告（含证据展开）。
5. 检查 `Next Best Action`、`Integrity Guard` 提示。
6. 查看 Agent Trace（脱敏后摘要）。
7. 标记学习任务完成。
8. 创建下一版简历。
9. 再次分析。
10. 查看分数趋势。
11. 切换到 `frontend-only` 模式，验证所有视图切换到 `BackendNotReadyNotice`。
12. 切换回 `fullstack` 模式，验证视图自动恢复真实数据。
