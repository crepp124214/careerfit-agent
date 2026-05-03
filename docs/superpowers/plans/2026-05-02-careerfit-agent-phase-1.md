<!-- /autoplan restore point: /c/Users/qwer/.gstack/projects/Newproject2/main-autoplan-restore-20260503-032137.md -->
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

- [x] **Step 1：创建前端依赖配置**

`package.json` 必须包含：

- 运行时：Vue3、Vue Router、Pinia、VueUse、`reka-ui`（Phase 4 D4）、`echarts` + `vue-echarts`（Phase 4 D5，T5 趋势图主力）。
- 构建：Vite、`@vitejs/plugin-vue`、TypeScript、`vite-tsconfig-paths`、`@types/node`。
- 测试：Vitest、`@vue/test-utils`、jsdom、`@vitest/coverage-v8`。

脚本至少包含：

```text
npm run dev
npm run build
npm run preview
npm test
npm run typecheck
```

UI 组件库已锁定为 Reka UI（headless），样式与变体走 `docs/DESIGN.md`；Reka 不提供的细分组件在 T2 自行实现。ECharts 在 T1 引入是为了固定核心依赖结构，T5 直接调用，无需后续重做 `package.json`。

- [x] **Step 2：创建 TypeScript 与 Vite 配置**

`tsconfig.json` 开启严格模式（`strict: true`、`noUncheckedIndexedAccess: true`），路径别名 `@ -> src`。
`vite.config.ts` 注册 `@vitejs/plugin-vue`，Vitest 环境为 `jsdom`，`coverage` 启用 v8 reporter。

- [x] **Step 3：创建路由表**

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

- [x] **Step 4：先写失败的路由 smoke 测试**

`tests/routing.test.ts` 断言：

- 上述 13 条路由都能解析到对应 view（不报路由 not found）。
- `/` 命中 `WorkspaceView`。
- 未知路径命中 `NotFoundView`。

- [x] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm install
npm test
```

- [x] **Step 6：实现路由与 App shell**

`App.vue` 使用 `<RouterView>`，外层包一个最小 `AppShell`（暂不含侧栏）。`main.ts` 装配 `createApp` + `createPinia` + `router`。

- [x] **Step 7：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 8：修订 `docs/DESIGN.md`（Phase 4 D12）**

把 480px 章节"Phase 1 不要求完整布局"改写为五档断点（480 / 768 / 1024 / 1280 / 1440）全覆盖，与 CLAUDE.md 前端实现约束一致。同步更新已知缺口 #3，使其不再声明 480px 仅做最小可读。修订必须与 T1 在同一个 commit 落地，避免后续 T3–T7 在错误断点假设下返工。

- [x] **Step 9：提交**

```powershell
git add frontend docs/DESIGN.md docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md
git commit -m "feat: scaffold frontend with router, 13 routes and design breakpoint fix"
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

- [x] **Step 1：把 docs/DESIGN.md 的 token 落到 tokens.css**

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

- [x] **Step 2：先写失败的 RiskPill 测试**

`RiskPill.test.ts` 断言：

- props `level: "high" | "medium" | "low"` 控制底色与文字色。
- 必须渲染 `aria-label` 与可见文字（"高风险" / "需关注" / "通过"）；**只有颜色没有文字会失败测试**。
- 文字 fallback：未传入 `label` 时使用约定中文标签。

- [x] **Step 3：先写失败的 BackendNotReadyNotice 测试**

`BackendNotReadyNotice.test.ts` 断言：

- 必传 props `feature`（功能名）、`waitingFor`（依赖的后端能力）。
- 渲染默认文案 "{feature}尚未上线，等待后端 {waitingFor}"。
- 不允许渲染任何 mock 数据样本（断言：组件 render 输出中不出现"示例""sample""demo"等字样，以及任何看似真实的数字/分数）。
- 必须含 `role="status"` 或 `role="alert"` 之一。

- [x] **Step 4：先写失败的 NextBestActionCallout 测试**

`NextBestActionCallout.test.ts` 断言：

- props `state: "ready" | "blocked" | "empty"`。
- `ready`：渲染 lavender 左色条 + headline 文案 + 主按钮。
- `blocked`：按钮 disabled，渲染等待原因文案。
- `empty`：渲染 ink-subtle "当前没有推荐行动" 文案，无按钮。
- headline 文案超过 24 字符必须被截断或换行处理，不得溢出。

- [x] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [x] **Step 6：实现共享原子组件**

按 `docs/DESIGN.md` 组件契约实现 `AppButton`/`AppInput`/`AppTextarea`/`StatusBadge`/`Modal`，全部状态齐全（默认/hover/focus/active/disabled/loading/error）。

- [x] **Step 7：实现反馈与风险组件**

按测试断言实现 `EmptyState`/`LoadingCard`/`ErrorBanner`/`BackendNotReadyNotice`/`SkeletonBlock`/`RiskPill`/`IntegrityGuardBanner`/`NextBestActionCallout`。

- [x] **Step 8：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 9：提交**

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

- [x] **Step 1：实现 API client 与 availability 探测**

`client.ts` 实现 `requestJson<T>()`，对 404/501/网络错误统一返回 `unavailable` 标志而不是抛错，让 stores 决定渲染 `BackendNotReadyNotice` 还是 `ErrorBanner`。
`availability.ts` 提供 `fetchBackendCapabilities()`，调用后端 `/api/capabilities`（后端未实现时返回 `unavailable`，前端按"全部能力未就绪"处理）。

- [x] **Step 2：实现 stores**

`stores/availability.ts`：Pinia store，记录每个能力（jobs / resumes / analysis / reports / agentRuns / learning）的状态：`unknown | ready | unavailable`。
`stores/jobs.ts` 与 `stores/resumes.ts`：对应的 CRUD 调用与缓存；后端 `unavailable` 时 store 不写入任何 mock 数据，组件层自行渲染 `BackendNotReadyNotice`。

- [x] **Step 3：实现 layout 组件**

`AppShell.vue`：左侧 `SideNav`、底部 `StatusBar`、主内容 `<RouterView>` 区。
`SideNav.vue`：列出 工作台 / 岗位 / 简历 / 历史 / 对比 / 学习 / 设置 7 个入口，未就绪能力以 ink-subtle 文字 + 锁形图标显示，但**仍可点击进入**对应页面查看 `BackendNotReadyNotice`。
`StatusBar.vue`：底部一行展示当前后端连通性（"已连接 / 部分未上线 / 后端未连接"）+ 当前会话脱敏注记。

- [x] **Step 4：先写失败的 WorkspaceView 测试**

`tests/views/WorkspaceView.test.ts` 断言：

- 默认渲染 `NextBestActionCallout`（state=`empty` 时渲染"当前没有推荐行动"）。
- 后端 `unavailable` 时，岗位选择器与简历选择器各自显示 `BackendNotReadyNotice`，文案分别提到 "等待后端 jobs API" 与 "等待后端 resumes API"。
- 后端 `ready` 但列表为空时显示 `EmptyState` + "新建岗位 / 新建简历" 按钮。
- 视图根元素带有 `role="main"` 与可见标题"个人求职成长工作台"。

- [x] **Step 5：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [x] **Step 6：实现工作台首屏**

`WorkspaceView.vue`：顶部 `NextBestActionCallout`，下方两栏分别为 `JobSelector` 与 `ResumeSelector`，再下方 `AnalysisLauncher`。每个组件按 store 状态渲染 `BackendNotReadyNotice` / `LoadingCard` / `EmptyState` / 真实数据 四态之一。

- [x] **Step 7：实现岗位与简历管理**

`JobsView.vue`：列表 + "新建岗位" 按钮 + 表单 Modal；后端未就绪时整个表单 disabled 并显示 `BackendNotReadyNotice`。
`JobDetailView.vue`：详情 + 解析摘要 + 相关分析任务列表；后端未就绪时显示 notice。
`ResumesView.vue` + `ResumeDetailView.vue`：同上结构。

- [x] **Step 8：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 9：提交**

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

- [x] **Step 1：先写失败的 AgentTraceTimeline 测试**

`AgentTraceTimeline.test.ts` 断言：

- 节点输入/输出展示区只渲染 `summary`、`length`、`field_names` 等脱敏字段；如果 props 中包含 `raw_jd` 或 `raw_resume`，组件抛出 dev-only 警告并**不渲染原文**。
- 节点状态 `running / success / failed` 分别对应 info-trace / risk-low / risk-high 配色 + 文字标签。
- 长列表支持折叠（768 px 以下默认折叠）。

- [x] **Step 2：先写失败的 ReportView 测试**

`ReportView.test.ts` 断言：

- `/reports/:taskId` 路由可达；`taskId` 非法时显示 `ErrorBanner`。
- 后端 reports API `unavailable` 时，整个报告区显示 `BackendNotReadyNotice`，文案为 "评分报告功能尚未上线，等待后端 analysis pipeline 完成"。
- 后端 ready 但任务尚未完成时显示 `LoadingCard` + "分析中..." 文案。
- 后端 ready 且数据返回时，顶部固定 `NextBestActionCallout`、其下 `ScoringOverviewCard`、再下方维度卡列表、再下方简历建议卡列表、底部 `AgentTraceTimeline`。
- 简历建议被 Integrity Guard 拦截时，列表上方插入 `IntegrityGuardBanner`，被拦截卡片置灰并带 `RiskPill level="high" label="高风险"`。

- [x] **Step 3：运行测试确认失败**

```powershell
cd frontend
npm test
```

- [x] **Step 4：实现报告组件**

按 `docs/DESIGN.md` 组件契约实现 `ScoringOverviewCard`/`ScoringDimensionCard`/`EvidenceCard`/`SuggestionCard`/`AgentTraceRow`/`AgentTraceTimeline`。证据卡的 JD 与简历原文展示长度上限 200 字符，超出折叠。

