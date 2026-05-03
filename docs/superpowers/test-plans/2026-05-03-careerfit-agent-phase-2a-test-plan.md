# CareerFit Agent Phase 2A 测试计划

日期：2026-05-03
版本：v1（学习任务与成长闭环）

## 适用约束

- 本测试计划不覆盖 `AGENTS.md` 与 `CLAUDE.md`；如有冲突，以项目级约束优先。
- 本测试计划对应 `docs/superpowers/plans/2026-05-03-careerfit-agent-phase-2a-learning-loop.md`。
- 修改本文件后，必须同步外部副本：`C:\Users\qwer\.gstack\projects\Newproject\phase-2a-test-plan-2026-05-03-careerfit-agent.md`。

## 测试门

| 门 | 阻塞 Phase 2A | 说明 |
|---|---|---|
| Phase 1.5 收口门 | 是 | review-log、PII 安全审计、测试计划同步 |
| 后端学习任务 API 门 | 是 | list/generate/update 与幂等生成 |
| 前端学习任务视图门 | 是 | `/learning` 真实状态机与交互 |
| Next Best Action 联动门 | 是 | 工作台与报告页 CTA 连接学习任务 |
| 全栈 smoke 门 | 是 | Docker fullstack 中 learning capability ready |

## 后端测试

### API 覆盖

| API | 必测场景 |
|---|---|
| `GET /api/learning/tasks` | 空列表、有任务列表、字段契约完整 |
| `POST /api/learning/tasks/generate` | 有效分析任务、重复生成幂等、分析任务不存在、报告不存在 |
| `PATCH /api/learning/tasks/{id}` | `not_started -> doing`、`doing -> done`、`doing -> paused`、`paused -> doing`、非法状态、任务不存在 |
| `GET /api/capabilities` | `learning` 为 `ready`，前端 fullstack 模式识别为可用 |

### 学习任务字段契约

每个学习任务响应必须包含：

```json
{
  "schema_version": "1",
  "id": 1,
  "source_task_id": 1,
  "source_report_id": 1,
  "title": "补强 FastAPI 项目证据",
  "dimension": "skill_gap",
  "rationale": "来自报告能力缺口，不含简历/JD 原文",
  "status": "not_started",
  "evidence_refs": [],
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

断言：

- `schema_version` 必须存在。
- `status` 只能是 `not_started`、`doing`、`done`、`paused`。
- `source_task_id` 与 `source_report_id` 必须存在。
- 响应不得包含 `raw_text`、`raw_resume`、`raw_jd`、完整简历原文或完整 JD 原文。
- `evidence_refs` 只能保存证据 ID、维度或短摘要，不保存原文。

### 幂等生成

同一个 `task_id` 连续调用两次：

- 第二次不新增数据库行。
- 两次返回的任务 ID 顺序一致。
- 不覆盖已经被用户修改过的任务状态。

### 状态流转

合法：`not_started -> doing`、`not_started -> paused`、`doing -> done`、`doing -> paused`、`paused -> doing`。

非法：`done -> doing`、`done -> paused`、任意未知状态。非法状态必须返回 422 或 400；任务不存在必须返回 404。

## 前端测试

### API 层

- `fetchLearningTasks()` 成功时返回 `ok: true` 与任务数组。
- `fetchLearningTasks()` 遇到 404/501 时返回 unavailable，不 throw。
- `generateLearningTasks(taskId)` body 使用 `task_id`，不使用 `taskId`。
- `updateLearningTaskStatus(id, status)` 使用 `PATCH /learning/tasks/{id}`。

### Store 层

`frontend/src/stores/learning.ts` 必测：

- 初始状态：`status = "idle"`、`tasks = []`、`error = null`。
- `loadTasks()` 成功：`status = "ready"`。
- `loadTasks()` 后端不可用：`status = "unavailable"`，`tasks = []`。
- `loadTasks()` 失败：`status = "error"`，显示中文错误。
- `generateFromTask(taskId)` 成功：用返回任务替换当前任务列表。
- `updateStatus(id, status)` 成功：只更新对应任务。
- store 不写 localStorage / IndexedDB。

### `/learning` 视图

必须覆盖：

- learning capability unavailable：渲染 `BackendNotReadyNotice`，文案包含“功能尚未上线”或“等待后端”。
- loading：显示加载状态。
- error：显示 `ErrorBanner`。
- empty：显示空状态，不出现硬编码 mock 学习任务。
- ready：显示任务标题、维度、状态文字、证据数量和操作按钮。
- partial：字段缺失时显示弱提示，不崩溃。
- 点击“开始”：调用 `updateStatus(id, "doing")`。
- 点击“完成”：调用 `updateStatus(id, "done")`。

### Next Best Action 联动

- `NextBestActionCallout` 支持 `ctaTo="/learning"`。
- 工作台首屏有 `Next Best Action` 时，CTA 指向 `/learning` 或 `/learning?taskId=<id>`。
- 报告头部有 `Next Best Action` 时，CTA 指向 `/learning` 或 `/learning?taskId=<id>`。
- 路由 query 只允许 ID，不允许携带简历/JD/报告正文。

### 无障碍与视觉状态

- 任务状态必须文字 + 颜色双通道表达。
- 状态按钮必须有 `aria-label`。
- 禁用按钮必须说明原因。
- 键盘可达：Tab 能到达任务状态按钮，Enter 能触发。
- 480px 移动端任务卡片不溢出、不遮挡。

## 安全与隐私测试

- 学习任务响应不包含原始简历/JD。
- 前端不把任务详情写入 `careerfit:pref:*`。
- `console.warn`、`console.error` 不输出原始简历/JD。
- PII 入口逻辑变更后必须运行 `gstack:cso` 或记录环境不可用原因。

## 验证命令

后端：

```powershell
cd backend
pytest tests/test_learning_api.py -q
pytest -q
```

前端：

```powershell
cd frontend
npm test -- --run tests/stores/learning.test.ts tests/views/LearningTasksView.test.ts
npm test
npm run typecheck
npm run build
```

Docker：

```powershell
docker compose up --build
```

文档：

```powershell
git diff --check
```

如果任一命令无法运行，必须在实施计划对应步骤记录失败原因、已尝试命令和下一步修正方向。

