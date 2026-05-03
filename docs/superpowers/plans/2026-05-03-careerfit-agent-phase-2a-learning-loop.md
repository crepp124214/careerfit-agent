# CareerFit Agent Phase 2A 学习闭环实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 Phase 1 的分析报告转化为可持续推进的学习任务闭环，让 `Next Best Action` 能落到真实任务、真实状态和可复盘进展。

**Architecture:** 后端新增 `learning_tasks` 持久化模型、schema、service 和 API route；学习任务从 `analysis_reports.learning_plan`、`gaps`、`next_best_action` 派生，禁止编造报告外事实。前端把 `/learning` 从占位页升级为真实任务工作台，并让工作台与报告页能跳转到对应学习任务。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、SQLite 测试替身、PostgreSQL Docker、Vue3、TypeScript、Pinia、Vue Router、Vitest、Vue Test Utils、Docker Compose。

---

## 范围

本计划只覆盖 Phase 2A：学习任务与成长闭环真实化。

进入范围：

- Phase 1.5 收口：补 review-log、跑 PII 安全审计、同步测试计划副本。
- 后端学习任务 API：列表、按分析报告生成、状态更新。
- 学习任务持久化：关联 `analysis_tasks` 和 `analysis_reports`，JSON 字段包含 `schema_version`。
- `CAPABILITIES.learning` 从 `unavailable` 翻为 `ready`。
- 前端 `/learning` 真实数据状态机：空、加载、错误、部分数据、有数据。
- `Next Best Action` 与学习任务打通：能从工作台或报告页进入学习任务。

不进入范围：登录、多用户、多租户、PDF/DOCX 简历解析、报告导出、面试回答评分、外部课程爬取、生产级后台 worker。

## 成功标准

- `GET /api/learning/tasks` 返回当前学习任务列表。
- `POST /api/learning/tasks/generate` 能从已有分析任务生成幂等学习任务。
- `PATCH /api/learning/tasks/{id}` 支持合法状态流转，拒绝非法状态。
- 学习任务只来自报告中的缺口、学习计划和 `Next Best Action`，不得加入无证据新事实。
- 前端 `LearningTasksView` 不再显示 disabled 占位按钮；在 learning ready 时渲染真实任务列表和状态操作。
- 工作台首屏和报告头部的 `Next Best Action` 能链接到 `/learning`。
- localStorage / IndexedDB 仍只保存 UI 偏好和最近打开 ID，不保存任务详情中的敏感文本。
- 后端、前端和 Docker smoke 验证通过；若命令无法运行，必须写入本计划对应步骤附近。

## 文件结构

```text
backend/
  app/
    api/routes/learning.py
    db/models.py
    main.py
    schemas/learning.py
    services/learning_service.py
  tests/
    test_learning_api.py
    test_analysis_flow.py
frontend/
  src/
    api/learning.ts
    components/workbench/NextBestActionCallout.vue
    stores/learning.ts
    views/LearningTasksView.vue
    views/ReportView.vue
    views/WorkspaceView.vue
  tests/
    stores/learning.test.ts
    views/LearningTasksView.test.ts
    views/PeripheralViews.test.ts
    views/ReportView.test.ts
    views/WorkspaceView.test.ts
docs/
  superpowers/test-plans/2026-05-03-careerfit-agent-phase-2a-test-plan.md
TODOS.md
```

---

## Task 0：Phase 1.5 收口门

**Files:**

- Modify: `TODOS.md`
- Create: `docs/superpowers/review-logs/2026-05-03-phase-1-review-log.md`
- Modify or Create: `docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2a-test-plan.md`

- [x] **Step 1：补 Phase 1 review-log**

创建 `docs/superpowers/review-logs/2026-05-03-phase-1-review-log.md`，记录 `plan-ceo-review`、`plan-design-review`、`plan-eng-review` 的 Phase 1 结论；必须写明 Hold Scope、不扩大到 HR/导师/登录、Next Best Action 显眼位、风险双通道、PII 风险门。

