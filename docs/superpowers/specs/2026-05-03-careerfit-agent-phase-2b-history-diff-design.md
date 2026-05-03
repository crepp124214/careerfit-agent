# CareerFit Agent Phase 2B 历史趋势与版本对比设计

日期：2026-05-03

## 背景

Phase 2A 已把 `Next Best Action` 落到学习任务和状态推进。Phase 2B 需要回答闭环里的下一组问题：学习和简历迭代之后，分数是否真的变好；哪些能力缺口仍未改善；两个简历版本之间到底改了什么。

用户在 Phase 2B 方向选择中确认 **A：历史趋势 + 版本对比**。本阶段采用轻量实现：不做富文本编辑、不做导出、不做 PDF/DOCX 解析，只用已有分析报告和已有简历版本生成真实、可验证的复盘视图。

## 目标

- 历史趋势页从占位升级为真实趋势视图，展示已持久化分析报告的总分、分项分数和缺口变化。
- 版本对比页从占位升级为真实简历版本 diff，帮助用户判断表达修改是否与目标岗位更匹配。
- 两个页面都继续遵守 Phase 1 前端验收门：空、加载、错误、部分数据、后端不可用状态完整；禁止 mock 数据假装。
- 不在 localStorage / IndexedDB 保存简历原文、JD 原文、diff 原文或 Agent trace 原文。

## 非目标

- 不新增账号、登录、多租户或分享链接。
- 不新增富文本简历编辑器。
- 不新增 PDF/DOCX 解析依赖。
- 不新增报告导出、简历导出或可下载 diff。
- 不新增后台 worker 或定时任务。
- 不让 LLM 解释趋势或直接判断版本优劣；趋势和 diff 都使用确定性数据。

## 用户体验

### 历史趋势

页面重点是“迭代是否变好”。用户应能看到：

- 最新总分与上一份报告相比的变化。
- 维度分数的折线趋势。
- 当前仍低于阈值的缺口数量。
- 最近报告对应的岗位、简历版本和创建时间。
- 数据不足时的明确提示，例如“至少完成两次分析后才能形成趋势”。

图表使用项目已有 `echarts` / `vue-echarts`，不引入新图表库。

### 版本对比

页面重点是“改了什么，以及是否更诚实”。用户应能看到：

- 两个简历版本选择器。
- 新增、删除、未变的行级 diff。
- 总计新增/删除/未变行数。
- 对比结果中的隐私提示：diff 仅来自服务端已有简历版本，本地不缓存原文。
- 如果两个版本都已有分析报告，则展示最近报告的总分对比；若没有报告，展示“等待分析报告后补充分数影响”。

diff 可以返回简历行文本，因为这是用户显式请求查看自己的版本差异；但前端不得把这些文本写入本地存储、日志或路由参数。

## 后端设计

### 历史趋势 API

新增 `GET /api/reports/history`。

返回内容从已有 `analysis_tasks`、`analysis_reports`、`job_descriptions`、`resume_versions` 派生，不新增表。每条 snapshot 包含：

- `task_id`
- `report_id`
- `job_id`
- `job_title`
- `resume_id`
- `resume_label`
- `final_score`
- `score_breakdown`
- `gap_count`
- `high_risk_suggestion_count`
- `created_at`

可选 query：

- `job_id`
- `resume_id`
- `limit`，默认 20，最大 100。

### 版本对比 API

新增 `GET /api/resumes/compare?from_id=<id>&to_id=<id>`。

返回内容使用 Python 标准库 `difflib.SequenceMatcher` 或等价确定性算法生成，不引入新依赖：

- `from_resume`
- `to_resume`
- `summary`
- `sections`
- `score_context`

`sections` 使用行级 diff：

- `type`: `added` / `removed` / `unchanged`
- `text`
- `old_line`
- `new_line`

`score_context` 只从已有分析报告派生；没有报告时返回 `available: false` 和中文原因，不编造影响结论。

## 前端设计

### API 与 Store

- 新增或扩展 `frontend/src/api/reports.ts`：`fetchReportHistory()`。
- 扩展 `frontend/src/api/resumes.ts`：`compareResumes()`。
- 新增 `frontend/src/stores/history.ts` 管理历史趋势状态。
- 新增 `frontend/src/stores/resumeDiff.ts` 管理版本对比状态。

Store 不持久化响应数据到 localStorage / IndexedDB。

### 页面

- `HistoryView.vue`：支持 unavailable、loading、error、empty、partial、ready。ready 状态显示摘要指标、筛选控件和趋势图。
- `VersionDiffView.vue`：支持 unavailable、loading、error、empty、partial、ready。ready 状态显示版本选择、summary、score context 和 diff 列表。

## 隐私与安全

- 后端 route 不记录简历原文、JD 原文或 diff 文本。
- API 错误详情不得包含简历原文。
- 前端不得把 diff 文本放入 localStorage / IndexedDB、路由 query 或 console。
- diff 文本只在用户进入版本对比页并选择版本后从 API 返回到当前内存。
- 本阶段不新增 PII 入口解析逻辑，因此不强制重跑 `gstack:cso`；如果实现中触碰 prompt 装配、向量入库或解析流程，则必须重跑。

## 成功标准

- `/history` 在 reports ready 时不再显示“功能尚未上线”占位，而是展示真实持久化报告趋势。
- `/diff` 在 resumes ready 时不再显示“功能尚未上线”占位，而是展示真实简历版本 diff。
- 后端历史趋势和版本对比 API 均有测试覆盖。
- 前端两个页面均有状态机与交互测试覆盖。
- 全量后端测试、前端测试、typecheck、build 通过。