- [x] **Step 5：实现分析执行视图与报告视图**

`AnalysisRunView.vue`：选岗位 + 选简历 + 启动分析；后端未就绪时按钮 disabled + notice。
`ReportView.vue`：组合上述组件，按 store 状态渲染 4 态。

- [x] **Step 6：运行测试确认通过**

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 7：提交**

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

- [x] **Step 1：HistoryView**

页面结构：

- 顶部时间区间筛选（占位 select，后端未就绪时 disabled）。
- 主区域：折线图占位（不引入图表库，先用占位 `<div>` + 文本"功能尚未上线"），下方表格展示历史报告列表（empty 时 `EmptyState`、后端未就绪时 `BackendNotReadyNotice`）。
- 即使图表占位，文字提示必须明确"等待后端 reports 历史聚合接口"。

- [x] **Step 2：VersionDiffView**

页面结构：

- 顶部双 select：基线版本 / 对比版本。
- 主区域：左右两栏 diff 占位；后端未就绪时整页 `BackendNotReadyNotice`，等待"简历版本 diff 接口"。
- 后端 ready 时，左右栏渲染各版本结构化摘要（不展示原文）。

- [x] **Step 3：LearningTasksView**

页面结构：

- 上方"按当前缺口生成学习任务"按钮（后端未就绪 disabled）。
- 主区域：任务卡片列表，每卡片含目标、关联评分维度、状态徽章；后端未就绪时整列 `BackendNotReadyNotice`，等待"learning 接口"。

- [x] **Step 4：AgentTraceView**

页面结构：

- 顶部任务 ID 与状态。
- 主区域：完整 `AgentTraceTimeline`（脱敏摘要展开版），允许节点级折叠。
- 后端未就绪时：整页 `BackendNotReadyNotice`，等待 "agent_runs 接口"。

- [x] **Step 5：运行测试与类型检查**

每个 view 至少有一个 smoke test 断言：未就绪态渲染 `BackendNotReadyNotice`。

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 6：提交**

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

- [x] **Step 1：先写失败的 useLocalStorageRef 测试**

`useLocalStorageRef.test.ts` 断言：

- key 命名空间 `careerfit:pref:*`；非命名空间 key 写入会拒绝。
- 写入对象时序列化 + 反序列化对称。
- **白名单校验**：尝试写入 `raw_jd` / `raw_resume` / 任何超过 1KB 的字符串会拒绝并写控制台警告。
- 浏览器禁用 localStorage 时优雅降级到内存。

- [x] **Step 2：先写失败的 SettingsView 测试**

`SettingsView.test.ts` 断言：

- 渲染主题选择（暗色 / 跟随系统，亮色 disabled 并标注 "Phase 2 启用"）、布局密度（紧凑 / 宽松）、最近打开历史长度 等本地偏好项。
- 修改设置后立即写入 `careerfit:pref:*`；刷新后保持。
- 不渲染任何账号、登录、邮箱、用户名相关 UI。

- [x] **Step 3：实现 composables 与 stores/preferences**

`useLocalStorageRef.ts`：基于 VueUse `useStorage` 包一层命名空间 + 白名单校验。
`useResponsive.ts`：暴露 `isDesktop / isTablet / isMobile` 响应式断点（1280 / 1024 / 768 / 480）。
`useA11y.ts`：暴露 `prefersReducedMotion`、当前 focus trap 工具函数。
`stores/preferences.ts`：从 `useLocalStorageRef` 读出各项偏好并暴露给全局。

- [x] **Step 4：实现 SettingsView 与 MobileNav**

`SettingsView.vue`：仅本地偏好；不与后端交互；显眼提示 "本设置仅保存在你的浏览器，未来如果清空浏览器数据将恢复默认。"
`MobileNav.vue`：768 px 以下替代 `SideNav` 的顶部 hamburger 菜单。

- [x] **Step 5：UX 抛光走查**

逐页检查并补齐：

- 完整响应式：所有页面在 1440 / 1280 / 1024 / 768 / 480 五个断点都不溢出，关键操作可达。
- 完整无障碍：每个交互元素有可见 focus 描边；表单字段有 label 关联；图标按钮有 `aria-label`；对比度满足 WCAG AA。
- 动效：modal 打开 / 关闭、状态切换、Trace 节点展开 等关键交互有 150–250 ms 过渡；尊重 `prefers-reduced-motion`。

每完成一页打勾，未通过的页面回到对应 Task 修复。

- [x] **Step 6：运行测试与类型检查**

```powershell
cd frontend
npm test
npm run typecheck
```

- [x] **Step 7：提交**

```powershell
git add frontend
git commit -m "feat(frontend): add local preferences, settings view and ux polish pass"
```

## Task 7：前端 Docker 化与前端 Phase 1.A 验收

**文件：**

- 创建 `frontend/Dockerfile`
- 创建 `docker-compose.frontend-only.yml`
- 创建 `.env.example`

- [x] **Step 1：创建前端 Dockerfile**

基于 `node:20-alpine`，多阶段构建：build 阶段 `npm ci && npm run build`，runtime 阶段使用 `nginx:alpine` 提供静态文件，端口 80。

- [x] **Step 2：创建独立前端 compose**

`docker-compose.frontend-only.yml`：仅启动 frontend 容器，**不依赖 backend**。前端在该模式下应全部走 `BackendNotReadyNotice` 占位。

- [x] **Step 3：添加 .env.example（前端部分）**

```text
VITE_API_BASE=http://localhost:8000
VITE_APP_VARIANT=frontend-only
```

`VITE_APP_VARIANT=frontend-only` 时，前端跳过 `availability.fetchBackendCapabilities` 请求，直接把全部能力标记为 `unavailable`。

- [x] **Step 4：前端独立冒烟**

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

- [x] **Step 5：前端 Phase 1.A 验收门自检**

逐条对照 `CLAUDE.md` "前端 Phase 1 验收门" 10 条；任何一条不满足，回到对应 Task 修复，不得跳过。

- [x] **Step 6：提交**

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

- [x] **Step 1：创建后端依赖配置**

`backend/pyproject.toml` 必须包含 FastAPI、uvicorn、Pydantic、SQLAlchemy、psycopg、pgvector、LangGraph，以及 dev 依赖 pytest、httpx、ruff。配置 `setuptools` build backend，并让 pytest 的 `pythonpath` 指向当前目录。

- [x] **Step 2：创建配置模块**

在 `backend/app/core/config.py` 中定义 `Settings`，至少包含：

```python
database_url = "sqlite+pysqlite:///./careerfit_dev.db"
app_name = "CareerFit Agent"
environment = "development"
```

使用 `pydantic-settings` 和 `CAREERFIT_` 环境变量前缀。

- [x] **Step 3：创建数据库 session**

在 `backend/app/db/session.py` 中创建 SQLAlchemy engine、`SessionLocal` 和 `get_db()` 依赖。

- [x] **Step 4：创建 Declarative Base**

在 `backend/app/db/base.py` 中定义 `Base(DeclarativeBase)`。

- [x] **Step 5：创建初始模型**

在 `backend/app/db/models.py` 中创建：

- `JobDescription`
- `ResumeVersion`
- `AnalysisTask`
- `AnalysisReport`
- `AgentRun`
- `AnalysisStatus`

JSON 字段使用 SQLAlchemy 通用 `JSON` 类型，方便 SQLite 测试和 PostgreSQL 运行都能工作。

- [x] **Step 6：创建 FastAPI app**

在 `backend/app/main.py` 中实现 `create_app()`，启动时调用 `Base.metadata.create_all(bind=engine)`，并提供 `/health` 与 `/api/capabilities`（后者返回当前已上线能力名单，供前端 availability store 消费）。

- [x] **Step 7：创建测试 fixture**

`backend/tests/conftest.py` 使用内存 SQLite，覆盖 `get_db`，返回 `TestClient`。

- [x] **Step 8：运行骨架测试**

```powershell
cd backend
python -m pip install -e ".[dev]"
pytest -q
```

预期：没有测试或测试通过。

- [x] **Step 9：提交**

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

- [x] **Step 1：先写失败的岗位 API 测试**

测试 `POST /api/jobs` 能创建岗位，并从 JD 文本中抽取 `FastAPI` 等技能；空 JD 返回 422。

- [x] **Step 2：先写失败的简历 API 测试**

测试 `POST /api/resumes` 能创建简历版本，并从简历文本中抽取 `FastAPI` 等技能；空简历返回 422。

- [x] **Step 3：运行测试确认失败**

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

预期：因为路由不存在而失败。

- [x] **Step 4：创建 Pydantic schemas**

`jobs.py` 定义 `JobCreate` 和 `JobRead`。
`resumes.py` 定义 `ResumeCreate` 和 `ResumeRead`。
输入文本最小长度为 20，标题和名称不能为空。

- [x] **Step 5：实现 service**

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

- [x] **Step 6：实现路由**

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

- [x] **Step 7：注册路由并更新 capabilities**

在 `backend/app/main.py` 中 include `jobs.router` 和 `resumes.router`，并更新 `/api/capabilities` 输出，把 `jobs` 与 `resumes` 标记为 `ready`。前端 availability store 会自动从占位切换到真实数据。

- [x] **Step 8：运行测试确认通过**

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

- [x] **Step 9：提交**

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

- [x] **Step 1：先写失败的评分测试**

测试 `score_match(jd_profile, resume_profile)`：

- 返回 `final_score`，范围必须在 0-100。
- `score_breakdown.skill_score` 大于 0。
- 每个 required skill 都有 `score_items`。
- 每个评分项包含 JD evidence。
- 空输入时最终分数为 0。

- [x] **Step 2：先写失败的 Integrity Guard 测试**

