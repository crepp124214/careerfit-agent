# CareerFit Agent Phase 2B 历史趋势与版本对比实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把历史趋势和版本对比从诚实占位升级为真实数据驱动的复盘闭环，让用户能判断学习和简历迭代是否带来改善。

**Architecture:** 后端不新增持久化表，历史趋势从 `analysis_reports` 与关联任务派生，版本对比从已有 `resume_versions.raw_text` 计算确定性行级 diff。前端新增轻量 API/store，把 `HistoryView` 和 `VersionDiffView` 升级为完整状态机和真实交互。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、Python `difflib`、SQLite 测试替身、PostgreSQL Docker、Vue3、TypeScript、Pinia、Vue Router、ECharts、Vitest、Vue Test Utils、Docker Compose。

---

## 范围

进入范围：

- 后端历史趋势 API：`GET /api/reports/history`。
- 后端简历版本对比 API：`GET /api/resumes/compare`。
- 趋势数据只来自已持久化分析报告，不编造趋势。
- diff 使用确定性行级算法，不调用 LLM。
- 前端历史趋势页真实化：筛选、摘要指标、趋势图、状态机。
- 前端版本对比页真实化：版本选择、diff 摘要、行级 diff、分数上下文、状态机。
- 文档、测试计划和 `TODOS.md` 同步。

不进入范围：

- 富文本简历编辑器。
- PDF/DOCX 解析或文件上传。
- 报告导出、简历导出、diff 导出。
- 登录、多用户、多租户、分享链接。
- 外部课程推荐、自动周报或后台 worker。
- LLM 趋势解读。

## 成功标准

- `GET /api/reports/history` 返回真实报告 snapshot，支持 `job_id`、`resume_id`、`limit`。
- `GET /api/resumes/compare?from_id=&to_id=` 返回确定性 diff summary、sections 和可选 score context。
- 历史趋势页在有报告时展示图表和摘要；报告不足时展示数据不足状态。
- 版本对比页在选择两个版本后展示真实 diff；版本不足时展示空状态。
- 两个前端页面均覆盖 unavailable、loading、error、empty、partial、ready。
- localStorage / IndexedDB 不保存简历原文、JD 原文或 diff 文本。
- 后端、前端、typecheck、build、文档 diff 检查通过。

## 文件结构

```text
backend/
  app/
    api/routes/reports.py
    api/routes/resumes.py
    schemas/reports.py
    schemas/resumes.py
    services/report_history_service.py
    services/resume_diff_service.py
  tests/
    test_report_history_api.py
    test_resume_diff_api.py
frontend/
  src/
    api/reports.ts
    api/resumes.ts
    stores/history.ts
    stores/resumeDiff.ts
    views/HistoryView.vue
    views/VersionDiffView.vue
  tests/
    stores/history.test.ts
    stores/resumeDiff.test.ts
    views/HistoryView.test.ts
    views/VersionDiffView.test.ts
docs/
  superpowers/specs/2026-05-03-careerfit-agent-phase-2b-history-diff-design.md
  superpowers/plans/2026-05-03-careerfit-agent-phase-2b-history-diff.md
  superpowers/test-plans/2026-05-03-careerfit-agent-phase-2b-test-plan.md
TODOS.md
```

---

## Task 0：计划与文档门

**Files:**

- Create: `docs/superpowers/specs/2026-05-03-careerfit-agent-phase-2b-history-diff-design.md`
- Create: `docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2b-test-plan.md`
- Modify: `TODOS.md`

- [x] **Step 1：确认 Phase 2B 范围**

用户已选择 A：历史趋势 + 版本对比。记录范围边界：轻量真实复盘，不做导出、富文本编辑、PDF/DOCX、登录或多租户。

- [x] **Step 2：创建设计文档**

新增 Phase 2B 设计文档，写明 API、前端状态机、隐私约束和成功标准。

- [x] **Step 3：创建测试计划**

新增 Phase 2B 测试计划，并同步到外部 gstack 测试计划副本。

- [x] **Step 4：更新 TODOS**

把 Phase 2B 当前范围、延后项和验证门写入 `TODOS.md`。

---

## Task 1：后端历史趋势 API

**Files:**

- Create: `backend/app/services/report_history_service.py`
- Modify: `backend/app/api/routes/reports.py`
- Modify: `backend/app/schemas/reports.py`
- Test: `backend/tests/test_report_history_api.py`

- [ ] **Step 1：写失败测试：历史趋势字段契约**

