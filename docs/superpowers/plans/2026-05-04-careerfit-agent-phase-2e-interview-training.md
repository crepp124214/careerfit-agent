# CareerFit Agent Phase 2E 面试训练闭环实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把面试题从只读列表升级为可练习、可追踪、可复盘的面试训练闭环。

**Architecture:** 新增 `interview_sessions` + `interview_questions` 两表，新增面试训练 API，RAG 补充面试题，前端新增面试训练页面。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、PostgreSQL、Vue 3、TypeScript。

---

## 范围

进入范围：

- `interview_sessions` 和 `interview_questions` 持久化模型。
- 面试训练 CRUD API。
- RAG 知识库面试题补充。
- 前端面试训练列表页和详情页。
- `/api/capabilities` 增加 `interview` 状态。

不进入范围：

- 面试回答评分。
- 面试模拟对话。
- 面试题导出。

## 成功标准

- 可以从报告生成面试训练会话。
- 会话包含报告题目 + RAG 补充题目（去重）。
- 每道题有分类、难度、回答提示和追问。
- 可以更新题目练习状态和笔记，状态流转校验正确。
- 前端面试训练页面完整可用（列表 + 详情 + 练习）。
- 后端测试、前端 typecheck 和 build 通过。

## 文件结构

```text
backend/
  app/
    db/models.py                          # 修改：新增 InterviewSession + InterviewQuestion
    api/routes/interview.py               # 新增
    schemas/interview.py                  # 新增
    services/interview_service.py         # 新增
    main.py                               # 修改：注册 interview router + capability
  tests/
    test_interview_api.py                 # 新增
    test_interview_service.py             # 新增
frontend/
  src/
    api/interview.ts                      # 新增
    stores/interview.ts                   # 新增
    views/InterviewListView.vue           # 新增
    views/InterviewDetailView.vue         # 新增
    components/interview/InterviewSessionCard.vue  # 新增
    components/interview/InterviewQuestionCard.vue  # 新增（替换报告页简单版）
    router/index.ts                       # 修改：新增 /interview 路由
    views/ReportView.vue                  # 修改：添加"开始面试训练"CTA
    components/report/InterviewQuestionCard.vue  # 保留，报告页继续使用
docs/
  superpowers/specs/2026-05-04-careerfit-agent-phase-2e-interview-training-design.md
  superpowers/plans/2026-05-04-careerfit-agent-phase-2e-interview-training.md
  superpowers/test-plans/2026-05-04-careerfit-agent-phase-2e-test-plan.md
TODOS.md
```

---

## Task 0：计划与文档门

- [x] **Step 1：确认 Phase 2E 范围**

用户已确认面试训练闭环方向。记录范围边界：面试训练会话 + 题目练习 + RAG 补充，不做回答评分和模拟对话。

- [x] **Step 2：创建设计文档**

新增 Phase 2E 设计文档。

- [x] **Step 3：创建实施计划**

本文件。

- [ ] **Step 4：创建测试计划**

- [ ] **Step 5：更新 TODOS**

---

## Task 1：数据库模型

**Files:**

- Modify: `backend/app/db/models.py`

- [ ] **Step 1：新增 InterviewSession 模型**

`interview_sessions` 表：id, report_id (FK), job_title, status, total_questions, completed_questions, metadata_, created_at, updated_at。

- [ ] **Step 2：新增 InterviewQuestion 模型**

`interview_questions` 表：id, session_id (FK), skill, category, difficulty, question, answer_hint, follow_ups (JSON), source, status, notes, sort_order。

- [ ] **Step 3：验证模型在 SQLite 中可创建**

---

## Task 2：Schema 与 Service

**Files:**

- Create: `backend/app/schemas/interview.py`
- Create: `backend/app/services/interview_service.py`

- [ ] **Step 1：写失败测试：创建会话**

测试 `POST /api/interview/sessions` 从报告生成会话。

- [ ] **Step 2：写失败测试：列出会话**

测试 `GET /api/interview/sessions`。

- [ ] **Step 3：写失败测试：获取会话详情**

测试 `GET /api/interview/sessions/{id}` 含题目列表。

- [ ] **Step 4：写失败测试：更新题目状态**

测试 `PATCH /api/interview/sessions/{id}/questions/{qid}`，含状态流转校验。

- [ ] **Step 5：新增 interview schema**

`InterviewSessionCreate`、`InterviewSessionRead`、`InterviewQuestionRead`、`InterviewQuestionUpdate`、`InterviewSessionDetailRead`。

- [ ] **Step 6：实现 interview_service**