- [x] **Step 2：运行 PII 安全审计**

Run:

```powershell
gstack:cso
```

Expected: 生成 OWASP + STRIDE 基线结论，覆盖简历/JD 输入、Agent prompt 装配、Agent trace 脱敏、报告和学习任务生成。若环境没有该入口，把失败原因写入 review-log，并在 `TODOS.md` 保留未完成项。

验证记录：当前 PowerShell 环境没有 `gstack:cso` 可执行入口；已在 `docs/superpowers/review-logs/2026-05-03-phase-1-review-log.md` 记录命令失败原因，并按本地 `gstack:cso` skill 文档完成 OWASP + STRIDE PII 基线审计。

- [x] **Step 3：同步测试计划副本**

Run:

```powershell
Copy-Item -LiteralPath "E:\New project 2\docs\superpowers\test-plans\2026-05-03-careerfit-agent-phase-2a-test-plan.md" -Destination "C:\Users\qwer\.gstack\projects\Newproject\phase-2a-test-plan-2026-05-03-careerfit-agent.md" -Force
```

Expected: 外部副本存在，内容与项目内 Phase 2A 测试计划一致。

---

## Task 1：后端学习任务模型与 schema

**Files:**

- Modify: `backend/app/db/models.py`
- Create: `backend/app/schemas/learning.py`
- Test: `backend/tests/test_learning_api.py`

- [x] **Step 1：写失败测试：学习任务字段契约**

在 `backend/tests/test_learning_api.py` 新增测试，先创建岗位、简历、分析任务，再调用 `POST /api/learning/tasks/generate`，断言响应包含 `schema_version`、`status`、`source_report_id`、`source_task_id`、`title`、`dimension`、`evidence_refs`。

