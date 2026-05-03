# CareerFit Agent Phase 2B 测试计划：历史趋势与版本对比

日期：2026-05-03

## 测试目标

验证 Phase 2B 的历史趋势和版本对比是真实数据驱动、确定性、可解释且不泄露本地敏感数据。测试必须覆盖后端 API、前端 store、前端视图状态机和全栈回归。

## 后端测试

### 历史趋势 API

命令：

```powershell
cd backend
pytest tests/test_report_history_api.py -q
```

覆盖：

- `GET /api/reports/history` 返回 `schema_version` 和 `items`。
- 每个历史 snapshot 包含 `task_id`、`report_id`、`job_id`、`job_title`、`resume_id`、`resume_label`、`final_score`、`score_breakdown`、`gap_count`、`high_risk_suggestion_count`、`created_at`。
- 返回结果按报告创建时间倒序排列。
- `job_id` 筛选只返回对应岗位。
- `resume_id` 筛选只返回对应简历。
- `limit` 生效，且超过上限时被 clamp 到 100。
- 没有报告时返回空列表，不返回 mock 数据。

### 简历版本 diff API

命令：

```powershell
cd backend
pytest tests/test_resume_diff_api.py -q
```

覆盖：

- `GET /api/resumes/compare?from_id=&to_id=` 返回 `schema_version`、`from_resume`、`to_resume`、`summary`、`sections`、`score_context`。
- 行级 diff 能区分 `added`、`removed`、`unchanged`。
- summary 正确统计新增、删除、未变行数。
- 不存在的简历 ID 返回 404。
- 相同 `from_id` 和 `to_id` 返回 400。
- 没有相关分析报告时 `score_context.available` 为 `false`，并返回中文原因。
- 有分析报告时返回两个版本最近报告分数，不调用 LLM 生成影响推断。

## 前端测试

### Store

命令：

```powershell
cd frontend
npm test -- --run tests/stores/history.test.ts tests/stores/resumeDiff.test.ts
```

覆盖：

- `history` store 加载成功后进入 ready，派生 latest 和 score delta。
- `history` store 对空列表进入 empty。
- `history` store 对 API 错误进入 error。
- `resumeDiff` store 加载成功后保存 summary 与 sections。
- `resumeDiff` store 对缺少版本、相同版本和 API 错误给出中文错误。
- 两个 store 都不调用 localStorage / IndexedDB 保存响应正文。

### 历史趋势视图

命令：

```powershell
cd frontend
npm test -- --run tests/views/HistoryView.test.ts
```

覆盖：

- ready 状态显示最新分数、分数变化、缺口数量和图表容器。
- unavailable 状态显示 `BackendNotReadyNotice`。
- loading 状态显示加载提示。
- error 状态显示错误提示和重试入口。
- empty 状态显示“暂无历史报告”。
- partial 状态显示“数据不足以形成趋势”。
- 分数升降同时使用颜色和文字表达。

### 版本对比视图

命令：

```powershell
cd frontend
npm test -- --run tests/views/VersionDiffView.test.ts
```

覆盖：

- ready 状态显示两个版本选择器、diff summary、score context 和行级 diff。
- unavailable 状态显示 `BackendNotReadyNotice`。
- loading 状态显示加载提示。
- error 状态显示错误提示和重试入口。
- empty 状态覆盖简历版本少于 2 个。
- partial 状态覆盖没有 score context，但 diff 可用。
- 选择相同版本时不调用后端，并显示中文错误。
- 新增/删除行同时使用颜色和文字表达。

## 全量回归

后端：

```powershell
cd backend
pytest -q
```

前端：

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

文档：

```powershell
git diff --check
```

Docker smoke：

```powershell
docker compose up --build
```

验收：

- backend health OK。
- frontend 可访问。
- `/api/reports/history` 返回真实历史列表或空列表。
- `/api/resumes/compare` 对两个已有简历版本返回 diff。
- `/history` 和 `/diff` 在 fullstack 模式不显示“功能尚未上线”占位，除非对应 capability 真实不可用。

## 隐私检查

- 搜索前端 localStorage / IndexedDB 写入点，确认没有保存 diff 文本、简历原文、JD 原文。
- 浏览器 console 不应输出 diff 文本或原始简历。
- 后端异常响应不得包含简历原文。
- 如果实现过程中触碰简历/JD 解析、Agent prompt 装配或向量入库，必须补跑 `gstack:cso` 或记录本地等价安全审计。