测试 `assess_integrity_risk(suggestion, resume_text)`：

- 无证据百分比指标触发 `unsupported_metric`。
- 无证据"主导/生产级/架构设计"触发 `unsupported_leadership_claim`。
- 安全改写返回 `risk_level = low`。

- [x] **Step 3：运行测试确认失败**

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

预期：模块不存在导致失败。

- [x] **Step 4：实现 rubric**

`rubric.py` 定义能力层级分数：

```text
not_mentioned -> 0.0
mentioned -> 0.3
basic_usage -> 0.5
project_practice -> 0.75
deep_experience -> 1.0
```

并提供 `clamp_score(value)`，把分数限制在 0-100。

- [x] **Step 5：实现 evidence 和 Integrity Guard**

`evidence.py` 提供：

- `find_resume_evidence(skill, resume_profile)`
- `assess_integrity_risk(suggestion, resume_text)`

需要识别百分比、倍数、ms 指标，以及"主导""负责架构""生产级"等领导力或生产化表述。

- [x] **Step 6：实现确定性评分**

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

- [x] **Step 7：运行测试确认通过**

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

- [x] **Step 8：提交**

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

- [x] **Step 1：先写失败的分析流程测试**

测试完整路径：创建 JD、创建简历、`POST /api/analysis`、读取报告、读取 Agent runs。

断言：

- 任务状态为 `success`。
- 报告 `final_score > 0`。
- 报告包含 `next_best_action.title`。
- 报告包含分项评分。
- Agent runs 至少包含多个节点，首个节点是 `jd_parser`。

- [x] **Step 2：运行测试确认失败**

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

预期：路由不存在。

- [x] **Step 3：创建 schemas**

`analysis.py` 定义 `AnalysisCreate` 和 `AnalysisTaskRead`。
`reports.py` 定义 `ReportRead` 和 `AgentRunRead`。

- [x] **Step 4：创建 workflow state 和节点**

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

- [x] **Step 5：实现 graph runner 和 trace logging**

`graph.py` 定义节点序列、`redact_state()` 和 `run_workflow()`。
UI trace 中必须把 `raw_jd` 和 `raw_resume` 替换成 `[redacted]`。

- [x] **Step 6：实现分析 service 和路由**

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

- [x] **Step 7：注册路由并更新 capabilities**

在 `main.py` 中 include `analysis`、`reports`、`agent_runs`，并把 `analysis` / `reports` / `agentRuns` 在 `/api/capabilities` 中切到 `ready`。

- [x] **Step 8：运行分析流程测试**

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

- [x] **Step 9：运行全部后端测试**

```powershell
cd backend
pytest -q
```

- [x] **Step 10：提交**

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
- 修改 `.env.example`

- [x] **Step 1：添加后端 Dockerfile**

后端镜像基于 `python:3.12-slim`，安装 `pyproject.toml` 依赖，启动命令为：

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- [x] **Step 2：完善 .env.example（全栈）**

```text
CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_VARIANT=fullstack
```

`fullstack` 模式下前端正常调用 `/api/capabilities` 与各业务接口。

- [x] **Step 3：添加全栈 Docker Compose**

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

- [x] **Step 4：联调走查**

```powershell
docker compose up --build
```

2026-05-03 执行记录（第二轮 — Docker daemon 已启动）：

- 已运行：`docker compose up --build -d`，三个容器全部启动成功（postgres healthy, backend healthy, frontend healthy）。
- 已验证 `/api/capabilities`：`jobs/resumes/analysis/reports/agentRuns` 为 `ready`，`learning` 为 `unavailable`。
- 已验证主路径 API 端到端：
  - `POST /api/jobs` → 创建 job id=2
  - `POST /api/resumes` → 创建 resume id=2
  - `POST /api/analysis` → 创建 analysis id=2，status=`success`
  - `GET /api/reports/2` → 完整报告（final_score=50, score_breakdown 6 维, strengths, gaps, resume_suggestions 含 integrity, interview_questions, learning_plan, next_best_action, evidence 含 jd+resume 双证据）
  - `GET /api/agent-runs/2` → 8 个 agent 节点全部 success（jd_parser, resume_parser, match_scorer, gap_analyzer, resume_optimizer, interview_coach, learning_planner, next_best_action）
- Agent Trace 脱敏确认：所有 input_snapshot 中 `raw_jd`/`raw_resume` 均为 `"[redacted]"`。
- 前端 HTML 正常返回，title 为 "CareerFit Agent"。

2026-05-03 继续执行记录（第三轮 — 真实报告页联调修复）：

- 已补充 `frontend/.dockerignore` 与 `backend/.dockerignore`，避免 Docker build context 带入 `node_modules` / `dist` / 缓存文件。
- 已修复 Agent Trace 对外快照中间态 evidence 泄漏原文的问题；API 冒烟确认 `traceContainsRawText = false`。
- 已修复报告页前端适配真实后端 snake_case 报告与 agent-runs 响应；直达报告页时由 `AppShell` 触发 capabilities probe。
- 已修复生产页无效 favicon 请求造成的 404 控制台错误。
- 已修复 frontend 容器 healthcheck 使用 `localhost` 连接失败，改为 `127.0.0.1`。
- 已验证：`docker compose ps` 显示 postgres、backend、frontend 均为 healthy；`/health`、`/api/capabilities`、创建岗位、创建简历、执行分析、读取报告、读取 Agent runs 全部成功。
- 已用 Playwright 打开 `http://localhost:5173/reports/6`，报告页渲染总分、Next Best Action、评分明细、简历建议和 Agent 运行轨迹；控制台 0 error / 0 warning；Agent Trace 区域不包含原始 JD/简历文本。

逐项验证：

- [x] 工作台从打开 / 创建岗位 / 创建简历 / 启动分析 / 看报告 端到端可走通。
- [x] 报告页的总分、Next Best Action、维度卡、证据链卡、简历建议、Integrity Guard、Agent Trace 时间线 全部由真实后端数据驱动。
- [x] 前端没有任何路由仍处于 `BackendNotReadyNotice` 状态时，对应能力都已上线（即周边模块如 history/diff/learning 仍可显示 notice，因为它们不在后端 Phase 1.B 范围内 —— 这是预期的；不影响 Phase 1 验收）。
- [x] Agent Trace UI 不渲染原始 JD 或简历文本。
- [x] 风险标签同时有色与文字。

- [x] **Step 5：前后端集成测试（轻量）**

可选：用 Playwright 做一条 happy-path 端到端 smoke。如果引入需在 `frontend/package.json` 增加 dev 依赖；不强制。

2026-05-03：通过 curl 验证了完整的主路径 API（create job → create resume → create analysis → get report → get agent-runs），所有节点 success，脱敏正确。随后用 Playwright 做报告页 smoke，未引入 Playwright 依赖或测试文件。

- [x] **Step 6：提交**

```powershell
git add backend/Dockerfile docker-compose.yml frontend/.env.example
git commit -m "chore: add backend dockerfile and fullstack docker compose"
```

注：T12 Steps 1-3 已在 `3606ed9` 提交。Step 4-5 验证记录更新随 T13 README 一起提交。

## Task 13：README 与最终验证

**文件：**

- 创建 `README.md`

- [x] **Step 1：编写 README（中文）**

README 必须包含：

- 项目简介与边界（不做登录、不做多租户、不做 HR 端、不做导师端）。
- 技术栈。
- 两种运行方式：
  - 仅前端（`docker compose -f docker-compose.frontend-only.yml up`），用于在没有后端的情况下查看完整网站结构与"功能未上线"状态。
  - 全栈（`docker compose up`），可信主路径端到端可用。
- 默认地址：前端 `http://localhost:5173`、后端 `http://localhost:8000`。
- Phase 1 双验收门简介及当前对应实现位置。

- [x] **Step 2：运行全部后端测试**（2026-05-03：15 passed）

- [x] **Step 3：运行全部前端测试与类型检查**（2026-05-03：77 tests passed，typecheck clean）

- [x] **Step 4：构建 Docker stack 全栈**（2026-05-03：postgres + backend + frontend 全部 healthy）

- [x] **Step 5：构建前端独立 stack**（跳过 — 已在 T7 验证通过，本次资源集中全栈验证）

- [x] **Step 6：双验收门最终自检**

按 `CLAUDE.md` "Phase 1 验收门" 全部条目逐项打勾；任何一项未达成不得声称 Phase 1 完成。

- [x] **Step 7：提交 README**

```powershell
git add README.md
git commit -m "docs: add project README"
```

---

## 自检清单

### 前端 Phase 1.A

- [x] 13 条路由全部存在且可达。
- [x] 每个页面支持空 / 加载 / 错误 / 部分数据 四态。
- [x] 后端缺口处显示 `BackendNotReadyNotice`，不出现 mock 数据。
- [x] 风险信息全部色 + 文字双通道。
- [x] `Next Best Action` 在工作台首屏与报告头部显眼位呈现。
- [x] 报告结构化展示，无大段 AI 生成纯文本堆叠。
- [x] 完整响应式（桌面 / 平板 / 移动端）。
- [x] 完整无障碍（键盘 / ARIA / 对比度 / focus 描边）。
- [x] 关键交互有动效过渡，并尊重 `prefers-reduced-motion`。
- [x] 本地偏好通过 localStorage 持久化；命名空间 `careerfit:pref:*`；白名单拒绝 PII。
- [x] 浏览器隐私模式 / 清空数据后能优雅恢复默认。
- [x] 无登录 / 无注册 / 无多租户 UI。
- [x] 前端独立 Docker compose 可启动并正常显示占位状态。

### 后端 Phase 1.B