新增测试：创建岗位、简历和两次分析，调用 `GET /api/reports/history`，断言响应包含 `schema_version`、`items`，每个 item 包含 `task_id`、`report_id`、`job_title`、`resume_label`、`final_score`、`score_breakdown`、`gap_count`、`created_at`。

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_report_history_api.py::test_report_history_contract -q
```

Expected: FAIL，原因是 `/api/reports/history` 不存在或字段缺失。

- [ ] **Step 3：新增 schema**

在 `backend/app/schemas/reports.py` 新增 `ReportHistoryItem` 和 `ReportHistoryResponse`。`ReportHistoryResponse.schema_version` 固定为 `"1"`。

- [ ] **Step 4：实现 service**

创建 `backend/app/services/report_history_service.py`，从 `AnalysisReport` join `AnalysisTask`、`JobDescription`、`ResumeVersion` 查询报告，按 `created_at desc` 排序。`limit` clamp 到 1–100。

- [ ] **Step 5：实现 route**

在 `backend/app/api/routes/reports.py` 新增 `GET /history`，只做参数接收、依赖注入和响应返回。

- [ ] **Step 6：补筛选测试**

测试 `job_id`、`resume_id` 和 `limit` 均生效。

- [ ] **Step 7：运行后端历史测试**

Run:

```powershell
cd backend
pytest tests/test_report_history_api.py -q
```

Expected: PASS。

---

## Task 2：后端简历版本 diff API

**Files:**

- Create: `backend/app/services/resume_diff_service.py`
- Modify: `backend/app/api/routes/resumes.py`
- Modify: `backend/app/schemas/resumes.py`
- Test: `backend/tests/test_resume_diff_api.py`

- [ ] **Step 1：写失败测试：diff 字段契约**

创建两个简历版本，调用 `GET /api/resumes/compare?from_id=<old>&to_id=<new>`，断言响应包含 `schema_version`、`from_resume`、`to_resume`、`summary`、`sections`、`score_context`。

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_resume_diff_api.py::test_resume_diff_contract -q
```

Expected: FAIL，原因是 `/api/resumes/compare` 不存在。

- [ ] **Step 3：新增 schema**

在 `backend/app/schemas/resumes.py` 新增 `ResumeDiffResumeRef`、`ResumeDiffSummary`、`ResumeDiffSection`、`ResumeScoreContext`、`ResumeDiffResponse`。

- [ ] **Step 4：实现 diff service**

创建 `backend/app/services/resume_diff_service.py`，使用 `difflib.SequenceMatcher` 或标准库等价算法按行生成 `added`、`removed`、`unchanged`。不要在 service 中写日志输出原文。

- [ ] **Step 5：实现 score context**

从两个简历版本各自最近一次成功分析报告中提取 `final_score` 和 `created_at`。没有报告时返回 `available: false` 和中文原因。

- [ ] **Step 6：实现 route**

在 `backend/app/api/routes/resumes.py` 新增 `GET /compare`，缺失简历返回 404，相同版本返回 400。

- [ ] **Step 7：补错误路径测试**

覆盖不存在 ID、相同 ID、没有报告时的 `score_context.available: false`。

- [ ] **Step 8：运行 diff 测试**

Run:

```powershell
cd backend
pytest tests/test_resume_diff_api.py -q
```

Expected: PASS。

---

## Task 3：前端 API 与 store

**Files:**

- Modify: `frontend/src/api/reports.ts`
- Modify: `frontend/src/api/resumes.ts`
- Create: `frontend/src/stores/history.ts`
- Create: `frontend/src/stores/resumeDiff.ts`
- Test: `frontend/tests/stores/history.test.ts`
- Test: `frontend/tests/stores/resumeDiff.test.ts`

- [ ] **Step 1：写失败测试：history store 加载成功**

mock `fetchReportHistory` 返回两条 snapshot，断言 `items`、`status`、`latest`、`scoreDelta`。

- [ ] **Step 2：写失败测试：history store 错误与空状态**

mock API 错误和空列表，断言 `status` 分别为 `error`、`empty`，不得创建假数据。

- [ ] **Step 3：写失败测试：resumeDiff store 加载 diff**

mock `compareResumes` 返回 diff，断言 `summary`、`sections`、`status`。

- [ ] **Step 4：写失败测试：resumeDiff store 错误与版本不足**

覆盖 API 错误、缺少 `fromId` / `toId`、相同 ID，断言中文错误消息。

- [ ] **Step 5：实现 API 函数**

`frontend/src/api/reports.ts` 新增 `fetchReportHistory(params)`；`frontend/src/api/resumes.ts` 新增 `compareResumes(fromId, toId)`。保留对现有后端 snake_case 的 normalize。

- [ ] **Step 6：实现两个 store**

`history` store 管理筛选、加载和派生指标；`resumeDiff` store 管理版本选择、diff 加载和错误。两个 store 均不使用 localStorage / IndexedDB。

- [ ] **Step 7：运行 store 测试**

Run:

```powershell
cd frontend
npm test -- --run tests/stores/history.test.ts tests/stores/resumeDiff.test.ts
```

Expected: PASS。

---

## Task 4：前端 HistoryView 真实化

