# CareerFit Agent Phase 1 实施计划

> **给智能执行代理的要求：** 实施本计划时必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`。执行时必须逐项更新 checklist，把完成的步骤从 `- [ ]` 改成 `- [x]`。

**目标：** Phase 1 由两条独立验收门组成，全部达成才算完成：

- **前端 Phase 1.A 验收门**：完整功能网站。所有规划页面（工作台、报告、岗位/简历管理、Agent trace、历史趋势、版本对比、学习任务、设置）存在且可路由；每页支持空/加载/错误/部分数据状态；UX 抛光（响应式、键盘可达、ARIA、动效）达标；后端缺口走"诚实告知"组件提示用户，**禁止 mock 数据**；本地偏好/会话用 localStorage / IndexedDB；不引入登录与多租户。
- **后端 Phase 1.B 验收门**：可信主路径。

```text
创建目标岗位
  -> 创建简历版本
  -> 执行分析
  -> 确定性评分
  -> 生成证据链报告
  -> 运行 Integrity Guard
  -> 展示 Agent 运行轨迹
  -> 给出 Next Best Action
```

详细判定条件见 `CLAUDE.md` "Phase 1 验收门" 节。

**实施顺序：** 先前端 Phase 1.A 全部完成，再启动后端 Phase 1.B；最后做前后端联调，把"诚实告知"占位逐步替换为真实数据。

**架构：**

- 前端：Vue3 + Vite + TypeScript，Pinia 状态管理，Vue Router 路由，Vitest + Vue Test Utils 测试。所有视觉 token 来自 `docs/DESIGN.md`，组件层严格遵守 risk 双通道、Next Best Action 显眼位、Agent Trace 脱敏 等约束。前端可在没有任何后端时独立运行，所有未到位的后端功能用 `BackendNotReadyNotice` 组件占位。
- 后端：FastAPI、SQLAlchemy、Pydantic、PostgreSQL/pgvector、LangGraph-compatible workflow boundary。LLM 调用封装在可替换 Agent 节点接口后面，并提供规则化本地 fallback，保证开发环境没有付费模型也能跑通核心流程。

**技术栈：** FastAPI、Pydantic、SQLAlchemy、PostgreSQL、pgvector、LangGraph、Vue3、TypeScript、Vite、Vue Router、Pinia、VueUse（推荐）、Vitest、Vue Test Utils、Playwright（E2E，可选）、Docker Compose、pytest。

---

## 范围

本计划只实现 Phase 1。明确不做：登录、多租户、HR 流程、导师看板、PDF/DOCX 解析、完整面试会话、生产级后台 worker。

前端 Phase 1.A 与后端 Phase 1.B 是两条独立验收门：前端可以在没有任何后端的情况下完成验收并独立部署一份"功能未上线提示"网站；后端只覆盖可信主路径，不追求功能铺满。

视觉与组件契约：见 `docs/DESIGN.md`，前端实现必须严格按其 token 与组件语义。

## 文件结构

```text
backend/
  app/
    main.py
    api/routes/jobs.py
    api/routes/resumes.py
    api/routes/analysis.py
    api/routes/reports.py
    api/routes/agent_runs.py
    api/routes/knowledge.py
    agents/graph.py
    agents/nodes.py
    agents/state.py
    core/config.py
    core/logging.py
    db/base.py
    db/models.py
    db/session.py
    rag/seed_data.py
    rag/retriever.py
    schemas/jobs.py
    schemas/resumes.py
    schemas/analysis.py
    schemas/reports.py
    schemas/knowledge.py
    scoring/evidence.py
    scoring/rules.py
    scoring/rubric.py
    services/analysis_service.py
    services/job_service.py
    services/resume_service.py
    services/knowledge_service.py
  tests/
    test_jobs_api.py
    test_resumes_api.py
    test_scoring.py
    test_integrity_guard.py
    test_analysis_flow.py
frontend/
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main.ts
    App.vue
    router/index.ts
    api/client.ts
    api/jobs.ts
    api/resumes.ts
    api/analysis.ts
    api/reports.ts
    api/agentRuns.ts
    api/learning.ts
    api/availability.ts            # 后端能力探测（哪些 API 已上线）
    stores/jobs.ts
    stores/resumes.ts
    stores/analyses.ts
    stores/preferences.ts
    stores/availability.ts
    composables/useBackendStatus.ts
    composables/useLocalStorageRef.ts
    composables/useResponsive.ts
    composables/useA11y.ts
    components/layout/AppShell.vue
    components/layout/SideNav.vue
    components/layout/StatusBar.vue
    components/layout/MobileNav.vue
    components/feedback/EmptyState.vue
    components/feedback/LoadingCard.vue
    components/feedback/ErrorBanner.vue
    components/feedback/BackendNotReadyNotice.vue
    components/feedback/SkeletonBlock.vue
    components/risk/RiskPill.vue
    components/risk/IntegrityGuardBanner.vue
    components/workbench/NextBestActionCallout.vue
    components/workbench/JobSelector.vue
    components/workbench/ResumeSelector.vue
    components/workbench/AnalysisLauncher.vue
    components/report/ScoringOverviewCard.vue
    components/report/ScoringDimensionCard.vue
    components/report/EvidenceCard.vue
    components/report/SuggestionCard.vue
    components/report/AgentTraceTimeline.vue
    components/report/AgentTraceRow.vue
    components/common/StatusBadge.vue
    components/common/Modal.vue
    components/common/AppButton.vue
    components/common/AppInput.vue
    components/common/AppTextarea.vue
    views/WorkspaceView.vue
    views/JobsView.vue
    views/JobDetailView.vue
    views/ResumesView.vue
    views/ResumeDetailView.vue
    views/AnalysisRunView.vue
    views/ReportView.vue
    views/HistoryView.vue
    views/VersionDiffView.vue
    views/LearningTasksView.vue
    views/AgentTraceView.vue
    views/SettingsView.vue
    views/NotFoundView.vue
    styles/tokens.css
    styles/base.css
    styles/a11y.css
  tests/
    components/RiskPill.test.ts
    components/BackendNotReadyNotice.test.ts
    components/NextBestActionCallout.test.ts
    components/AgentTraceTimeline.test.ts
    views/WorkspaceView.test.ts
    views/ReportView.test.ts
    views/SettingsView.test.ts
    composables/useLocalStorageRef.test.ts
    routing.test.ts