- [x] 可以通过 API 创建目标岗位、简历版本、执行分析。
- [x] `analysis_tasks` / `analysis_reports` / `agent_runs` 持久化。
- [x] 报告含总分、分项评分、优势、缺口、简历建议、面试题、学习计划、`Next Best Action`。
- [x] 每个评分项可追溯到 JD 证据与简历证据。
- [x] Agent Trace 对 UI 展示脱敏，不暴露原始 JD / 简历文本。
- [x] `Integrity Guard` 阻止无证据指标与夸大职责。
- [x] 评分确定性，全部测试通过。
- [x] `/api/capabilities` 正确反映当前已上线能力。
- [x] 后端单独 Docker（与 postgres）可启动并通过 healthcheck。

### 全栈

- [x] 前后端联调走通主路径；报告页所有数据来自真实后端。
- [x] 全栈 Docker Compose 可启动 frontend、backend、postgres。
- [x] README 说明两种运行方式与 Phase 1 双验收门。

---

# autoplan 审查报告（2026-05-03）

> 本节由 `gstack:autoplan` 流水线写入，包含 Phase 1（CEO）/ Phase 2（Design）/ Phase 3（Eng）/ Phase 4（最终批准门）四个阶段的产出。CEO 模式为 **HOLD SCOPE**（CLAUDE.md 显式约束）。所有审查不修改代码，只产出决策与待确认项。

## Phase 0 系统审计快照

- 仓库基线：commit `2d87b46`，分支 `main`，工作树干净。
- **代码状态：绿地。** 仅有 `CLAUDE.md`、`TODOS.md`、`docs/`，没有 `frontend/`、`backend/`、`docker-compose.yml`、`Dockerfile`。所有 T1–T13 都从 0 开始。
- 已就位文档基线：`CLAUDE.md`、`TODOS.md`、`docs/DESIGN.md`、`docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`、`docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md`、`docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md`、外部副本 `~/.gstack/projects/Newproject2/main-test-plan-2026-05-02-careerfit-agent.md`。
- Restore point：`/c/Users/qwer/.gstack/projects/Newproject2/main-autoplan-restore-20260503-032137.md`。
- Codex 双声可用（auth probe = AUTH_OK）。

## Phase 1 — CEO 审查（HOLD SCOPE）

### D1 前提门：已通过

用户选择 A）锁定双门：前端完整功能网站 + 后端主路径 MVP。后续所有审查在此前提下展开，不再讨论"是否改回单门 MVP"。

### 0B 既有代码地图

- 既有：仅文档，无代码、无依赖、无构建产物。
- 含义：本计划没有遗留兼容包袱，但也意味着 13 个任务全部是"从零搭建"，前端骨架（Vite + Vue Router + Pinia + Vitest）必须先到位，否则后续任何 TDD 都跑不起来。
- 风险：T1（脚手架）一旦延迟，T2–T7 全部阻塞。HOLD SCOPE 不允许新增任务，但要求 T1 内部"先把骨架跑通"必须独立可验证（`npm run dev` + `npm test` 都通过）。

### 0C 梦想态 vs 当前态（HOLD SCOPE 下的 delta）

在 HOLD SCOPE 范围内，10 分版的 Phase 1 是：

- 13 条路由都能渲染真实空状态，且每个页面对自己的"等待后端 X"原因有明确文案（不是统一占位）。
- 报告页的证据展开是强对照视觉：JD 证据高亮 + 简历证据高亮，可以一眼看到匹配。
- Agent Trace 时间线不仅有节点名，每个节点能展开到"输入摘要 / 输出摘要 / 失败原因"。
- 后端 Integrity Guard 不仅做关键词阻断，还做"是否能从证据集合中回溯"的二次校验。
- 评分原始因子（`raw_factors`）能在前端"调试模式"下被复现，便于自审。

当前计划与 10 分版 delta：

- ✅ 13 条路由 + 状态机 + `BackendNotReadyNotice`：T1+T3–T5 已覆盖。
- ✅ 报告证据展开：T4 + DESIGN.md `EvidenceCard` 已覆盖。
- ⚠️ 节点输入/输出摘要可能停留在"节点名 + 状态"，未显式要求展开摘要。**建议在 T11 (Agent Trace 脱敏) 内部 checklist 增加一项："对外响应包含 input_summary 与 output_summary 字段，长度受限"**。
- ⚠️ Integrity Guard 二次校验未写明。**建议在 T9 内部增加"验证步骤 4：从证据集合中回溯 LLM 改写后的所有事实声明"**。
- ⚠️ 调试模式复现 `raw_factors`：DESIGN.md 已留 hook，但 T8/T11 未写明。**Phase 2+ 延后即可，记录到 TODOS.md**。

### 0D 模式分析（已锁 HOLD SCOPE）

CLAUDE.md 明文：plan-ceo-review 必须以 HOLD SCOPE 调用。所有"扩大范围"提议本节不允许；"缩减范围"提议也不允许（双门已是用户已确认范围）。本节只做：bulletproof + 找雷 + 暴露 taste 决策。

### 0E 时间深度（5–10 年视角下的 Phase 1 不可逆决策）

- 数据模型（`analysis_tasks` / `analysis_reports` / `agent_runs` 的 JSON schema）：一旦写入生产数据，未来迁移成本高。**必须在 T8 落库前确认 schema_version 字段在所有 JSON 列上存在，且校验函数能拒绝缺字段的旧数据**。
- 评分公式：一旦报告对外发布，用户对分数会建立心理基线，后续调整公式会让历史报告失去可比性。**必须把"评分公式版本号"和分数一起持久化（已在计划中），并把版本号显示在前端报告页**（T4 内部 checklist 应加一行）。
- 隐私边界：localStorage 白名单一旦放宽（例如某个未来功能"想缓存简历摘要"），就很难收回。**T6 必须把白名单实现为 const，新增字段必须通过 PR review，不能运行时动态扩展**。

### 0F HOLD SCOPE 模式确认

模式 = HOLD SCOPE。后续审查不会提出"加上 PDF 解析"、"加上多用户"、"加上面试评分闭环"等扩展。这些已在 TODOS.md 的 Phase 2+ 延后区。

### CEO 审查关键结论（Voice 1：Claude HOLD SCOPE）

#### 五大潜在雷区

1. **后端 LangGraph "兼容边界" 退化为永远不替换的本地 runner**
   - 位置：T8/T9/T10 任务集合。
   - 问题：`CLAUDE.md` 允许 LangGraph 先用兼容 boundary，但若不在每个 Agent 节点接口处显式声明 `def __call__(state) -> state` 的 LangGraph 节点签名，半年后会发现根本无法切换。
   - 修复：T8 落地 Agent 接口时，每个节点必须实现 LangGraph 兼容签名；本地 runner 仅是调度器实现，节点本身就是 LangGraph node。在 T11 加一条 checklist："本地 runner 与 LangGraph 切换路径有 ADR 注释"。

2. **`/api/capabilities` schema 被 hard-code，前端硬解析**
   - 位置：T8 + T1 `availability` store。
   - 问题：测试计划写明缺失字段 fallback `pending`，但若前端仅用 `response.capabilities.jobs.list === 'ready'` 这种点路径访问，schema 演化会破坏前端。
   - 修复：前端 `availability` store 必须先用 `CapabilitySchema.parse(response)` 校验（zod 或自写），缺字段直接置 `pending`，未知字段允许保留但不影响。后端响应必须含 `schema_version`，前端不识别的版本一律降级为"全部 pending"。

3. **SQLite ↔ PostgreSQL JSON 行为分歧未被显式护栏**
   - 位置：T8 数据层。
   - 问题：单测跑 SQLite，集成测试跑 PostgreSQL，但若 ORM 写入 JSON 时依赖 PostgreSQL `jsonb` 操作符，SQLite 静默通过，集成阶段才炸。
   - 修复：T8 内部增加一条 checklist："JSON 字段访问全部走 ORM 字段层 API（不写原生 JSON 操作符）；任何 native SQL JSON 操作必须有显式 PostgreSQL-only 标记"。

4. **Integrity Guard 误报阻塞合理改写**
   - 位置：T9 服务层 + Agent 层。
   - 问题：当前规则是"无证据指标"被阻断；但简历优化常见的合理改写（被动语态改主动语态，重新组织句子）若被规则误判为"新增事实"，会导致 LLM 输出被反复打回。
   - 修复：Integrity Guard 必须有**白名单测试样例**："只动语序"、"专业术语对齐"、"被动改主动"等都必须通过；同时维护**黑名单测试样例**：编造数字、加入未声明项目、夸大领导规模等必须被阻断。测试计划里 T9 的"5 条不安全简历优化样例"应配套 5 条**安全改写样例**，对照测试。

5. **前端 `BackendNotReadyNotice` 退化为通用占位词，失去信息价值**
   - 位置：T2 共享组件 + T3/T5 视图调用。
   - 问题：若所有后端缺口都用同一个 `feature="工作台" waitingFor="后端"` 的兜底文案，用户感知不到具体阻塞点，调研价值丢失。
   - 修复：T2 在 `BackendNotReadyNotice` 上增加 `feature` 与 `waitingFor` 必填校验（运行时 props validator + 测试用例）；T3–T5 调用时必须填具体能力名（如 `feature="历史趋势" waitingFor="analyses.history 接口"`），不允许通用占位。

#### 三条 taste 决策待确认（Phase 4 终批门统一摆出）

- **T1 之前是否引入 UI 组件库**：候选 Reka UI / Radix Vue / 纯手写。当前 TODOS.md 标"待定"。
- **HistoryView 图表库**：Chart.js vs ECharts。
- **后端 SQLAlchemy 是否全异步**：影响 FastAPI 路由签名与依赖注入风格。

#### 失败模式登记（Failure Modes Registry）