**Files:**

- Modify: `frontend/src/views/HistoryView.vue`
- Test: `frontend/tests/views/HistoryView.test.ts`

- [ ] **Step 1：写失败测试：ready 状态**

mock reports ready 和两条历史 snapshot，断言标题、最新分数、分数变化、缺口数量、趋势图容器存在。

- [ ] **Step 2：写失败测试：状态机**

覆盖 unavailable、loading、error、empty、partial。partial 至少覆盖缺少 `score_breakdown` 或只有 1 条报告。

- [ ] **Step 3：写失败测试：筛选交互**

切换时间区间或筛选控件时调用 store reload；如果后端只支持 `limit`，前端先把区间映射为 limit。

- [ ] **Step 4：实现视图**

使用 `vue-echarts` 渲染趋势图；用文本同步表达分数变化，不能只靠颜色。加载和错误状态复用已有 feedback 组件。

- [ ] **Step 5：运行 HistoryView 测试**

Run:

```powershell
cd frontend
npm test -- --run tests/views/HistoryView.test.ts
```

Expected: PASS。

---

## Task 5：前端 VersionDiffView 真实化

**Files:**

- Modify: `frontend/src/views/VersionDiffView.vue`
- Test: `frontend/tests/views/VersionDiffView.test.ts`

- [ ] **Step 1：写失败测试：ready 状态**

mock resumes ready、两个简历版本和 diff 响应，断言选择器、summary、score context、added/removed/unchanged 文本存在。

- [ ] **Step 2：写失败测试：状态机**

覆盖 unavailable、loading、error、empty、partial。empty 包括简历版本少于 2 个。

- [ ] **Step 3：写失败测试：选择版本触发 compare**

选择两个不同版本后调用 `compareResumes`；相同版本时显示中文错误并不调用 API。

- [ ] **Step 4：实现视图**

显示两个版本选择器、diff summary、分数上下文和行级 diff。风险或删除信息必须颜色 + 文本双通道表达，并为按钮/选择器补充 ARIA。

- [ ] **Step 5：运行 VersionDiffView 测试**

Run:

```powershell
cd frontend
npm test -- --run tests/views/VersionDiffView.test.ts
```

Expected: PASS。

---

## Task 6：全量回归与文档同步

**Files:**

- Modify: `TODOS.md`
- Modify: `docs/superpowers/test-plans/2026-05-03-careerfit-agent-phase-2b-test-plan.md`

- [ ] **Step 1：后端全量测试**

Run:

```powershell
cd backend
pytest -q
```

Expected: PASS。

- [ ] **Step 2：前端全量测试**

Run:

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

Expected: 全部 PASS。

- [ ] **Step 3：Docker smoke**

Run:

```powershell
docker compose up --build
```

Expected: backend health OK；frontend 可访问；`/history` 和 `/diff` 在 fullstack 模式展示真实状态机。

- [ ] **Step 4：文档同步检查**

Run:

```powershell
git diff --check
```

Expected: 无 trailing whitespace 或冲突标记。

- [ ] **Step 5：提交 Phase 2B 实现**

Run:

```powershell
git status --short
git add backend frontend docs TODOS.md
git commit -m "feat: add history trends and resume diff"
```

Expected: commit 成功，且不包含 `.superpowers/` 临时头脑风暴 HTML。

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| Phase 2B 范围 | A：历史趋势 + 版本对比 | 同时补上“是否变好”和“改了什么”，形成学习后的复盘闭环 | 实现超过一个里程碑仍无法稳定，可先切出趋势或 diff 单独交付 |
| 趋势数据来源 | 从已有报告实时派生，不新增 snapshot 表 | Phase 2B 数据量小，避免过早持久化派生数据 | 查询性能或审计需求要求保留历史快照 |
| diff 算法 | Python 标准库确定性行级 diff | 不引入依赖，不让 LLM 判断版本差异 | 用户需要词级高亮或富文本语义 diff |
| score context | 只展示已有报告分数，不生成“影响推断” | 避免把相关性包装成因果结论 | 后续有同岗位同简历链路的可解释实验数据 |
| 本地存储 | 不缓存 diff、报告 snapshot 或简历原文 | 遵守 PII 约束 | 后续离线模式通过专门安全审计 |

## 风险与缓解

- **风险：diff 响应包含简历敏感文本。** 缓解：只在用户显式比较时返回，不写日志、不落本地存储、不放入路由。
- **风险：趋势被误读为因果。** 缓解：只展示“分数变化”和“报告时间”，不写“某次学习导致提升”的结论。
- **风险：历史报告不足导致图表空转。** 缓解：少于 2 条报告时展示数据不足状态，仍显示最新报告摘要。
- **风险：前端回到 mock 数据。** 缓解：视图测试断言 empty/unavailable 不出现硬编码示例任务或报告。