docker-compose.yml
docker-compose.frontend-only.yml
```

分层职责：

- API routes 只处理 HTTP 请求和响应。
- Services 编排数据库、评分和 workflow。
- Agents 负责结构化中间结果和 trace。
- Scoring 只放确定性评分逻辑。
- RAG 负责种子知识、chunk、embedding 和 retrieval。
- Frontend views 组合可复用组件；组件层严格不内嵌业务请求，业务请求走 stores 与 api 模块。
- Frontend stores 的接口在后端未到位时返回 `unavailable` 状态供组件渲染 `BackendNotReadyNotice`，**不返回 mock 数据**。

---

# 第一部分：前端 Phase 1.A

## Task 1：前端项目骨架与路由

**文件：**

- 创建 `frontend/package.json`
- 创建 `frontend/index.html`
- 创建 `frontend/tsconfig.json`
- 创建 `frontend/vite.config.ts`
- 创建 `frontend/src/main.ts`
- 创建 `frontend/src/App.vue`
- 创建 `frontend/src/router/index.ts`
- 创建 `frontend/src/views/NotFoundView.vue`
- 创建 `frontend/tests/routing.test.ts`

- [ ] **Step 1：创建前端依赖配置**

`package.json` 必须包含：Vue3、Vite、`@vitejs/plugin-vue`、TypeScript、Vue Router、Pinia、VueUse、Vitest、Vue Test Utils、jsdom、`@vue/test-utils`、`@types/node`、`vite-tsconfig-paths`。脚本至少包含：

```text
npm run dev
npm run build
npm run preview
npm test
npm run typecheck
```

不在本步骤选定 UI 组件库；后续按 `docs/DESIGN.md` 自行实现原子组件。

- [ ] **Step 2：创建 TypeScript 与 Vite 配置**

`tsconfig.json` 开启严格模式（`strict: true`、`noUncheckedIndexedAccess: true`），路径别名 `@ -> src`。
`vite.config.ts` 注册 `@vitejs/plugin-vue`，Vitest 环境为 `jsdom`，`coverage` 启用 v8 reporter。

- [ ] **Step 3：创建路由表**

`router/index.ts` 注册以下路由：

```text
/              -> WorkspaceView
/jobs          -> JobsView
/jobs/:id      -> JobDetailView
/resumes       -> ResumesView
/resumes/:id   -> ResumeDetailView
/analyses/new  -> AnalysisRunView
/reports/:taskId    -> ReportView
/history       -> HistoryView
/diff          -> VersionDiffView
/learning      -> LearningTasksView
/trace/:taskId -> AgentTraceView
/settings      -> SettingsView
/:pathMatch(.*)*  -> NotFoundView
```

每个 view 先用占位组件（写一行标题即可），保证路由可达；具体内容在后续 Task 填充。

- [ ] **Step 4：先写失败的路由 smoke 测试**

`tests/routing.test.ts` 断言：

- 上述 13 条路由都能解析到对应 view（不报路由 not found）。
- `/` 命中 `WorkspaceView`。
- 未知路径命中 `NotFoundView`。

- [ ] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm install
npm test
```

- [ ] **Step 6：实现路由与 App shell**

`App.vue` 使用 `<RouterView>`，外层包一个最小 `AppShell`（暂不含侧栏）。`main.ts` 装配 `createApp` + `createPinia` + `router`。

- [ ] **Step 7：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 8：提交**

```powershell
git add frontend
git commit -m "chore: scaffold frontend with router and skeleton views"
```

## Task 2：设计 token 与共享反馈 / 风险 / 行动组件

**文件：**

- 创建 `frontend/src/styles/tokens.css`
- 创建 `frontend/src/styles/base.css`
- 创建 `frontend/src/styles/a11y.css`
- 创建 `frontend/src/components/common/AppButton.vue`
- 创建 `frontend/src/components/common/AppInput.vue`
- 创建 `frontend/src/components/common/AppTextarea.vue`
- 创建 `frontend/src/components/common/StatusBadge.vue`
- 创建 `frontend/src/components/common/Modal.vue`
- 创建 `frontend/src/components/feedback/EmptyState.vue`
- 创建 `frontend/src/components/feedback/LoadingCard.vue`
- 创建 `frontend/src/components/feedback/ErrorBanner.vue`
- 创建 `frontend/src/components/feedback/BackendNotReadyNotice.vue`
- 创建 `frontend/src/components/feedback/SkeletonBlock.vue`
- 创建 `frontend/src/components/risk/RiskPill.vue`
- 创建 `frontend/src/components/risk/IntegrityGuardBanner.vue`
- 创建 `frontend/src/components/workbench/NextBestActionCallout.vue`
- 创建 `frontend/tests/components/RiskPill.test.ts`
- 创建 `frontend/tests/components/BackendNotReadyNotice.test.ts`
- 创建 `frontend/tests/components/NextBestActionCallout.test.ts`

- [ ] **Step 1：把 docs/DESIGN.md 的 token 落到 tokens.css**

把 `docs/DESIGN.md` frontmatter 的 colors / typography / rounded / spacing 节翻译成 CSS 自定义属性，例如：