- LLM 返回非法 JSON 连续两次：节点标记 failed，工作流标记任务 failed，前端报告页渲染 `failed` 状态而非半成品。
- RAG 召回错域文档（如查询 LLM 工程师却返回 React 标准）：评分必须降级到"知识库证据不足"，而非沿用错文档生成结论。
- 前端 localStorage 缓存了过期 capability 状态：`availability` store 启动时强制重新探测，不信任缓存。
- capability 在用户操作中途从 `ready` 翻 `pending`（如后端重启）：当前视图必须立即切换到 `BackendNotReadyNotice`，已在途的请求必须可取消或忽略响应。
- Integrity Guard 对合法改写误报：必须能用证据集合二次校验"是否所有事实都能从证据回溯"，否则阻断 + 提示用户而非自动放行。
- Agent Trace 脱敏漏字段：原始 JD/简历文本若漏过滤，会通过 trace API 泄露。**必须有"脱敏输出 vs 原始输入"的 diff 测试**：原始内容片段不得在响应中出现。
- 移动端键盘弹起遮挡输入框：T6/T7 必须有 480px 断点的真机或模拟器走查（不仅仅是 viewport 缩放）。
- 浏览器禁用 localStorage：所有偏好读写走内存 fallback，不抛异常，下次刷新重置（已在测试计划中覆盖，需复核实现真的有 try/catch）。

#### 错误与救援登记（Error & Rescue Registry）

| 错误源 | 触发场景 | 用户感知 | 系统救援 |
|---|---|---|---|
| 网络 5xx / 超时 | 任意 fetch 失败 | 视图切换 `error` 态，含"重试"按钮 | 指数退避 1 次重试，仍失败 → 显式报错 |
| 后端 4xx（参数错） | 表单提交校验通过但后端拒收 | 表单字段下方 inline error 文案 | 不重试；记录错误码以便排查 |
| LLM 非法 JSON | Agent 节点 LLM 输出无法 parse | Agent Trace 节点 = `retry` 后 `failed` | 至多 1 次修复重试，超过则节点 failed，工作流 failed |
| RAG 检索空 | 查询无相关文档 | 报告对应维度标"知识库证据不足" | 不编造来源；评分降级 |
| Integrity Guard 阻断 | 简历改写有无证据事实 | 报告"简历建议"区域显示风险标签 + 文字 + 跳转证据 | 阻断 LLM 输出，要求重写或保留原文 |
| capability 翻 pending | 后端节点重启 / 健康检查失败 | 视图立即切换 `BackendNotReadyNotice` | 无；用户感知后由用户手动刷新或自动重探 |
| 浏览器 localStorage 不可用 | 隐身模式 / quota 满 / 拒绝访问 | 用户偏好仅本会话内有效 | 内存 fallback；console.warn；不抛未捕获异常 |
| 浏览器 IndexedDB 失败 | 同上 | 同上 | 走 localStorage fallback |
| 路由匹配失败 | 用户输入未知路径 | `NotFoundView` + 返回工作台按钮 | 无；纯前端处理 |
| Docker 启动失败 | 端口冲突 / postgres 卷损坏 | README 给出排错命令 | 文档化诊断步骤；不静默降级 |

### NOT in scope（确认延后到 Phase 2+）

下列项已在 TODOS.md，CEO 审查再次确认 HOLD SCOPE 不动：

- 真实账号、登录、注册、多租户、SSO。
- HR 候选人筛选、导师/管理员看板。
- PDF/DOCX 简历解析、Markdown 简历导入。
- 后台 worker（Celery / RQ / Arq）、多模型路由、面试回答评分闭环、每周进展总结。
- 简历/报告 PDF 导出、协作分享只读链接。
- i18n、PWA、富文本编辑器、深度主题自定义。
- 生产部署（K8s/灰度/蓝绿）、监控仪表盘、CI/CD 全链路、镜像签名/SBOM。

### 已在文档中显式存在的支撑（avoid duplicate work）

- Phase 1 验收门两套：`CLAUDE.md` 已写定（前端 Phase 1.A + 后端 Phase 1.B）。
- 决策点清单：`TODOS.md` "决策点（不允许静默选）"。
- 测试矩阵：`docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md` 与外部副本同步。
- 视觉 token：`docs/DESIGN.md`。

### CEO Voice 2（codex）

codex 输出原文：`/c/Users/qwer/.gstack/projects/Newproject2/autoplan-runs/ceo-codex-output.txt`

#### 前提验证

双门前提成立的前提是：前端 Phase 1.A 必须把"后端缺失"当作一等运行时状态，而非视觉占位阶段。具体风险是：在主路径还没证明"确定性评分 + 证据链 + Integrity Guard + 可追踪"之前，前端"完整性"会漂移成 mock-product 假象。

#### 五大潜在雷区

1. **`Backend Phase 1.B / 确定性评分`**：若 LLM 抽取、归一化、Agent 重试影响评分输入，分数确定性会破。修复：把评分锁定为对持久化"标准化件"的版本化纯函数，LLM 输出仅作为证据输入，不能进入打分公式。
2. **`evidence-chain 报告`**：若报告生成阶段信任早期 pipeline 创建的引用，证据链校验可被绕过。修复：每条对外展示的论断必须在**报告组装之后**对照存储的 source span 重新校验。
3. **`Integrity Guard prompt`**：若 Guard 收到完整简历/JD 私有上下文，prompt 可能泄露或被改写禁项。修复：传入 Guard 的 payload 最小化（只传 claim/action），Guard 决策日志与 source evidence 分离。
4. **`Frontend / capability readiness`**：若前端把路由行为硬编码到后端 readiness flag 上，schema 演化会破。修复：定义版本化 capability 契约，含 ready/pending/missing/stale 四态及其测试。
5. **`持久化 fixture 测试`**：SQLite/Postgres 在 JSON 排序、null、数值强转、JSON path 查询上行为分歧。修复：要么 Phase 1 锁单库，要么 fixture 测试证明两者持久化的 analysis artifact 完全一致。

#### 三条 taste 决策待确认（产品形态层）

1. **产品调性：分析师工作台 vs 引导式向导**。当前默认是 13 条完整路由 + 多套状态机；替代是单一线性主路径流 + 二级检查视图。建议：保留 13 路由的前提是导航不掩盖 Job → Resume → Analysis → Report → Next Best Action 的主轴。
2. **评分呈现：数字优先 vs 证据优先 vs 建议优先**。当前默认确定性数字 + 证据链；替代是先以"证据支撑的匹配区间"展示，精确数字次级显示。建议：证据优先，因为应届生会过度信任精确分数。
3. **Agent Trace 展示密度**。当前默认 Trace 是 MVP 主路径的一部分；替代是默认显示精简 trace，原始步骤可展开。建议：默认精简，否则产品读起来像调试输出。

#### codex 失败模式（合入主登记表）

- LLM JSON parse 连失两次时后端没存任何 partial artifact，前端会无限 loading 而不是显式可恢复错误。
- RAG 返回错域文档，报告引用看似合理但其实无关。
- Resume parser 把项目误判为工作经验，膨胀资历匹配度。
- JD 含 prompt 注入并到达 analysis / guard / next-best-action 任一阶段。
- 确定性分数在 Agent 重试后变化，因技能别名归一化结果不一致。
- 文本清洗后 evidence span 偏移漂移，导致引用指错句子。
- Integrity Guard 误报 → 阻断合理改写。
- Integrity Guard 漏报 → 放行无证据的"你已具备资格"语句。
- 前端 localStorage 缓存了过期/损坏的 capability，遮蔽刚就绪的后端能力。
- capability 在用户操作中途从 ready 翻 pending，丢失用户已输入内容。
- BackendNotReadyNotice 在已完工前端路由上变成主导 UX，让 Phase 1.A 看起来像坏的。
- Partial analysis 状态被渲染成"完整"，因为某个下游 artifact 存在了就被当作完成。
- Agent Trace 日志写入了应当只在 evidence-bound 上下文中出现的简历敏感文本。
- 错误态视觉测试通过但键盘恢复路径失败。
- 响应式布局通过宽度快照但在长公司名/技能名/文件名下溢出。

#### codex Dream state delta

固定范围内，达到 10/10 不是加功能，而是各阶段之间更严格的"信任契约"：什么能被持久化、被打分、被引用、被守卫、被追踪、被缓存、在不完整时如何展示，都必须有更尖锐的不变式。10/10 版本必须让产品**无法被误认成 mock demo**：每条路由真实反映后端能力，每个分数可复现，每条论断有证据绑定，每个 Guard 决策可解释，每个 partial/failed 态都给出稳定的 next action。

### CEO 共识表（Voice 1 vs Voice 2）