- [x] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_learning_api.py::test_generate_learning_tasks_contract -q
```

Expected: FAIL，原因是 `/api/learning/tasks/generate` 不存在。

- [x] **Step 3：新增模型**

在 `backend/app/db/models.py` 新增 `LearningTaskStatus` enum（`not_started`、`doing`、`done`、`paused`）和 `LearningTask` table：`id`、`source_task_id`、`source_report_id`、`title`、`dimension`、`rationale`、`status`、`evidence_refs`、`metadata`、`created_at`、`updated_at`。`metadata` 必须包含 `schema_version`。

- [x] **Step 4：新增 schema**

创建 `backend/app/schemas/learning.py`，包含 `LearningTaskRead`、`LearningTaskGenerateRequest`、`LearningTaskUpdateRequest`。`LearningTaskRead.schema_version` 从模型 `metadata` 读取，缺失时返回 `"1"`。

---

## Task 2：后端学习任务生成与幂等逻辑

**Files:**

- Create: `backend/app/services/learning_service.py`
- Create: `backend/app/api/routes/learning.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_learning_api.py`

- [x] **Step 1：写失败测试：从分析报告生成任务**

断言 `POST /api/learning/tasks/generate` 对有效 `task_id` 返回 201，至少生成 1 条任务，且所有任务 `source_task_id` 等于请求任务 ID。

- [x] **Step 2：写失败测试：生成任务幂等**

同一个 `task_id` 连续生成两次，第二次不新增行，返回任务 ID 顺序和第一次一致；已修改过的任务状态不得被覆盖。

- [x] **Step 3：写失败测试：报告不存在时返回 404**

`POST /api/learning/tasks/generate` 对不存在的 `task_id` 返回 404。

- [x] **Step 4：实现 service**

`backend/app/services/learning_service.py` 实现：

- `list_learning_tasks(db)`
- `generate_learning_tasks(db, task_id)`
- `update_learning_task_status(db, task_id, status)`

生成规则：优先从 `AnalysisReport.learning_plan` 生成；为空时从 `gaps` 生成；仍为空时从 `next_best_action.title` 生成 1 条。任务必须保留 `source_task_id`、`source_report_id`、`dimension`、`evidence_refs`，不得读取或返回原始简历/JD 文本。

- [x] **Step 5：实现 route 并翻转 capability**

创建 `backend/app/api/routes/learning.py`：

- `GET /api/learning/tasks`
- `POST /api/learning/tasks/generate`

`PATCH /api/learning/tasks/{task_id}` 留到 Task 3，在状态流转测试失败后实现。

修改 `backend/app/main.py`：注册 route，`CAPABILITIES["learning"] = "ready"`。

- [x] **Step 6：运行学习任务 API 测试**

Run:

```powershell
cd backend
pytest tests/test_learning_api.py -q
```

Expected: PASS。

---

## Task 3：后端状态流转与主路径补充

**Files:**

- Modify: `backend/app/services/learning_service.py`
- Modify: `backend/tests/test_learning_api.py`
- Modify: `backend/tests/test_analysis_flow.py`

- [x] **Step 1：写失败测试：合法状态流转**

生成任务后，PATCH 为 `doing`，再 PATCH 为 `done`，断言响应状态更新。

- [x] **Step 2：写失败测试：非法状态被拒绝**

未知状态返回 422；不存在任务返回 404；`done -> doing` 与 `done -> paused` 返回 400 或 422。

- [x] **Step 3：补主路径断言**

在 `backend/tests/test_analysis_flow.py` 中补充：分析成功后调用学习任务生成接口，响应为 201 且返回非空任务列表。

- [x] **Step 4：运行后端测试**

Run:

```powershell
cd backend
pytest -q
```

Expected: PASS。

---

## Task 4：前端 learning API 与 store

**Files:**

- Modify: `frontend/src/api/learning.ts`
- Create: `frontend/src/stores/learning.ts`
- Create: `frontend/tests/stores/learning.test.ts`

- [x] **Step 1：写失败测试：store 加载任务**

mock `fetchLearningTasks` 返回 `ok: true`，断言 `tasks`、`status`、`error`。

- [x] **Step 2：写失败测试：接口不可用时进入 unavailable**

mock `fetchLearningTasks` 返回 unavailable，断言 `tasks` 为空，`status` 为 `unavailable`，不得伪造任务。

- [x] **Step 3：写失败测试：状态更新**

mock `updateLearningTaskStatus` 返回更新后的任务，断言 store 只更新对应任务。

- [x] **Step 4：实现 API 与 Pinia store**

`frontend/src/api/learning.ts` 使用后端契约：状态为 `not_started | doing | done | paused`，生成接口 body 使用 `task_id`。新增 `frontend/src/stores/learning.ts`，支持 `loadTasks()`、`generateFromTask(taskId)`、`updateStatus(id, status)`，不写 localStorage / IndexedDB。

- [x] **Step 5：运行 store 测试**

Run:

```powershell
cd frontend
npm test -- --run tests/stores/learning.test.ts
```

Expected: PASS。

---

## Task 5：前端 LearningTasksView 真实化

**Files:**

- Modify: `frontend/src/views/LearningTasksView.vue`
- Modify: `frontend/tests/views/PeripheralViews.test.ts`
- Create or Modify: `frontend/tests/views/LearningTasksView.test.ts`

- [x] **Step 1：写失败测试：ready 时渲染真实任务**

设置 `availability.learning = ready`，mock 两条任务，断言标题、维度、状态文字、证据数量和操作按钮存在。

- [x] **Step 2：写失败测试：空、加载、错误、部分数据状态**

分别断言 `EmptyState`、加载卡片、`ErrorBanner`、字段缺失弱提示；禁止出现硬编码 mock 任务。

- [x] **Step 3：写失败测试：状态更新交互**

点击“开始”“完成”时调用 store 的 `updateStatus`。

- [x] **Step 4：实现真实视图**

`LearningTasksView.vue` 支持 learning unavailable、loading、error、empty、partial、ready 六类状态。风险/状态必须文字 + 颜色双通道表达，操作按钮要有 `aria-label`。

- [x] **Step 5：运行视图测试**

Run:

```powershell
cd frontend
npm test -- --run tests/views/LearningTasksView.test.ts tests/views/PeripheralViews.test.ts
```

Expected: PASS。

---

## Task 6：Next Best Action 与学习任务联动

**Files:**

- Modify: `frontend/src/components/workbench/NextBestActionCallout.vue`
- Modify: `frontend/src/views/WorkspaceView.vue`
- Modify: `frontend/src/views/ReportView.vue`
- Modify: `frontend/tests/components/NextBestActionCallout.test.ts`
- Modify: `frontend/tests/views/WorkspaceView.test.ts`
- Modify: `frontend/tests/views/ReportView.test.ts`

- [x] **Step 1：写失败测试：组件支持 `/learning` CTA**

测试 `NextBestActionCallout` 在传入 `ctaTo="/learning"` 时渲染可访问链接或按钮，包含清晰 `aria-label`。

- [x] **Step 2：写失败测试：工作台与报告页 CTA 指向学习任务**

断言工作台首屏和报告头部的 `Next Best Action` CTA 指向 `/learning` 或只携带 ID 的 `/learning?taskId=<id>`。

- [x] **Step 3：实现 CTA 联动**

如果 action 自带 `ctaTo`，优先使用；否则工作台和报告页默认传入 `/learning`。不要把报告正文、简历原文或 JD 原文写入路由 query 或 localStorage。

- [x] **Step 4：运行 CTA 测试**

Run:

```powershell
cd frontend
npm test -- --run tests/components/NextBestActionCallout.test.ts tests/views/WorkspaceView.test.ts tests/views/ReportView.test.ts
```

Expected: PASS。

---

## Task 7：全栈能力翻转与回归验证

**Files:**

- Modify: `README.md`（如启动说明或能力状态有变化）
- Modify: `TODOS.md`
- Modify: `docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2a-test-plan.md`

- [x] **Step 1：后端全量测试**

Run:

```powershell
cd backend
pytest -q
```

Expected: PASS。

- [x] **Step 2：前端全量测试**

Run:

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

Expected: 全部 PASS。

- [x] **Step 3：Docker smoke**

Run:

```powershell
docker compose up --build
```

Expected: backend health OK；frontend 可访问；`/api/capabilities` 返回 `learning: "ready"`；`/learning` 在 fullstack 模式展示真实任务状态机。

- [x] **Step 4：文档同步检查**

Run:

```powershell
git diff --check
```

Expected: 无 trailing whitespace 或冲突标记。

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| 学习任务来源 | 只从报告 `learning_plan`、`gaps`、`next_best_action` 派生 | 遵守证据链与诚实优化约束，避免编造新事实 | 后续引入可信知识库资源推荐并通过 RAG 证据测试 |
| 生成时机 | 用户显式触发 `POST /api/learning/tasks/generate` | Phase 2A 不引入 worker，保持主路径可控 | 用户研究显示自动生成更符合流程，且有幂等保护 |
| 幂等策略 | 同一 report 已有任务则直接返回已有任务 | 避免重复任务污染学习工作台 | 需要支持多版学习计划时引入 `generation_version` |
| 状态机 | `not_started` / `doing` / `done` / `paused` | 足够覆盖个人学习推进，不引入复杂项目管理 | 用户需要 due date、优先级、归档等完整任务系统 |
| 本地存储 | 不缓存学习任务详情 | 学习任务可能包含简历/JD 派生敏感摘要 | 后续做离线模式并通过 PII 存储审计 |

## 风险与缓解

- **风险：学习任务携带敏感文本。** 缓解：任务只保存短标题、维度、理由和证据引用，不保存原始简历/JD。
- **风险：Next Best Action 和任务不一致。** 缓解：生成时优先使用同一份报告的 `next_best_action`，并保留 `source_report_id`。
- **风险：重复生成造成任务泛滥。** 缓解：同一报告幂等返回已有任务。
- **风险：前端误把 unavailable 渲染成 mock 数据。** 缓解：测试断言 learning unavailable 时只显示 `BackendNotReadyNotice`。