```css
:root {
  --color-canvas: #010102;
  --color-primary: #5e6ad2;
  --color-risk-high: #e5484d;
  --color-risk-high-bg: #3a1418;
  ...
  --rounded-md: 8px;
  --rounded-lg: 12px;
  ...
}
```

`base.css` 重置 + 默认字体（Inter + 系统中文降级栈）。`a11y.css` 提供 focus-visible 描边、`prefers-reduced-motion` 适配、对比度强化样式。

- [ ] **Step 2：先写失败的 RiskPill 测试**

`RiskPill.test.ts` 断言：

- props `level: "high" | "medium" | "low"` 控制底色与文字色。
- 必须渲染 `aria-label` 与可见文字（"高风险" / "需关注" / "通过"）；**只有颜色没有文字会失败测试**。
- 文字 fallback：未传入 `label` 时使用约定中文标签。

- [ ] **Step 3：先写失败的 BackendNotReadyNotice 测试**

`BackendNotReadyNotice.test.ts` 断言：

- 必传 props `feature`（功能名）、`waitingFor`（依赖的后端能力）。
- 渲染默认文案 "{feature}尚未上线，等待后端 {waitingFor}"。
- 不允许渲染任何 mock 数据样本（断言：组件 render 输出中不出现"示例""sample""demo"等字样，以及任何看似真实的数字/分数）。
- 必须含 `role="status"` 或 `role="alert"` 之一。

- [ ] **Step 4：先写失败的 NextBestActionCallout 测试**

`NextBestActionCallout.test.ts` 断言：

- props `state: "ready" | "blocked" | "empty"`。
- `ready`：渲染 lavender 左色条 + headline 文案 + 主按钮。
- `blocked`：按钮 disabled，渲染等待原因文案。
- `empty`：渲染 ink-subtle "当前没有推荐行动" 文案，无按钮。
- headline 文案超过 24 字符必须被截断或换行处理，不得溢出。

- [ ] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [ ] **Step 6：实现共享原子组件**

按 `docs/DESIGN.md` 组件契约实现 `AppButton`/`AppInput`/`AppTextarea`/`StatusBadge`/`Modal`，全部状态齐全（默认/hover/focus/active/disabled/loading/error）。

- [ ] **Step 7：实现反馈与风险组件**

按测试断言实现 `EmptyState`/`LoadingCard`/`ErrorBanner`/`BackendNotReadyNotice`/`SkeletonBlock`/`RiskPill`/`IntegrityGuardBanner`/`NextBestActionCallout`。

- [ ] **Step 8：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 9：提交**

```powershell
git add frontend/src/styles frontend/src/components frontend/tests/components
git commit -m "feat(frontend): add design tokens and shared components"
```

## Task 3：工作台、岗位管理、简历管理（含诚实告知）

**文件：**

- 创建 `frontend/src/api/client.ts`
- 创建 `frontend/src/api/availability.ts`
- 创建 `frontend/src/api/jobs.ts`
- 创建 `frontend/src/api/resumes.ts`
- 创建 `frontend/src/stores/availability.ts`
- 创建 `frontend/src/stores/jobs.ts`
- 创建 `frontend/src/stores/resumes.ts`
- 创建 `frontend/src/composables/useBackendStatus.ts`
- 创建 `frontend/src/components/layout/AppShell.vue`
- 创建 `frontend/src/components/layout/SideNav.vue`
- 创建 `frontend/src/components/layout/StatusBar.vue`
- 创建 `frontend/src/components/workbench/JobSelector.vue`
- 创建 `frontend/src/components/workbench/ResumeSelector.vue`
- 创建 `frontend/src/components/workbench/AnalysisLauncher.vue`
- 实现 `frontend/src/views/WorkspaceView.vue`
- 实现 `frontend/src/views/JobsView.vue`
- 实现 `frontend/src/views/JobDetailView.vue`
- 实现 `frontend/src/views/ResumesView.vue`
- 实现 `frontend/src/views/ResumeDetailView.vue`
- 创建 `frontend/tests/views/WorkspaceView.test.ts`

- [ ] **Step 1：实现 API client 与 availability 探测**

`client.ts` 实现 `requestJson<T>()`，对 404/501/网络错误统一返回 `unavailable` 标志而不是抛错，让 stores 决定渲染 `BackendNotReadyNotice` 还是 `ErrorBanner`。
`availability.ts` 提供 `fetchBackendCapabilities()`，调用后端 `/api/capabilities`（后端未实现时返回 `unavailable`，前端按"全部能力未就绪"处理）。

- [ ] **Step 2：实现 stores**

`stores/availability.ts`：Pinia store，记录每个能力（jobs / resumes / analysis / reports / agentRuns / learning）的状态：`unknown | ready | unavailable`。
`stores/jobs.ts` 与 `stores/resumes.ts`：对应的 CRUD 调用与缓存；后端 `unavailable` 时 store 不写入任何 mock 数据，组件层自行渲染 `BackendNotReadyNotice`。

- [ ] **Step 3：实现 layout 组件**

`AppShell.vue`：左侧 `SideNav`、底部 `StatusBar`、主内容 `<RouterView>` 区。
`SideNav.vue`：列出 工作台 / 岗位 / 简历 / 历史 / 对比 / 学习 / 设置 7 个入口，未就绪能力以 ink-subtle 文字 + 锁形图标显示，但**仍可点击进入**对应页面查看 `BackendNotReadyNotice`。
`StatusBar.vue`：底部一行展示当前后端连通性（"已连接 / 部分未上线 / 后端未连接"）+ 当前会话脱敏注记。

- [ ] **Step 4：先写失败的 WorkspaceView 测试**

`tests/views/WorkspaceView.test.ts` 断言：