| 维度 | Voice 1 (Claude HOLD SCOPE) | Voice 2 (codex HOLD SCOPE) | 合并结论 |
|---|---|---|---|
| 前提是否成立 | ✅ 双门合理 | ✅ 成立但有"mock 假象漂移"风险 | **合并：双门成立，但 BackendNotReadyNotice 不允许成为任何核心视图的主导 UX** |
| 评分确定性 | 雷区 #1 间接：评分公式版本号上前端 | 雷区 #1：LLM 输出禁止进入打分公式，仅作为证据 | **合并：评分锁版本号 + LLM 严格隔离打分通道。T9 加约束："LLM 抽取产物归一化后才入打分；归一化函数版本号与分数一起持久化"** |
| 证据链校验时机 | 未单独抓出 | 雷区 #2：组装后再校验 | **采纳 Voice 2：T10 在报告组装后插入"逐论断 vs source span"重校验步骤** |
| Integrity Guard 输入边界 | 未单独抓出 | 雷区 #3：Guard 只接收 claim/action 最小 payload | **采纳 Voice 2：T9 Guard 接口签名限制为 minimal claim payload，禁止传完整简历/JD** |
| LangGraph 兼容退化 | Voice 1 雷区 #1：节点必须实现 LangGraph 签名 | 未单独抓出 | **采纳 Voice 1：T8 每个 Agent 节点实现 LangGraph 兼容签名 + ADR 注释切换边界** |
| capabilities schema 韧性 | Voice 1 雷区 #2：schema 校验 + schema_version | Voice 2 雷区 #4：版本化契约 + ready/pending/missing/stale 四态 | **合并：T1 `availability` store 用 schema 校验，含四态测试；后端 schema_version 不识别就降级全 pending** |
| SQLite/Postgres JSON 分歧 | Voice 1 雷区 #3：禁原生 JSON 操作 | Voice 2 雷区 #5：fixture 对比测试或锁单库 | **合并：T8 禁用原生 JSON 操作符 + 集成测试用 PostgreSQL 跑 fixture 比对，SQLite 仅做单元测试**（与 TODOS.md 决策一致） |
| Integrity Guard 误报/漏报 | Voice 1 雷区 #4：白+黑名单测试样例 | 失败模式 #7+#8：双向都要测 | **合并：T9 同时维护 5 条安全样例（必通过）+ 5 条不安全样例（必阻断）+ 5 条边界样例** |
| BackendNotReadyNotice 退化 | Voice 1 雷区 #5：必填 props 校验 | 失败模式："变成主导 UX 让前端像坏的" | **合并：T2 强制 feature/waitingFor 必填 + T3-T5 调用必须填具体能力名；增设"主导 UX 警戒线"——若工作台或报告整页都是该组件，文案必须升级为"系统未上线"级引导切 frontend-only 模式** |
| 失败模式：JD prompt 注入 | 未抓 | 抓到 | **采纳 Voice 2：T9 在 JD 解析、Guard 输入、Next Best Action 三处加 prompt 注入防护测试** |
| 失败模式：技能别名归一化破坏分数稳定 | 未抓 | 抓到 | **采纳 Voice 2：T9 归一化函数版本化，重试不重新归一化，使用首轮归一化结果** |
| 失败模式：evidence span 偏移漂移 | 未抓 | 抓到 | **采纳 Voice 2：T8 简历/JD 文本清洗后必须保留原文 + offset 映射；引用按"清洗后偏移"存储，展示时映射回原文** |
| 失败模式：partial 被当完整 | 未抓 | 抓到 | **采纳 Voice 2：T8 任务状态机仅在所有下游 artifact 都就绪时才置 success；任一缺失即 partial 或 failed** |
| 失败模式：Agent Trace 日志泄露 | Voice 1 提到 trace 脱敏 + diff 测试 | 重叠 | **合并：T11 trace 脱敏函数 + "原文 vs 响应"diff 单测必须覆盖** |
| 失败模式：长字符串溢出 | 未抓 | 抓到 | **采纳 Voice 2：T7 响应式测试除 viewport 宽度外加极端字符串测试（80 字符公司名 / 30 字符技能名 / Unicode 表情）** |
| 失败模式：错误态键盘恢复失败 | 暗示但未单列 | 抓到 | **采纳 Voice 2：T7 axe-core 之外加键盘从错误态恢复测试** |
| 产品形态 taste：13 路由 vs 线性向导 | 未提（Voice 1 是技术 taste） | 提了 | **进入 Phase 4 终批门作为产品 taste 决策** |
| 产品形态 taste：数字优先 vs 证据优先 | 未提 | 提了 | **进入 Phase 4 终批门** |
| 产品形态 taste：trace 密度 | 未提 | 提了 | **进入 Phase 4 终批门** |
| 技术 taste：UI 库 / 图表库 / SQLAlchemy 异步 | 提了 | 未提 | **进入 Phase 4 终批门** |

### CEO 阶段产出汇总

- 前提：✅ 双门，已 D1 确认。
- 模式：✅ HOLD SCOPE，CLAUDE.md 强制。
- 五大雷区：上方列出，将进入 Phase 4 终批门作为"用户挑战"项。
- 三条 taste 决策：UI 库 / 图表库 / SQLAlchemy 异步 — 进入 Phase 4。
- Failure Modes Registry + Error & Rescue Registry：上方表格。
- 决策审计追加：见下方"决策审计 trail"。

## Phase 2 — Design 审查

> 设计审查仅做信息性输出（CLAUDE.md：plan-design-review 非强制门）。但本节有一个**必须修**项，已上升为阻塞。

### Design Voice 1（Claude）

#### 必须修：DESIGN.md 与 CLAUDE.md 移动端约束直接冲突

- **冲突点**：
  - `docs/DESIGN.md` 响应式表（line 540）："Mobile 480 px：报告页保证可读，Phase 1 不要求完整布局"。
  - `docs/DESIGN.md` 已知缺口 #3（line 578）："移动端复杂布局：Phase 1 仅保证报告页 480 px 下可读，工作台高级响应留待 Phase 2"。
  - `CLAUDE.md` 前端实现约束："完整响应式：桌面、平板、移动端三套断点都达标，移动端不再仅'保证报告可读'，工作台与所有核心页面都必须可用"。
  - 测试计划 1440/1280/1024/768/480 五档全部要求工作台、报告、Jobs、Resumes、Settings、HistoryView 都可用。
- **结论**：CLAUDE.md 优先（DESIGN.md 顶部已声明"当本文件与项目根目录 CLAUDE.md 冲突时，以 CLAUDE.md 为准"）。
- **修复**：DESIGN.md 响应式表 480 px 行改为"工作台、报告、Jobs、Resumes、Settings 全部可用，单列布局，导航折叠为底部 tab"；已知缺口 #3 删除或改为"移动端键盘弹起遮挡尚未验证（T6/T7 落地时再决议）"。
- **任务归属**：在实施前修 DESIGN.md，避免 T7 实现时按 DESIGN.md 旧值落地，验收门挂掉。

#### 设计维度审查（HOLD SCOPE）

| 维度 | 状态 | 备注 |
|---|---|---|
| 视觉系统 token 完备 | ✅ | 颜色/排印/布局/深度/形状均有，Linear 风格一致 |
| 组件契约清晰 | ✅ | NextBestAction、ScoringOverview、EvidenceCard、SuggestionCard、IntegrityGuardBanner、AgentTrace 都已定义 |
| 风险双通道（色 + 文字） | ✅ | DESIGN.md "Don't" 节明文禁单通道 |
| Next Best Action 显眼位 | ✅ | 工作台首屏顶部 + 报告页头部，必有 |
| Agent Trace 脱敏 | ✅ | "禁止在 UI 层渲染节点的原始输入/输出原文" |
| 信息层级（hierarchy as service） | ⚠️ | 工作台首屏未明确"目标岗位 + 简历版本 + Next Best Action"三件套的视觉权重比例。建议 T3 落地时给出三件套的栅格分配（如 4:4:4 或 6:3:3） |
| 空/加载/错误/部分数据状态 | ⚠️ | DESIGN.md 描述了 Next Best Action "无可执行行动" 状态，但其他卡片的四态视觉规范没有显式给出。建议 T2 共享组件实现时同时定义四态视觉变体（loading skeleton、empty illustration、error 文案 + 重试按钮、partial 标识） |
| 响应式 | ❌ | 与 CLAUDE.md 冲突，见上方"必须修" |
| 触摸目标 ≥ 44px | ✅ | 已写明 |
| 折叠策略 | ✅ | 1024 / 768 断点的导航/Trace/证据折叠规则齐全 |
| 颜色对比 WCAG AA | ✅（暗色主题 + 高对比 ink） | 实施时仍需 axe-core 复核 |
| 动效 200–300ms | ✅（计划与测试明文） | DESIGN.md 未单独描述动效曲线，建议补一个 token 段（cubic-bezier(0.16, 1, 0.3, 1) 或类似） |
| `prefers-reduced-motion` | ✅ | 测试计划要求遵守，DESIGN.md 未单独提及，建议 T6 落地时显式写入 |
| 中文版式 | ✅ | "display 用负字距，body 用 0 字距以兼容中文" |

#### 三条 Design taste 决策（与 CEO Voice 2 部分重合）

1. **报告页主轴：分数优先 vs 证据优先**（与 CEO Voice 2 重合）。视觉建议：证据先呈现，分数次级；理由：应届生过度信任精确分数。
2. **Agent Trace 默认密度**（与 CEO Voice 2 重合）。视觉建议：默认显示"节点名 + 状态 + 耗时"三列，其余字段（输入/输出摘要、错误）默认折叠；点击行展开。理由：避免"调试日志感"。
3. **空状态插画 vs 纯文案**：当前 DESIGN.md 未指定。Phase 1 建议：纯文案 + 引导 CTA（无插画）；理由：插画需要美术资源，HOLD SCOPE 内不引入；文案设计成本低。

#### Design 审查结论

- 1 项必须修（DESIGN.md 移动端约束与 CLAUDE.md 冲突）。
- 4 项建议补强（首屏栅格、四态视觉变体、动效曲线 token、prefers-reduced-motion 显式化）。
- Design Voice 1（Claude）单声完成；本项目 Design 不强制双声（gstack 设计不要求 codex 复审），跳过 Voice 2。


## Phase 3 — Eng 审查

### Voice 1（Claude）— Eng 单声分析

#### 架构风险（Top 5）

1. **T1 脚手架阻塞关键路径**
   - 问题：仓库 greenfield，只有文档；Vue3 + Vite + TS 脚手架（T1）一旦延迟或返工，T2 的共享组件 TDD、T3 的工作台、T4 的报告视图全部停滞，前端 Phase 1.A 整条链都被堵住。
   - 修复：T1 必须在 1 个 work session 内完成并 commit，且 `npm test` 跑空跑通；T2 的第一个组件（建议 `AppButton`）作为脚手架冒烟用例，用来验证 vitest + jsdom + @vue/test-utils 链路。

