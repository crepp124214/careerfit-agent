# CareerFit Agent Phase 2E 面试训练闭环设计文档

日期：2026-05-04

## 目标

把报告中的面试题从"只读列表"升级为"可练习、可追踪、可复盘"的面试训练闭环。用户可以基于分析报告生成面试训练会话，按技能和难度筛选题目，记录练习状态和笔记，追踪准备进度。

## 当前状态

- 面试题仅作为 `analysis_reports.interview_questions` JSON 列存储，结构为 `{skill, question}` 列表。
- 前端报告页以 `InterviewQuestionCard` 卡片列表展示，只读，无交互。
- 没有独立的面试训练页面、路由或持久化模型。
- RAG 知识库中有 `interview` 类型文档（面试题和评价点），但未被面试模块消费。

## 范围

### 进入范围

- `interview_sessions` 持久化模型，关联 `analysis_reports`。
- `interview_questions` 子表，每道题独立持久化，支持状态和笔记。
- `POST /api/interview/sessions` — 从报告生成面试训练会话。
- `GET /api/interview/sessions` — 列出会话。
- `GET /api/interview/sessions/{id}` — 获取会话详情（含题目列表）。
- `PATCH /api/interview/sessions/{id}/questions/{qid}` — 更新题目状态或笔记。
- RAG 知识库 `interview` 类型文档作为题目来源补充。
- 前端面试训练页面，支持会话列表、题目筛选、练习状态、笔记。
- `/api/capabilities` 增加 `interview` 状态。

### 不进入范围

- 面试回答评分（需要 LLM 实时评判，延后）。
- 面试模拟对话（需要流式 LLM，延后）。
- 面试题导出（Markdown / PDF）。
- 多人面试协作。

## 数据模型

### interview_sessions

| 列 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTO | 会话 ID |
| report_id | INTEGER | FK → analysis_reports.id | 关联报告 |
| job_title | VARCHAR(200) | NOT NULL | 岗位名称（冗余，避免联表） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'created' | 会话状态：created / in_progress / completed |
| total_questions | INTEGER | NOT NULL, DEFAULT 0 | 题目总数 |
| completed_questions | INTEGER | NOT NULL, DEFAULT 0 | 已完成题目数 |
| metadata_ | JSON | NOT NULL, DEFAULT {"schema_version":"1"} | 扩展元数据 |
| created_at | TIMESTAMPTZ | NOT NULL | 创建时间 |
| updated_at | TIMESTAMPTZ | | 更新时间 |

### interview_questions

| 列 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTO | 题目 ID |
| session_id | INTEGER | FK → interview_sessions.id | 关联会话 |
| skill | VARCHAR(100) | NOT NULL | 关联技能 |
| category | VARCHAR(30) | NOT NULL, DEFAULT 'basic' | 题目类别：basic / project_deep_dive / scenario_design |
| difficulty | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | 难度：easy / medium / hard |
| question | TEXT | NOT NULL | 面试问题 |
| answer_hint | TEXT | | 回答提示 |
| follow_ups | JSON | DEFAULT [] | 追问列表 |
| source | VARCHAR(20) | NOT NULL, DEFAULT 'report' | 来源：report / rag / local |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | 练习状态：not_started / practicing / completed / skipped |
| notes | TEXT | | 用户笔记 |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | 排序序号 |

## API 设计

### POST /api/interview/sessions

从报告生成面试训练会话。

请求体：
```json
{
  "report_id": 10,
  "include_rag": true
}
```

响应：
```json
{
  "schema_version": "1",
  "session": {
    "id": 1,
    "report_id": 10,
    "job_title": "大模型应用开发工程师",
    "status": "created",
    "total_questions": 12,
    "completed_questions": 0,
    "created_at": "2026-05-04T..."
  }
}
```

逻辑：
1. 从报告的 `interview_questions` 提取已有题目。
2. 从 RAG 知识库 `interview` 类型文档补充题目。
3. 为每道题分配 category 和 difficulty。
4. 幂等：同一 report_id 不重复创建。

### GET /api/interview/sessions

列出所有会话。

查询参数：`status`（可选筛选）、`limit`、`offset`。

### GET /api/interview/sessions/{id}

获取会话详情，含题目列表。

### PATCH /api/interview/sessions/{id}/questions/{qid}

更新题目状态或笔记。

请求体：
```json
{
  "status": "completed",
  "notes": "回答了三个要点，需要加强系统设计部分"
}
```

状态流转：`not_started` → `practicing` → `completed` / `skipped`。拒绝非法状态跳转。

## 题目分类与难度

### 类别（category）

- `basic`：基础技术题，考察概念理解。
- `project_deep_dive`：项目深挖题，基于简历项目追问。
- `scenario_design`：场景设计题，考察系统设计能力。

### 难度（difficulty）

- `easy`：概念级别，应届生应能回答。
- `medium`：需要项目实践或深度理解。
- `hard`：需要系统设计或跨领域综合能力。

### 分类规则

报告中的面试题默认分类：
- 包含"请说明""请描述""请解释" → `basic`
- 包含简历项目关键词 → `project_deep_dive`
- 包含"设计""如何实现""方案" → `scenario_design`
- 默认 → `basic`

RAG 知识库面试题：使用文档 `metadata.tags` 中的分类信息。

## RAG 集成

当 `include_rag=true` 时：
1. 从报告的 JD 提取 `required_skills`。
2. 对每个技能调用 `retrieve_by_skill(db, skill, top_k=2, doc_type="interview")`。
3. 将检索到的面试题文档解析为结构化题目。
4. 去重（与报告已有题目比较）。
5. 标记 `source: "rag"`。

## 前端设计

### 新增路由

- `/interview` — 面试训练列表页
- `/interview/:id` — 面试训练详情页（题目列表 + 练习）

### 面试训练列表页

- 会话卡片列表，显示岗位名称、题目数、完成进度、状态。
- 支持空状态、加载、错误、后端不可用状态机。
- 从报告页 CTA 跳转创建新会话。

### 面试训练详情页

- 题目按技能/类别/难度筛选。
- 每道题展示：技能标签、类别标签、难度标签、问题文本、回答提示（可展开）、追问列表。
- 练习状态切换：未开始 → 练习中 → 已完成/跳过。
- 笔记输入。
- 进度条显示完成百分比。

### 报告页 CTA

在报告页面试问题区域底部添加"开始面试训练"按钮，跳转到创建会话。

## 隐私约束

- 面试会话和题目不包含完整简历原文或 JD 原文。
- 用户笔记仅存储在服务端，不写入 localStorage。
- Agent trace 不保存面试笔记内容。

## 成功标准

- 可以从报告生成面试训练会话。
- 会话包含报告题目 + RAG 补充题目。
- 每道题有分类、难度、回答提示和追问。
- 可以更新题目练习状态和笔记。
- 前端面试训练页面完整可用。
- 后端测试、前端 typecheck 和 build 通过。