- 默认渲染 `NextBestActionCallout`（state=`empty` 时渲染"当前没有推荐行动"）。
- 后端 `unavailable` 时，岗位选择器与简历选择器各自显示 `BackendNotReadyNotice`，文案分别提到 "等待后端 jobs API" 与 "等待后端 resumes API"。
- 后端 `ready` 但列表为空时显示 `EmptyState` + "新建岗位 / 新建简历" 按钮。
- 视图根元素带有 `role="main"` 与可见标题"个人求职成长工作台"。

- [ ] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [ ] **Step 6：实现工作台首屏**

`WorkspaceView.vue`：顶部 `NextBestActionCallout`，下方两栏分别为 `JobSelector` 与 `ResumeSelector`，再下方 `AnalysisLauncher`。每个组件按 store 状态渲染 `BackendNotReadyNotice` / `LoadingCard` / `EmptyState` / 真实数据 四态之一。

- [ ] **Step 7：实现岗位与简历管理**

`JobsView.vue`：列表 + "新建岗位" 按钮 + 表单 Modal；后端未就绪时整个表单 disabled 并显示 `BackendNotReadyNotice`。
`JobDetailView.vue`：详情 + 解析摘要 + 相关分析任务列表；后端未就绪时显示 notice。
`ResumesView.vue` + `ResumeDetailView.vue`：同上结构。

- [ ] **Step 8：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 9：提交**

```powershell
git add frontend
git commit -m "feat(frontend): add workspace, jobs and resumes management views"
```

## Task 4：分析执行视图与报告页（核心信任面）

**文件：**

- 创建 `frontend/src/api/analysis.ts`
- 创建 `frontend/src/api/reports.ts`
- 创建 `frontend/src/api/agentRuns.ts`
- 创建 `frontend/src/stores/analyses.ts`
- 创建 `frontend/src/components/report/ScoringOverviewCard.vue`
- 创建 `frontend/src/components/report/ScoringDimensionCard.vue`
- 创建 `frontend/src/components/report/EvidenceCard.vue`
- 创建 `frontend/src/components/report/SuggestionCard.vue`
- 创建 `frontend/src/components/report/AgentTraceTimeline.vue`
- 创建 `frontend/src/components/report/AgentTraceRow.vue`
- 实现 `frontend/src/views/AnalysisRunView.vue`
- 实现 `frontend/src/views/ReportView.vue`
- 创建 `frontend/tests/views/ReportView.test.ts`
- 创建 `frontend/tests/components/AgentTraceTimeline.test.ts`

- [ ] **Step 1：先写失败的 AgentTraceTimeline 测试**

`AgentTraceTimeline.test.ts` 断言：

- 节点输入/输出展示区只渲染 `summary`、`length`、`field_names` 等脱敏字段；如果 props 中包含 `raw_jd` 或 `raw_resume`，组件抛出 dev-only 警告并**不渲染原文**。
- 节点状态 `running / success / failed` 分别对应 info-trace / risk-low / risk-high 配色 + 文字标签。
- 长列表支持折叠（768 px 以下默认折叠）。

- [ ] **Step 2：先写失败的 ReportView 测试**

`ReportView.test.ts` 断言：

- `/reports/:taskId` 路由可达；`taskId` 非法时显示 `ErrorBanner`。
- 后端 reports API `unavailable` 时，整个报告区显示 `BackendNotReadyNotice`，文案为 "评分报告功能尚未上线，等待后端 analysis pipeline 完成"。
- 后端 ready 但任务尚未完成时显示 `LoadingCard` + "分析中..." 文案。
- 后端 ready 且数据返回时，顶部固定 `NextBestActionCallout`、其下 `ScoringOverviewCard`、再下方维度卡列表、再下方简历建议卡列表、底部 `AgentTraceTimeline`。
- 简历建议被 Integrity Guard 拦截时，列表上方插入 `IntegrityGuardBanner`，被拦截卡片置灰并带 `RiskPill level="high" label="高风险"`。

- [ ] **Step 3：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [ ] **Step 4：实现报告组件**

按 `docs/DESIGN.md` 组件契约实现 `ScoringOverviewCard`/`ScoringDimensionCard`/`EvidenceCard`/`SuggestionCard`/`AgentTraceRow`/`AgentTraceTimeline`。证据卡的 JD 与简历原文展示长度上限 200 字符，超出折叠。

- [ ] **Step 5：实现分析执行视图与报告视图**

`AnalysisRunView.vue`：选岗位 + 选简历 + 启动分析；后端未就绪时按钮 disabled + notice。
`ReportView.vue`：组合上述组件，按 store 状态渲染 4 态。

- [ ] **Step 6：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 7：提交**

```powershell
git add frontend
git commit -m "feat(frontend): add analysis run view and report view"
```

## Task 5：周边页面（历史 / 对比 / 学习 / Trace 全量）

**文件：**

- 创建 `frontend/src/api/learning.ts`
- 实现 `frontend/src/views/HistoryView.vue`
- 实现 `frontend/src/views/VersionDiffView.vue`
- 实现 `frontend/src/views/LearningTasksView.vue`
- 实现 `frontend/src/views/AgentTraceView.vue`

- [ ] **Step 1：HistoryView**

页面结构：

- 顶部时间区间筛选（占位 select，后端未就绪时 disabled）。
- 主区域：折线图占位（不引入图表库，先用占位 `<div>` + 文本"功能尚未上线"），下方表格展示历史报告列表（empty 时 `EmptyState`、后端未就绪时 `BackendNotReadyNotice`）。
- 即使图表占位，文字提示必须明确"等待后端 reports 历史聚合接口"。

- [ ] **Step 2：VersionDiffView**

页面结构：