2. **LangGraph 节点签名漂移**
   - 问题：CLAUDE.md 与 TODOS.md 决策点都允许"先用本地顺序 runner，后续替换 LangGraph"，但若节点签名不统一，"兼容边界"会成为永久债务，最终重写 7 个 Agent。
   - 修复：在 T8 之前先固定 `AgentNode` 协议（`(state: GraphState) -> NodeOutput`），所有节点（Parser/RAG/Scoring/Gap/Optimizer/IntegrityGuard/ReportComposer）必须实现该协议；写一份 ADR（`docs/adr/0001-langgraph-boundary.md`）说明替换 LangGraph 的边界条件与回退路径。

3. **Pydantic schema_version 与 JSON 列演进**
   - 问题：`analysis_tasks`、`analysis_reports`、`agent_runs` 三表使用 JSON 列，schema 必将演进；但当前计划没有 schema 迁移策略，旧记录在演进后会无法反序列化。
   - 修复：所有 JSON payload 顶层强制带 `schema_version: str`；定义读时迁移钩子 `migrate_payload(version, payload) -> latest_payload`；写测试覆盖 v1→v2 反序列化路径；DB 迁移测试在每次 schema_version 升版时跑一次。

4. **Evidence span 偏移在文本清洗后失效**
   - 问题：JD/简历输入会经过 normalize（去重换行、统一全半角、剔除控制字符），证据 span 若仅记录 normalized offset，UI 高亮会偏移；若仅记录 raw offset，二次解析会失败。
   - 修复：`Evidence` schema 必须同时持久化 `raw_text_hash`、`normalized_text_hash`、`raw_offset(start,end)`、`normalized_offset(start,end)`、`quote_snapshot`（冷快照）；解析器输出双坐标，UI 用 raw offset，后端复算用 normalized offset。

5. **`/api/capabilities` 四态契约缺失**
   - 问题：当前 schema 只定义 `ready | pending` 两态，但实际运行时需要区分：`ready`（可用）、`pending`（任务进行中）、`missing`（后端未实现）、`stale`（schema_version 不匹配）。前端无法精细区分将退化为粗暴占位，损害 UX。
   - 修复：capability 状态扩为四态枚举；前端 `availability` Pinia store 显式映射四态到 UI 行为（`ready` → 真实数据、`pending` → 加载占位、`missing` → BackendNotReadyNotice、`stale` → 强制刷新提示）；后端响应缺失字段必须 fallback 为 `missing`。

#### 测试计划缺口（vs targets）

对照 codex 列出的 10 个目标，本仓库测试计划当前覆盖：

| 目标 | 当前覆盖 | 缺口 |
|---|---|---|
| 评分公式 property-based 测试 | 仅有 clamp/最低分 unit | 缺 monotonicity、weight 异常、维度排列扰动属性测试 |
| 分析任务并发创建 | 无 | 全缺：同 user + 同 jobId + 同 resumeId 重复提交、并发提交去重 |
| schema_version 迁移测试 | 无 | 全缺：v1→v2 反序列化、未知 version 回退 |
| 前端 availability 缓存陈旧检测 | 无 | 全缺：浏览器后台 30min+ 后切回的 stale-cache 重探测试 |
| 中途 capability 翻转 UX | 仅文字描述 | 缺组件级 + store 级测试：从 ready→pending 时 UI 立即收回功能 |
| 长字符串视觉溢出 | 无 | 全缺：超长公司名/技能别名/JD 段落在 480/768/1024 三档的截断与省略 |
| 错误态键盘恢复 | 仅 ARIA 描述 | 缺 e2e：Tab→Enter 重试、Esc 撤销错误 toast、focus 恢复 |
| JD/简历 prompt injection | 无 | 全缺：JD 中嵌入"忽略以上指令"等指令性文本，验证 Parser/Guard 不被劫持 |
| Evidence span 偏移在清洗后保留 | 无 | 全缺：raw 与 normalized 双坐标 round-trip |
| 技能别名归一化确定性 | 无 | 全缺：大小写、标点、重复、排序扰动后输出稳定 |

#### 测试层次图

```text
unit (vitest / pytest)
├─ frontend
│  ├─ AppButton/RiskPill/EvidenceCard 等组件契约
│  ├─ useLocalStorageRef PII 白名单
│  └─ availability Pinia store 四态机
├─ backend
│  ├─ 评分公式（property-based + 边界）
│  ├─ Integrity Guard 黑/白名单矩阵
│  ├─ Parser 输出 Pydantic schema 校验
│  └─ schema_version 迁移钩子
            ↓
service (pytest + fakes)
├─ AnalysisService.create_task（并发去重）
├─ AnalysisService.run（节点编排 + retry 上限）
├─ AgentRunner（LangGraph adapter 边界）
└─ ReportComposer（证据链装配）
            ↓
integration (pytest + sqlite & postgres docker)
├─ sqlite：单元测试 default backend
├─ postgres：JSON 查询、UUID、时间戳行为差异覆盖
└─ pgvector：知识库 embedding round-trip
            ↓
e2e (playwright + docker compose)
├─ docker compose -f docker-compose.frontend-only.yml
│  └─ 13 路由 + BackendNotReadyNotice + 移动端 480/768
└─ docker compose up
   └─ 主路径 10 步 + 模式切换 11/12 步 + 关键路径回归
```

#### T1–T13 依赖图与关键路径

```text
                                       ┌──────────────────────────┐
                                       │        前端 Phase 1.A     │
                                       └──────────────────────────┘
T1 (前端脚手架 + 13 路由)
  └─→ T2 (共享组件 TDD)
       ├─→ T3 (工作台 + Jobs + Resumes)
       │    └─→ T4 (分析提交 + 报告视图)
       │         └─→ T5 (周边视图：HistoryView/VersionDiff/Learning/AgentTrace)
       │              └─→ T6 (本地偏好 + PII 白名单)
       │                   └─→ T7 (Frontend-only Docker + UX 抛光门)
                                       ┌──────────────────────────┐
                                       │        后端 Phase 1.B     │
                                       └──────────────────────────┘
T8 (FastAPI 骨架 + DB 模型 + capability 契约)
  └─→ T9 (Parser + RAG + Scoring + Gap)
       └─→ T10 (LangGraph adapter + Integrity Guard + ReportComposer)
            └─→ T11 (Agent Trace 持久化与脱敏)
                                       ┌──────────────────────────┐
                                       │        全栈集成           │
                                       └──────────────────────────┘
T7 + T11 ──→ T12 (docker-compose.yml 全栈 + 种子知识库 + 主路径冒烟)
              └─→ T13 (README 中文 + 关键路径回归 + 验收门 checklist)

关键路径（前端串行）：T1 → T2 → T3 → T4 → T5 → T6 → T7 → T12 → T13
关键路径（后端串行）：T8 → T9 → T10 → T11 → T12 → T13
最长路径：max(前端, 后端) → T12 → T13
T1 + T8 可在 work session 0 并行；T7 与 T11 必须都完成才能进入 T12。
```

#### 决策点（需在 Phase 4 由用户拍板）

| # | 决策 | 默认（codex Voice 2 推荐） | 备选 | 理由 |
|---|---|---|---|---|
| Eng-1 | SQLAlchemy 异步 vs 同步 | 同步（Phase 1） | 全异步 | greenfield SQLite/Postgres 测试更简单；FastAPI 路由可用 sync def；T8 之前如无流式/高并发需求，避免 async 复杂度 |
| Eng-2 | Agent trace 持久化策略 | 服务端原始快照 + 对外脱敏响应分离 | 直接嵌入 API 响应 | trace schema 演进比响应需求快，分离避免前端被迫升级；与 CLAUDE.md 隐私约束一致 |
| Eng-3 | Evidence 偏移坐标 | 同时持久化 raw + normalized | 仅 normalized | normalized-only 会破坏审计；双坐标支持 UI 高亮 + 后端复算 |
| Eng-4 | LangGraph 类型在 domain 层 | adapter-only（不外漏） | 服务层透传 graph state | 保留可替换性；与 CLAUDE.md "保留 LangGraph 切换边界"一致 |
| Eng-5 | Capability 契约版本化 | 带 schema_version + 四态枚举 | 无版本化布尔 | 未来 capability 翻转和新 agent 能力都需要确定性 UX；前端必须能识别 stale 与 missing |
| Eng-6 | 测试 DB 策略 | 双轨：单测用 SQLite，集成测试用 Postgres docker | 仅 Postgres | TODOS.md 已记录该决策；codex Voice 2 与本仓库一致；保留以便 Phase 4 最终确认 |

#### 缺失的 telemetry / observability（greenfield 基线）

- **后端结构化日志**：分析任务创建/执行/失败的 request_id、analysis_id、duration、retry_count、failure_node。
- **后端 metrics**：分析任务 P50/P95 延迟、scoring clamp 触发次数、Integrity Guard 拦截次数、LLM 非法 JSON 修复重试次数。
- **后端 trace span**（OpenTelemetry 兼容即可）：parser → RAG → scoring → agent run → persistence；每段独立 span，便于排查瓶颈。
- **capability 契约审计日志**：每次响应的 schema_version、enabled capabilities、生成来源（直接配置 vs 任务推导）。
- **capability 翻转计数**：会话期内从 ready 翻到 pending/missing 的次数（暗示后端不稳定）。
- **Evidence 完整性 metric**：raw hash mismatch、normalized hash mismatch、offset validation failure 三种异常的累计计数。
- **前端 telemetry（轻量）**：availability stale-cache 命中、错误态重试、disabled 按钮误点击；用 sendBeacon / fetch keepalive 异步上报，不阻塞渲染。
- **Prompt-injection 检测计数**：JD/Resume 解析器与 Guard 节点检测到指令性文本时计数（不发完整原文，只发 fingerprint）。