`create_session(db, report_id, include_rag)` — 从报告提取题目 + RAG 补充 + 去重 + 分类 + 持久化。
`list_sessions(db, status, limit, offset)` — 列出会话。
`get_session(db, session_id)` — 获取会话详情。
`update_question(db, session_id, question_id, status, notes)` — 更新题目，校验状态流转。

- [ ] **Step 7：实现题目分类逻辑**

`_classify_question(question_text)` — 根据关键词分类为 basic / project_deep_dive / scenario_design。
`_assign_difficulty(skill, category)` — 根据技能和类别分配难度。

- [ ] **Step 8：实现 RAG 面试题补充**

`_enrich_from_rag(db, skills)` — 对每个技能检索 interview 类型文档，解析为结构化题目。

---

## Task 3：API 路由

**Files:**

- Create: `backend/app/api/routes/interview.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1：实现 POST /api/interview/sessions**

- [ ] **Step 2：实现 GET /api/interview/sessions**

- [ ] **Step 3：实现 GET /api/interview/sessions/{id}**

- [ ] **Step 4：实现 PATCH /api/interview/sessions/{id}/questions/{qid}**

- [ ] **Step 5：注册 router 和 capability**

在 `main.py` 注册 `interview.router`，`CAPABILITIES` 新增 `"interview": "ready"`。

- [ ] **Step 6：运行面试 API 测试**

---

## Task 4：前端实现

**Files:**

- Create: `frontend/src/api/interview.ts`
- Create: `frontend/src/stores/interview.ts`
- Create: `frontend/src/views/InterviewListView.vue`
- Create: `frontend/src/views/InterviewDetailView.vue`
- Create: `frontend/src/components/interview/InterviewSessionCard.vue`
- Create: `frontend/src/components/interview/InterviewQuestionCard.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/ReportView.vue`
- Modify: `frontend/src/stores/availability.ts`
- Modify: `frontend/src/api/availability.ts`

- [ ] **Step 1：新增 interview API 客户端**

`createSession(reportId, includeRag)`、`listSessions(status, limit, offset)`、`getSession(id)`、`updateQuestion(sessionId, questionId, status, notes)`。

- [ ] **Step 2：新增 interview Pinia store**

状态：sessions、currentSession、isLoading、error。动作：fetchSessions、fetchSession、createSession、updateQuestion。

- [ ] **Step 3：新增 /interview 路由**

`/interview` → InterviewListView，`/interview/:id` → InterviewDetailView。

- [ ] **Step 4：实现 InterviewListView**

会话卡片列表，显示岗位名称、题目数、完成进度、状态。支持空/加载/错误/后端不可用状态机。

- [ ] **Step 5：实现 InterviewDetailView**

题目列表，按技能/类别/难度筛选。每道题展示技能标签、类别标签、难度标签、问题文本、回答提示（可展开）、追问。练习状态切换和笔记输入。进度条。

- [ ] **Step 6：实现 InterviewSessionCard 组件**

- [ ] **Step 7：实现 InterviewQuestionCard 组件**

- [ ] **Step 8：报告页添加"开始面试训练"CTA**

- [ ] **Step 9：availability store 消费 interview capability**

- [ ] **Step 10：运行前端 typecheck 和 build**

---

## Task 5：全量回归与文档同步

- [ ] **Step 1：后端全量测试**

- [ ] **Step 2：前端全量测试**

- [ ] **Step 3：Docker smoke**

- [ ] **Step 4：文档同步检查**

- [ ] **Step 5：提交 Phase 2E 实现**

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| 题目存储方式 | 独立 interview_questions 表 | 支持独立状态和笔记，优于 JSON 列 | 题目量极小，JSON 列更简单 |
| 会话与报告关系 | 一对一（幂等） | 同一报告不重复创建会话 | 需要同一报告多次训练 |
| RAG 补充时机 | 创建会话时一次性补充 | 避免运行时检索延迟 | 需要动态补充题目 |
| 题目分类方式 | 关键词匹配 | 简单可靠，不需要 LLM | 分类准确率不足 |
| 面试训练页面路由 | /interview + /interview/:id | 与其他模块路由风格一致 | 需要更深层级 |

## 风险与缓解

- **风险：题目分类不准确。** 缓解：关键词匹配覆盖常见模式，分类可手动调整。
- **风险：RAG 面试题质量不够。** 缓解：种子知识库已包含面试题，后续可增量补充。
- **风险：前端面试训练页面复杂度高。** 缓解：先实现核心功能（列表+详情+状态切换），高级筛选后续迭代。