- 顶部双 select：基线版本 / 对比版本。
- 主区域：左右两栏 diff 占位；后端未就绪时整页 `BackendNotReadyNotice`，等待"简历版本 diff 接口"。
- 后端 ready 时，左右栏渲染各版本结构化摘要（不展示原文）。

- [ ] **Step 3：LearningTasksView**

页面结构：

- 上方"按当前缺口生成学习任务"按钮（后端未就绪 disabled）。
- 主区域：任务卡片列表，每卡片含目标、关联评分维度、状态徽章；后端未就绪时整列 `BackendNotReadyNotice`，等待"learning 接口"。

- [ ] **Step 4：AgentTraceView**

页面结构：

- 顶部任务 ID 与状态。
- 主区域：完整 `AgentTraceTimeline`（脱敏摘要展开版），允许节点级折叠。
- 后端未就绪时：整页 `BackendNotReadyNotice`，等待 "agent_runs 接口"。

- [ ] **Step 5：运行测试与类型检查**

每个 view 至少有一个 smoke test 断言：未就绪态渲染 `BackendNotReadyNotice`。

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 6：提交**

```powershell
git add frontend
git commit -m "feat(frontend): add history, diff, learning and trace views with backend-not-ready notices"
```

## Task 6：本地偏好 / 会话 与 UX 抛光

**文件：**

- 创建 `frontend/src/composables/useLocalStorageRef.ts`
- 创建 `frontend/src/composables/useResponsive.ts`
- 创建 `frontend/src/composables/useA11y.ts`
- 创建 `frontend/src/stores/preferences.ts`
- 实现 `frontend/src/views/SettingsView.vue`
- 创建 `frontend/src/components/layout/MobileNav.vue`
- 创建 `frontend/tests/composables/useLocalStorageRef.test.ts`
- 创建 `frontend/tests/views/SettingsView.test.ts`

- [ ] **Step 1：先写失败的 useLocalStorageRef 测试**

`useLocalStorageRef.test.ts` 断言：

- key 命名空间 `careerfit:pref:*`；非命名空间 key 写入会拒绝。
- 写入对象时序列化 + 反序列化对称。
- **白名单校验**：尝试写入 `raw_jd` / `raw_resume` / 任何超过 1KB 的字符串会拒绝并写控制台警告。
- 浏览器禁用 localStorage 时优雅降级到内存。

- [ ] **Step 2：先写失败的 SettingsView 测试**

`SettingsView.test.ts` 断言：

- 渲染主题选择（暗色 / 跟随系统，亮色 disabled 并标注 "Phase 2 启用"）、布局密度（紧凑 / 宽松）、最近打开历史长度 等本地偏好项。
- 修改设置后立即写入 `careerfit:pref:*`；刷新后保持。
- 不渲染任何账号、登录、邮箱、用户名相关 UI。

- [ ] **Step 3：实现 composables 与 stores/preferences**

`useLocalStorageRef.ts`：基于 VueUse `useStorage` 包一层命名空间 + 白名单校验。
`useResponsive.ts`：暴露 `isDesktop / isTablet / isMobile` 响应式断点（1280 / 1024 / 768 / 480）。
`useA11y.ts`：暴露 `prefersReducedMotion`、当前 focus trap 工具函数。
`stores/preferences.ts`：从 `useLocalStorageRef` 读出各项偏好并暴露给全局。

- [ ] **Step 4：实现 SettingsView 与 MobileNav**

`SettingsView.vue`：仅本地偏好；不与后端交互；显眼提示 "本设置仅保存在你的浏览器，未来如果清空浏览器数据将恢复默认。"
`MobileNav.vue`：768 px 以下替代 `SideNav` 的顶部 hamburger 菜单。

- [ ] **Step 5：UX 抛光走查**

逐页检查并补齐：

- 完整响应式：所有页面在 1440 / 1280 / 1024 / 768 / 480 五个断点都不溢出，关键操作可达。
- 完整无障碍：每个交互元素有可见 focus 描边；表单字段有 label 关联；图标按钮有 `aria-label`；对比度满足 WCAG AA。
- 动效：modal 打开 / 关闭、状态切换、Trace 节点展开 等关键交互有 150–250 ms 过渡；尊重 `prefers-reduced-motion`。

每完成一页打勾，未通过的页面回到对应 Task 修复。

- [ ] **Step 6：运行测试与类型检查**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 7：提交**

```powershell
git add frontend
git commit -m "feat(frontend): add local preferences, settings view and ux polish pass"
```

## Task 7：前端 Docker 化与前端 Phase 1.A 验收

**文件：**

- 创建 `frontend/Dockerfile`
- 创建 `docker-compose.frontend-only.yml`
- 创建 `.env.example`

- [ ] **Step 1：创建前端 Dockerfile**

基于 `node:20-alpine`，多阶段构建：build 阶段 `npm ci && npm run build`，runtime 阶段使用 `nginx:alpine` 提供静态文件，端口 80。

- [ ] **Step 2：创建独立前端 compose**

`docker-compose.frontend-only.yml`：仅启动 frontend 容器，**不依赖 backend**。前端在该模式下应全部走 `BackendNotReadyNotice` 占位。

- [ ] **Step 3：添加 .env.example（前端部分）**

```text
VITE_API_BASE=http://localhost:8000
VITE_APP_VARIANT=frontend-only
```

`VITE_APP_VARIANT=frontend-only` 时，前端跳过 `availability.fetchBackendCapabilities` 请求，直接把全部能力标记为 `unavailable`。

- [ ] **Step 4：前端独立冒烟**

```powershell
docker compose -f docker-compose.frontend-only.yml up --build
```

验证：