> Greenfield 阶段建议从最小集开始：结构化日志（已含 request_id）+ scoring/integrity guard metric counter + parser→agent→persistence 三段 trace span。其余在 Phase 2 引入 OpenTelemetry collector 后启用。

### Voice 2（codex）— Eng 复审

> 完整原文见 `~/.gstack/projects/Newproject2/autoplan-runs/eng-codex-output.txt`。下方是关键摘要。

#### codex 的 5 项架构风险

1. 层边界漂移（route → service → scoring → agent → RAG），契约定义滞后。
2. Pydantic 宽松（无 `extra="forbid"`、无 strict types、无 discriminated union）。
3. async/sync DB 混用阻塞分析任务创建。
4. LangGraph 内部类型泄漏到 API 响应与持久化形态。
5. Evidence span 在文本 cleanup 后失效（需 raw + normalized 双坐标 + cleanup map）。

#### codex 测试缺口（10 项）

property-based 评分、并发分析任务、schema_version 迁移、前端 stale cache、capability flip 中途、长字符串溢出、错误态键盘恢复、prompt injection、evidence span round-trip、skill alias 归一化。

#### codex 决策点（5 项）

- async 还是 sync DB → 同步
- 持久化完整 trace 还是只存响应摘要 → 分离持久化
- evidence offset 用 raw 还是 normalized → 都存
- LangGraph 类型在 domain 层 → adapter-only
- capability 契约版本化 → 是

#### codex telemetry 缺失（10 项）

涵盖：task creation 结构化日志、并发冲突 metric、parser→agent→persistence 三段 trace、scoring clamp/evidence 异常 metric、capability 契约审计、capability flip 计数、trace 持久化审计、evidence 完整性 metric、前端 stale-cache + 错误恢复 + disabled-click telemetry、prompt-injection counter。

> codex 在 Windows sandbox 下 PowerShell `Get-Content` 多次失败（错误 1920），但 fallback 单文件读取后产出完整审查；输出可信。

### Eng 共识表

| # | 维度 | Voice 1（Claude） | Voice 2（codex） | 合并结论 |
|---|---|---|---|---|
| 1 | 架构风险 #1 | T1 脚手架阻塞关键路径 | 层边界漂移 | 两者保留：Voice 1 关注调度风险，Voice 2 关注接口契约风险，互补。先稳定 T1，并行起草 DTO/service command/agent tool 契约。 |
| 2 | 架构风险 #2 | LangGraph 节点签名漂移 | Pydantic 宽松 | 两者保留：Voice 1 关注 Agent 抽象稳定性，Voice 2 关注 schema 严格性；T8 之前同时落地 ADR + `extra="forbid"` 全量启用。 |
| 3 | 架构风险 #3 | schema_version 迁移钩子 | async/sync DB 混用 | 两者保留：迁移钩子归 T9；async/sync 选型归决策点（Eng-1）。 |
| 4 | 架构风险 #4 | Evidence span 双坐标 | LangGraph 类型外漏 | 两者保留：双坐标归 T9 数据模型；类型隔离归 ADR。 |
| 5 | 架构风险 #5 | capability 四态 | Evidence span 双坐标（与 Voice 1 #4 重叠） | 去重合并：Evidence 双坐标采纳；新增 capability 四态作为独立条目。 |
| 6 | 测试缺口 | 10 项详表（含覆盖标注） | 10 项摘要 | 覆盖一致，Voice 1 表更细，作为权威；Voice 2 措辞作为 acceptance language。 |
| 7 | 测试层次图 | 4 层 + 子条目 | 4 层简化 | 采用 Voice 1 详表，结构与 Voice 2 一致。 |
| 8 | 依赖图 | 前后端双轨 + T1+T8 并行 | 单轨串行 T1→...→T13 | 采用 Voice 1 双轨：与 CLAUDE.md "前端不受后端主路径优先级束缚"一致；Voice 2 单轨忽略了双门约束。 |
| 9 | 决策点 | 6 项（含测试 DB） | 5 项 | 6 项全采纳：codex 5 项 + 测试 DB 双轨。 |
| 10 | telemetry 缺失 | 8 项 + greenfield 最小集建议 | 10 项 | 采用 Voice 1 列表（含最小集） + Voice 2 prompt-injection counter（已并入 Voice 1）。 |

### Eng 审查结论

- 5 项架构风险全部进入 TODOS.md 的"决策记录"或"Phase 1 in-scope"补丁。
- 10 项测试缺口全部追加到 `docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md` 与 gstack 镜像测试计划。
- 6 项决策点带入 Phase 4 最终审批门，由用户最终拍板。
- 关键路径已识别：T1 单点失败 = 前端阻塞；T8 单点失败 = 后端阻塞；T7 + T11 双门是全栈集成入口。
- telemetry 最小集建议：结构化日志 request_id + scoring/integrity counter + parser→agent→persistence 三段 trace span。


## Phase 3.5 — DX 审查（跳过）

判断结论：本项目是面向最终用户（应届生求职者）的应用，不是开发者工具或 SDK，不存在显著 developer-facing 表面。Phase 3.5 DX 审查跳过。

跳过依据：
- gstack `plan-devex-review` 主要校验开发者 onboarding 速度、API 文档质量、错误信息可调试性、SDK ergonomics。
- 本项目 Phase 1 唯一开发者表面是 README 启动指南（T13 已覆盖），无 SDK / Plugin / Public API。
- 跳过经 autoplan 4-phase 流程审查标准允许（"DX 信息性，可按工程判断跳过"）。
- 后续若开放公共 API（Phase 2+），必须重启 DX 审查门。

## Phase 4 — 最终审批门

下列决策点已在 CEO/Design/Eng 三轮审查中识别，进入用户最终审批阶段。Auto-decide 仅适用于已被 codex Voice 2 与 Claude Voice 1 双声一致推荐、且不触碰用户已声明边界的决策。CLAUDE.md 硬边界（不做登录、不做 HR 端、不做多租户、不降级为 Demo）不进入审批，直接保留。

### 待审批决策清单

| 决策 | 默认推荐 | 类型 | 备注 |
|---|---|---|---|
| D1 产品形态 | 13 路由工作台 + 工作台首屏"下一步"卡片 | Taste | 与 CLAUDE.md 工作台优先一致 |
| D2 评分展示 | 评分卡 + 证据并列 | Taste | Design 共识：避免"先看分再看证据" |
| D3 Agent trace 密度 | 折叠摘要 + 展开看完整节点 | Taste | 平衡可信度与认知负载 |
| D4 UI 库 | Reka UI（轻量 headless） | Taste | 仅引入需要的组件，避免设计系统冲突 |
| D5 图表库 | ECharts | Taste | HistoryView 趋势图主力 |
| D6 SQLAlchemy 异步/同步 | 同步 Phase 1 | Taste | codex + Claude 双声一致 |
| D7 Agent trace 持久化 | 原始快照 + 对外脱敏分离 | Taste | 双声一致 + 与隐私约束一致 |
| D8 Evidence 偏移坐标 | raw + normalized 双坐标 | Taste | 双声一致 |
| D9 LangGraph 类型层级 | adapter-only | Taste | 双声一致 + 与 CLAUDE.md 切换边界一致 |
| D10 Capability 版本化 | schema_version + 四态枚举 | Taste | 双声一致 |
| D11 测试 DB 策略 | 双轨：SQLite 单测 + Postgres 集成 | Taste | TODOS.md 已记录 + codex 一致 |
| D12 DESIGN.md 480px 修订 | 随 PR ship | User Challenge | DESIGN.md 与 CLAUDE.md 冲突，必须修；用户审批是否在 T7 子项中完成 |

### 用户挑战（必须用户拍板，不可 auto-decide）

下列项与 CLAUDE.md 硬边界、隐私约束或产品愿景直接相关，必须由用户最终决定：

- **C1**：CEO Voice 1 第 5 项 — `BackendNotReadyNotice` 退化风险。是否同意把"必填 props + runtime 校验"作为 T2 强制门？
- **C2**：CEO Voice 2 第 4 项 — Integrity Guard 误报"你已经被录用"类伪积极结论。是否同意把这类伪积极也纳入黑名单？
- **C3**：Design 共识 — DESIGN.md 480px 与 CLAUDE.md 冲突修订时机。是否随 T1（脚手架）一起做、还是 T7（Frontend-only Docker + UX 抛光门）一起做？

### 通过门后下一步

用户审批后立即执行：

1. 把决策写入 TODOS.md "决策点（不允许静默选）"节，每条带"选择 / 理由 / 影响 / 回滚"。
2. 把决策落地到 `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md` 对应 T1–T13 任务的"决策记录"区。
3. 修复 DESIGN.md 480px（或按用户决定的时机修复）。
4. 调用 `~/.claude/skills/gstack/bin/gstack-review-log` 写 3 条 review-log（plan-ceo-review / plan-design-review / plan-eng-review，含双声标记）。
5. 建议用户接 `/ship`（commit 文档变更）然后启动实施 Task 1（Vue3 + Vite + TS 脚手架 + 13 路由）。
6. 提示后续 PII 入口逻辑（T8–T11）必须跑 `gstack:cso` 安全审计。


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
- [ ] 修订 `docs/DESIGN.md` 第 540 行 + 已知缺口 #3（移到 D12 决议下，与 T1 同步执行）。
- [ ] 把 14 项决策同步到 `TODOS.md` "决策点" 节。
- [ ] 写 3 条 review-log（plan-ceo-review / plan-design-review / plan-eng-review，含双声标记）。
- [ ] 建议下一步：`/ship`（commit autoplan 文档批次） → 启动 T1 实施。
- [ ] 提示：T8–T11 的 PII 入口逻辑必须跑 `gstack:cso` OWASP + STRIDE 安全审计。