- 容器 healthy。
- 浏览器打开 `http://localhost:5173`（或映射端口）。
- 13 条路由全部可达。
- 工作台首屏渲染 `NextBestActionCallout` 与两个 `BackendNotReadyNotice`。
- 报告页 / 历史 / 对比 / 学习 / Trace 全部走占位。
- 设置页可读写本地偏好；刷新后保持；浏览器隐私模式下也不报错。

- [ ] **Step 5：前端 Phase 1.A 验收门自检**

逐条对照 `CLAUDE.md` "前端 Phase 1 验收门" 10 条；任何一条不满足，回到对应 Task 修复，不得跳过。

- [ ] **Step 6：提交**

```powershell
git add frontend/Dockerfile docker-compose.frontend-only.yml .env.example
git commit -m "chore: add frontend dockerfile and frontend-only compose; complete frontend phase 1.A"
```

---

# 第二部分：后端 Phase 1.B

## Task 8：后端项目骨架

**文件：**

- 创建 `backend/pyproject.toml`
- 创建 `backend/app/main.py`
- 创建 `backend/app/core/config.py`
- 创建 `backend/app/db/session.py`
- 创建 `backend/app/db/base.py`
- 创建 `backend/app/db/models.py`
- 创建 `backend/tests/conftest.py`

- [ ] **Step 1：创建后端依赖配置**

`backend/pyproject.toml` 必须包含 FastAPI、uvicorn、Pydantic、SQLAlchemy、psycopg、pgvector、LangGraph，以及 dev 依赖 pytest、httpx、ruff。配置 `setuptools` build backend，并让 pytest 的 `pythonpath` 指向当前目录。

- [ ] **Step 2：创建配置模块**

在 `backend/app/core/config.py` 中定义 `Settings`，至少包含：

```python
database_url = "sqlite+pysqlite:///./careerfit_dev.db"
app_name = "CareerFit Agent"
environment = "development"
```

使用 `pydantic-settings` 和 `CAREERFIT_` 环境变量前缀。

- [ ] **Step 3：创建数据库 session**

在 `backend/app/db/session.py` 中创建 SQLAlchemy engine、`SessionLocal` 和 `get_db()` 依赖。

- [ ] **Step 4：创建 Declarative Base**

在 `backend/app/db/base.py` 中定义 `Base(DeclarativeBase)`。

- [ ] **Step 5：创建初始模型**

在 `backend/app/db/models.py` 中创建：

- `JobDescription`
- `ResumeVersion`
- `AnalysisTask`
- `AnalysisReport`
- `AgentRun`
- `AnalysisStatus`

JSON 字段使用 SQLAlchemy 通用 `JSON` 类型，方便 SQLite 测试和 PostgreSQL 运行都能工作。

- [ ] **Step 6：创建 FastAPI app**

在 `backend/app/main.py` 中实现 `create_app()`，启动时调用 `Base.metadata.create_all(bind=engine)`，并提供 `/health` 与 `/api/capabilities`（后者返回当前已上线能力名单，供前端 availability store 消费）。

- [ ] **Step 7：创建测试 fixture**

`backend/tests/conftest.py` 使用内存 SQLite，覆盖 `get_db`，返回 `TestClient`。

- [ ] **Step 8：运行骨架测试**

```powershell
cd backend
python -m pip install -e ".[dev]"
pytest -q
```

预期：没有测试或测试通过。

- [ ] **Step 9：提交**

```powershell
git add backend
git commit -m "chore: scaffold backend application"
```

## Task 9：目标岗位和简历 API

**文件：**

- 创建 `backend/app/schemas/jobs.py`
- 创建 `backend/app/schemas/resumes.py`
- 创建 `backend/app/services/job_service.py`
- 创建 `backend/app/services/resume_service.py`
- 创建 `backend/app/api/routes/jobs.py`
- 创建 `backend/app/api/routes/resumes.py`
- 修改 `backend/app/main.py`
- 测试 `backend/tests/test_jobs_api.py`
- 测试 `backend/tests/test_resumes_api.py`

- [ ] **Step 1：先写失败的岗位 API 测试**

测试 `POST /api/jobs` 能创建岗位，并从 JD 文本中抽取 `FastAPI` 等技能；空 JD 返回 422。

- [ ] **Step 2：先写失败的简历 API 测试**

测试 `POST /api/resumes` 能创建简历版本，并从简历文本中抽取 `FastAPI` 等技能；空简历返回 422。

- [ ] **Step 3：运行测试确认失败**

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

预期：因为路由不存在而失败。

- [ ] **Step 4：创建 Pydantic schemas**

`jobs.py` 定义 `JobCreate` 和 `JobRead`。
`resumes.py` 定义 `ResumeCreate` 和 `ResumeRead`。
输入文本最小长度为 20，标题和名称不能为空。

- [ ] **Step 5：实现 service**

`job_service.py` 提供：

- `KNOWN_SKILLS`
- `parse_job_profile(raw_text)`
- `create_job(db, payload)`
- `list_jobs(db)`
- `get_job(db, job_id)`

`resume_service.py` 提供：

- `parse_resume_profile(raw_text)`
- `create_resume(db, payload)`
- `list_resumes(db)`
- `get_resume(db, resume_id)`

解析结果必须包含 `schema_version` 和证据字段。

- [ ] **Step 6：实现路由**

`jobs.py` 暴露：

```text
POST /api/jobs
GET /api/jobs
GET /api/jobs/{job_id}
```

`resumes.py` 暴露：

```text
POST /api/resumes
GET /api/resumes
GET /api/resumes/{resume_id}
```

不存在时返回 404。

- [ ] **Step 7：注册路由并更新 capabilities**

在 `backend/app/main.py` 中 include `jobs.router` 和 `resumes.router`，并更新 `/api/capabilities` 输出，把 `jobs` 与 `resumes` 标记为 `ready`。前端 availability store 会自动从占位切换到真实数据。

- [ ] **Step 8：运行测试确认通过**

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

- [ ] **Step 9：提交**

```powershell
git add backend/app backend/tests
git commit -m "feat: add job and resume APIs"
```

## Task 10：确定性评分和 Integrity Guard

**文件：**

- 创建 `backend/app/scoring/rubric.py`
- 创建 `backend/app/scoring/rules.py`
- 创建 `backend/app/scoring/evidence.py`
- 创建 `backend/tests/test_scoring.py`
- 创建 `backend/tests/test_integrity_guard.py`

- [ ] **Step 1：先写失败的评分测试**

测试 `score_match(jd_profile, resume_profile)`：

- 返回 `final_score`，范围必须在 0-100。
- `score_breakdown.skill_score` 大于 0。
- 每个 required skill 都有 `score_items`。
- 每个评分项包含 JD evidence。
- 空输入时最终分数为 0。

- [ ] **Step 2：先写失败的 Integrity Guard 测试**

测试 `assess_integrity_risk(suggestion, resume_text)`：

- 无证据百分比指标触发 `unsupported_metric`。
- 无证据"主导/生产级/架构设计"触发 `unsupported_leadership_claim`。
- 安全改写返回 `risk_level = low`。

- [ ] **Step 3：运行测试确认失败**

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

预期：模块不存在导致失败。

- [ ] **Step 4：实现 rubric**

`rubric.py` 定义能力层级分数：

```text
not_mentioned -> 0.0
mentioned -> 0.3
basic_usage -> 0.5
project_practice -> 0.75
deep_experience -> 1.0
```

并提供 `clamp_score(value)`，把分数限制在 0-100。

- [ ] **Step 5：实现 evidence 和 Integrity Guard**

`evidence.py` 提供：

- `find_resume_evidence(skill, resume_profile)`
- `assess_integrity_risk(suggestion, resume_text)`

需要识别百分比、倍数、ms 指标，以及"主导""负责架构""生产级"等领导力或生产化表述。

- [ ] **Step 6：实现确定性评分**

`rules.py` 提供 `score_match()`。最终分数使用固定权重：

```text
skill_score * 0.35
project_score * 0.25
domain_score * 0.15
basic_requirement_score * 0.10
expression_score * 0.10
integrity_risk_penalty * 0.05
```

LLM 不参与数字计算。

- [ ] **Step 7：运行测试确认通过**

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

- [ ] **Step 8：提交**

```powershell
git add backend/app/scoring backend/tests/test_scoring.py backend/tests/test_integrity_guard.py
git commit -m "feat: add deterministic scoring and integrity guard"
```

## Task 11：分析工作流和报告

**文件：**

- 创建 `backend/app/schemas/analysis.py`
- 创建 `backend/app/schemas/reports.py`
- 创建 `backend/app/agents/state.py`
- 创建 `backend/app/agents/nodes.py`
- 创建 `backend/app/agents/graph.py`
- 创建 `backend/app/services/analysis_service.py`
- 创建 `backend/app/api/routes/analysis.py`
- 创建 `backend/app/api/routes/reports.py`
- 创建 `backend/app/api/routes/agent_runs.py`
- 修改 `backend/app/main.py`
- 测试 `backend/tests/test_analysis_flow.py`

- [ ] **Step 1：先写失败的分析流程测试**

测试完整路径：创建 JD、创建简历、`POST /api/analysis`、读取报告、读取 Agent runs。

断言：

- 任务状态为 `success`。
- 报告 `final_score > 0`。
- 报告包含 `next_best_action.title`。
- 报告包含分项评分。
- Agent runs 至少包含多个节点，首个节点是 `jd_parser`。

- [ ] **Step 2：运行测试确认失败**

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

预期：路由不存在。

- [ ] **Step 3：创建 schemas**

`analysis.py` 定义 `AnalysisCreate` 和 `AnalysisTaskRead`。
`reports.py` 定义 `ReportRead` 和 `AgentRunRead`。

- [ ] **Step 4：创建 workflow state 和节点**

`state.py` 定义 `CareerFitState`。
`nodes.py` 实现：

- `jd_parser`
- `resume_parser`
- `match_scorer`
- `gap_analyzer`
- `resume_optimizer`
- `interview_coach`
- `learning_planner`
- `next_best_action`

`next_best_action` 必须在有缺口时返回优先补齐技能；没有缺口时建议创建下一版简历并重新分析。

- [ ] **Step 5：实现 graph runner 和 trace logging**

`graph.py` 定义节点序列、`redact_state()` 和 `run_workflow()`。
UI trace 中必须把 `raw_jd` 和 `raw_resume` 替换成 `[redacted]`。

- [ ] **Step 6：实现分析 service 和路由**

`analysis_service.py` 负责：

1. 校验 job 和 resume 是否存在。
2. 创建 `AnalysisTask`。
3. 执行 workflow。
4. 创建 `AnalysisReport`。
5. 成功时把 task 标记为 `success`。
6. 失败时把 task 标记为 `failed` 并保存错误。

路由：

```text
POST /api/analysis
GET /api/reports/{task_id}
GET /api/agent-runs/{task_id}
```

- [ ] **Step 7：注册路由并更新 capabilities**

在 `main.py` 中 include `analysis`、`reports`、`agent_runs`，并把 `analysis` / `reports` / `agentRuns` 在 `/api/capabilities` 中切到 `ready`。

- [ ] **Step 8：运行分析流程测试**

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

- [ ] **Step 9：运行全部后端测试**

```powershell
cd backend
pytest -q
```

- [ ] **Step 10：提交**

```powershell
git add backend/app backend/tests
git commit -m "feat: add analysis workflow and reports"
```

---

# 第三部分：联调与最终验证

## Task 12：前后端联调与全栈 Docker Compose

**文件：**

- 创建 `backend/Dockerfile`
- 创建 `docker-compose.yml`
- 修改 `frontend/.env.example`

- [ ] **Step 1：添加后端 Dockerfile**

后端镜像基于 `python:3.11-slim`，安装 `pyproject.toml` 依赖，启动命令为：

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- [ ] **Step 2：完善 .env.example（全栈）**

```text
CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit
VITE_API_BASE=http://localhost:8000
VITE_APP_VARIANT=fullstack
```

`fullstack` 模式下前端正常调用 `/api/capabilities` 与各业务接口。

- [ ] **Step 3：添加全栈 Docker Compose**

`docker-compose.yml` 包含：

- `postgres`：使用 `pgvector/pgvector:pg16`。
- `backend`：依赖 postgres healthcheck。
- `frontend`：依赖 backend healthcheck（避免在 capabilities 接口未起来时探测失败）。

端口：

```text
postgres 5432
backend 8000
frontend 5173
```

- [ ] **Step 4：联调走查**

```powershell
docker compose up --build
```

逐项验证：

- 工作台从打开 / 创建岗位 / 创建简历 / 启动分析 / 看报告 端到端可走通。
- 报告页的总分、Next Best Action、维度卡、证据链卡、简历建议、Integrity Guard、Agent Trace 时间线 全部由真实后端数据驱动。
- 前端没有任何路由仍处于 `BackendNotReadyNotice` 状态时，对应能力都已上线（即周边模块如 history/diff/learning 仍可显示 notice，因为它们不在后端 Phase 1.B 范围内 —— 这是预期的；不影响 Phase 1 验收）。
- Agent Trace UI 不渲染原始 JD 或简历文本。
- 风险标签同时有色与文字。

- [ ] **Step 5：前后端集成测试（轻量）**

可选：用 Playwright 做一条 happy-path 端到端 smoke。如果引入需在 `frontend/package.json` 增加 dev 依赖；不强制。

- [ ] **Step 6：提交**

```powershell
git add backend/Dockerfile docker-compose.yml frontend/.env.example
git commit -m "chore: add backend dockerfile and fullstack docker compose"
```

## Task 13：README 与最终验证

**文件：**

- 创建 `README.md`

- [ ] **Step 1：编写 README（中文）**

README 必须包含：

- 项目简介与边界（不做登录、不做多租户、不做 HR 端、不做导师端）。
- 技术栈。
- 两种运行方式：
  - 仅前端（`docker compose -f docker-compose.frontend-only.yml up`），用于在没有后端的情况下查看完整网站结构与"功能未上线"状态。
  - 全栈（`docker compose up`），可信主路径端到端可用。
- 默认地址：前端 `http://localhost:5173`、后端 `http://localhost:8000`。
- Phase 1 双验收门简介及当前对应实现位置。

- [ ] **Step 2：运行全部后端测试**

```powershell
cd backend
pytest -q
```

- [ ] **Step 3：运行全部前端测试与类型检查**

```powershell
cd frontend
npm test
npm run typecheck
```

- [ ] **Step 4：构建 Docker stack 全栈**

```powershell
docker compose up --build
```

- [ ] **Step 5：构建前端独立 stack**

```powershell
docker compose -f docker-compose.frontend-only.yml up --build
```

- [ ] **Step 6：双验收门最终自检**

按 `CLAUDE.md` "Phase 1 验收门" 全部条目逐项打勾；任何一项未达成不得声称 Phase 1 完成。

- [ ] **Step 7：提交 README**

```powershell
git add README.md
git commit -m "docs: add project README"
```

---

## 自检清单

### 前端 Phase 1.A

- [ ] 13 条路由全部存在且可达。
- [ ] 每个页面支持空 / 加载 / 错误 / 部分数据 四态。
- [ ] 后端缺口处显示 `BackendNotReadyNotice`，不出现 mock 数据。
- [ ] 风险信息全部色 + 文字双通道。
- [ ] `Next Best Action` 在工作台首屏与报告头部显眼位呈现。
- [ ] 报告结构化展示，无大段 AI 生成纯文本堆叠。
- [ ] 完整响应式（桌面 / 平板 / 移动端）。
- [ ] 完整无障碍（键盘 / ARIA / 对比度 / focus 描边）。
- [ ] 关键交互有动效过渡，并尊重 `prefers-reduced-motion`。
- [ ] 本地偏好通过 localStorage 持久化；命名空间 `careerfit:pref:*`；白名单拒绝 PII。
- [ ] 浏览器隐私模式 / 清空数据后能优雅恢复默认。
- [ ] 无登录 / 无注册 / 无多租户 UI。
- [ ] 前端独立 Docker compose 可启动并正常显示占位状态。

### 后端 Phase 1.B

- [ ] 可以通过 API 创建目标岗位、简历版本、执行分析。
- [ ] `analysis_tasks` / `analysis_reports` / `agent_runs` 持久化。
- [ ] 报告含总分、分项评分、优势、缺口、简历建议、面试题、学习计划、`Next Best Action`。
- [ ] 每个评分项可追溯到 JD 证据与简历证据。
- [ ] Agent Trace 对 UI 展示脱敏，不暴露原始 JD / 简历文本。
- [ ] `Integrity Guard` 阻止无证据指标与夸大职责。
- [ ] 评分确定性，全部测试通过。
- [ ] `/api/capabilities` 正确反映当前已上线能力。
- [ ] 后端单独 Docker（与 postgres）可启动并通过 healthcheck。

### 全栈

- [ ] 前后端联调走通主路径；报告页所有数据来自真实后端。
- [ ] 全栈 Docker Compose 可启动 frontend、backend、postgres。
- [ ] README 说明两种运行方式与 Phase 1 双验收门。
