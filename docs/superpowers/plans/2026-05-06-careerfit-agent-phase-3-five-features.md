# CareerFit Phase 3 — 五大功能拓展实施计划

日期：2026-05-06
版本：v1
状态：计划已完成，待用户确认后开始实施

***

## 总体概述

本计划覆盖五个优先级拓展功能，按依赖关系和实施顺序组织：

| # | 功能                                     | 优先级 | 预估复杂度 | 依赖               |
| - | -------------------------------------- | --- | ----- | ---------------- |
| 1 | Phase 2G 多 Agent 可信分析（含 LangGraph 真接入） | 高   | 高     | 已有设计/测试文档        |
| 2 | PDF/DOCX 简历解析                          | 高   | 中     | 无                |
| 3 | 面试回答评分闭环                               | 高   | 中     | 依赖已有面试系统 (2E)    |
| 4 | 技能雷达图 + 目标岗位对比                         | 中   | 低     | 前端已有雷达图组件        |
| 5 | 后台 Worker + 分析缓存                       | 中   | 低     | 已有线程池 + LLMCache |

***

## 功能 1：Phase 2G 多 Agent 可信分析（含 LangGraph 真接入）

### 现状

- \[llm/agent\_schemas.py]\(file:///e:/New project 2/backend/app/llm/agent\_schemas.py) 已定义全部 10 个 Agent 输出 Schema：`JDParseOutput`、`ResumeParseOutput`、`RagQueryPlanOutput`、`GapAnalysisOutput`、`ResumeSuggestionOutput`、`InterviewQuestionOutput`、`LearningPlanOutput`、`NextBestActionOutput`、`IntegrityCriticOutput`、`SkillDimension`
- \[llm/agent\_service.py]\(file:///e:/New project 2/backend/app/llm/agent\_service.py) 已实现 `run_structured_agent()` 统一执行器（LLM 调用 + 1 次 JSON 修复重试 + Pydantic 校验 + fallback）
- 已有测试文件：`test_agent_schemas.py`、`test_multi_agent_llm_flow.py`、`test_data_analysis_dimension_extraction.py`、`test_rag_relevance_filtering.py`
- **但** \[graph.py]\(file:///e:/New project 2/backend/app/agents/graph.py) 和 \[nodes.py]\(file:///e:/New project 2/backend/app/agents/nodes.py) **尚未更新**，仍然使用旧的线性顺序 runner（无真实多 Agent 分工）
- LangGraph 仅写在 `requirements.txt` 中，实际未接入（D9 决策：adapter-only）

### 目标

1. 将工作流升级为真正的多 Agent 协作：每个 Agent 节点独立调用 LLM，通过结构化 schema 校验
2. 用 LangGraph StateGraph 替代自定义 `run_workflow()` 顺序 runner，获得条件路由、并行 fan-out、checkpointing 能力
3. JD 解析从简单技能词匹配升级为岗位族 + 多维度抽取（至少覆盖 SQL、Python、数据可视化、统计/A/B 测试等）
4. RAG 检索增加岗位族过滤、文档类型过滤和相关性阈值
5. Agent Trace 展示真实执行方式（llm/rule/rag/deterministic）和重试/fallback 细节

### 实施步骤

- [ ] **S1：LangGraph 基础设施**
  - 创建 `backend/app/agents/langgraph_runner.py`：LangGraph StateGraph 版本的工作流 runner
  - 定义 `StateGraph`，注册所有 Agent 节点
  - 实现条件路由：`gap_analyzer` 后根据缺口数量决定是否执行 `resume_optimizer`
  - 实现并行 fan-out：`gap_analyzer` → 同时执行 `interview_coach`、`learning_planner`、`resume_optimizer`
  - 配置 `SqliteSaver`（测试）/ `PostgresSaver`（生产）做 checkpointing
  - 保持与现有 `run_workflow()` 的接口兼容（返回 state + trace）
    验证：`cd backend && pytest tests/test_langgraph_runner.py -q`
- [ ] **S2：升级 JD 解析节点 (`jd_parser`)**
  - 将 \[nodes.py]\(file:///e:/New project 2/backend/app/agents/nodes.py) 中的 `jd_parser` 从正则匹配改为调用 `run_structured_agent()`
  - 使用 `JDParseOutput` schema，产出 `job_family` + `dimensions`（含 weight、required\_level、jd\_evidence、aliases）
  - 降级方案：当 LLM 不可用时保留现有正则匹配逻辑
  - Agent trace 标记执行方式为 `llm` 或 `rule`
    验证：`cd backend && pytest tests/test_data_analysis_dimension_extraction.py -q`
- [ ] **S3：升级简历解析节点 (`resume_parser`)**
  - 改为调用 `run_structured_agent()` 使用 `ResumeParseOutput` schema
  - 产出结构化 skill → evidence 映射，禁止新增简历事实（Integrity Guard 硬约束）
  - 降级方案：保留现有 `parse_resume_profile()`
    验证：`cd backend && pytest tests/test_multi_agent_llm_flow.py -q`
- [ ] **S4：新增 RAG Query Planner Agent**
  - 新增 `rag_query_planner` 节点，在 `rag_retriever` 之前运行
  - 使用 `RagQueryPlanOutput` schema，为每个技能维度生成检索 query、岗位族过滤和文档类型
  - 降级方案：直接使用技能名作为检索词
    验证：`cd backend && pytest tests/test_rag_relevance_filtering.py -q`
- [ ] **S5：升级 RAG 检索节点**
  - 增加岗位族过滤（`job_family` 字段匹配）
  - 增加文档类型过滤（`doc_types` 字段匹配）
  - 增加相关性阈值（embedding 相似度 < 阈值则标记为"知识库证据不足"）
  - 低相关结果不编造来源
    验证：`cd backend && pytest tests/test_rag_relevance_filtering.py -q`
- [ ] **S6：拆分 LLM 增强节点**
  - 将当前单一 `generate_report_enhancement()` 调用拆分为 5 个独立 Agent：
    - `resume_optimizer` → `ResumeSuggestionOutput`
    - `interview_coach` → `InterviewQuestionOutput`
    - `learning_planner` → `LearningPlanOutput`
    - `next_best_action` → `NextBestActionOutput`
    - `integrity_critic`（新增）→ `IntegrityCriticOutput`
  - 每个独立调用 `run_structured_agent()`，拥有独立的 fallback
  - `integrity_critic` 只能辅助解释风险，不能替代硬规则 Integrity Guard
    验证：`cd backend && pytest tests/test_agent_schemas.py -q`
- [ ] **S7：Agent Trace 增强**
  - `execution_meta` 包含：`execution_mode`（llm/rule/rag/deterministic）、`model_name`、`fallback_used`、`schema_valid`、`retry_count`
  - 节点输出 snapshot 不含完整 JD、简历、prompt、API key
  - 确保后端 `AgentRun` 响应与前端 `agentRuns.ts` normalize 层对齐
    验证：`cd backend && pytest tests/test_agent_schemas.py -q`
- [ ] **S8：前端 Phase 2G**
  - \[AgentTraceRow\.vue]\(file:///e:/New project 2/frontend/src/components/report/AgentTraceRow\.vue) 展示真实执行方式（LLM / 规则 / RAG / 确定性）
  - Agent 节点名通俗化（如 `jd_parser` → "解析岗位要求"）
  - Trace 展示 fallback 状态、schema 校验、JSON 修复重试次数
  - 报告页增加折叠策略，避免 Phase 2G 维度增多后纵向堆叠
  - 知识库证据只展示相关文档，无相关时显示"知识库证据不足"
    验证：`cd frontend && npm test -- AgentTraceTimeline && npm test -- ReportView`
- [ ] **S9：全面验证**
  - 后端全量测试：`cd backend && pytest -q`
  - 前端全量测试：`cd frontend && npm test && npm run typecheck && npm run build`
  - Docker：`docker compose up --build`，使用数据分析师 JD/简历完成端到端分析
  - PII：运行本地等价 OWASP + STRIDE 审计

### 决策记录：LangGraph 真接入

| 项目     | 内容                                                                                                                                              |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **选择** | 从 adapter-only 升**级为 LangG**raph StateGraph 真接入                                                                                                 |
| **理由** | Phase 2G 需要条件路由（跳过无缺口场景）、并行 fan-out（5 个 Agent 同时执行）、checkpointing（节点级状态持久化）；自定义 runner 已无法低成本满足这些需求                                             |
| **影响** | 替换 \[graph.py]\(file:///e:/New project 2/backend/app/agents/graph.py) 中的 `run_workflow()`；新增 `langgraph_runner.py`；nodes.py 保持不变（只修改 node 内部逻辑） |
| **回滚** | 若 LangGraph 行为不如预期，保留旧 `run_workflow()` 作为 `CAREERFIT_USE_LANGGRAPH=0` 时的降级路径                                                                   |

***

## 功能 2：PDF/DOCX 简历解析

### 现状

- 当前简历输入为纯文本框，用户需手动粘贴
- `resume_service.py` 中的 `parse_resume_profile()` 基于纯文本工作
- Phase 1 明确禁止引入 PDF/DOCX 解析依赖直到"文本输入端到端跑通"

### 目标

1. 支持上传 PDF（`.pdf`）和 Word（`.docx`）文件
2. 自动提取文本内容，传入现有解析管线
3. 安全校验：文件类型白名单、大小限制、PII 不落地日志
4. 前端上传 UI 集成到简历创建/编辑页

### 实施步骤

- [ ] **S1：添加 PDF/DOCX 解析依赖**
  - 安装 `pdfplumber`（PDF 文本提取，比 PyPDF2 更准确）
  - 安装 `python-docx`（DOCX 文本提取）
  - 更新 `requirements.txt` 和 `pyproject.toml`
    验证：`cd backend && pip install pdfplumber python-docx`
- [ ] **S2：新增文件解析服务**
  - 创建 `backend/app/services/file_parser.py`
  - `parse_pdf(file_bytes: bytes) -> str`：使用 pdfplumber 提取文本，按页组织
  - `parse_docx(file_bytes: bytes) -> str`：使用 python-docx 提取段落文本
  - `parse_upload(file_bytes: bytes, filename: str) -> str`：根据扩展名分发
  - 所有错误统一为 `FileParseError`，含用户提示信息
  - 解析后的文本不写入日志
    验证：`cd backend && pytest tests/test_file_parser.py -q`
- [ ] **S3：新增上传 API**
  - `POST /api/resumes/upload`：multipart/form-data 接收文件
  - 校验：扩展名白名单 `.pdf,.docx`、MIME 类型校验、文件大小限制（默认 5MB）
  - 自动创建简历记录并解析，返回 `ResumeResponse`
  - 并行保留现有 `POST /api/resumes` 纯文本创建路径
    验证：`cd backend && pytest tests/test_resume_upload_api.py -q`
- [ ] **S4：前端上传 UI**
  - \[ResumeDetailView\.vue]\(file:///e:/New project 2/frontend/src/views/ResumeDetailView\.vue) / \[ResumesView\.vue]\(file:///e:/New project 2/frontend/src/views/ResumesView\.vue) 增加"上传文件"入口
  - 拖拽上传区域（drag & drop）+ 点击选择文件
  - 文件类型/大小前端预校验
  - 上传进度指示
  - 上传成功后自动填充文本框（供用户确认/编辑）
    验证：`cd frontend && npm test && npm run typecheck && npm run build`
- [ ] **S5：安全审计**
  - PII：上传文件不落地磁盘（仅内存处理）；解析文本不记日志；API Key 不入 trace
  - 运行本地等价 OWASP + STRIDE 审计
    验证：记录到 `docs/superpowers/review-logs/2026-05-06-phase-3-file-upload-security-review.md`

***

## 功能 3：面试回答评分闭环

### 现状

- Phase 2E 已有面试训练系统：`interview_sessions` 和 `interview_questions` 持久化
- 题目支持状态流转（not\_started → practicing → completed / skipped）
- **缺失**：用户无法提交回答、无法获得评分和反馈

### 目标

1. 用户可以为面试题提交文本/语音风格的回答
2. LLM 对回答进行评分（正确性、完整性、表达清晰度）
3. 给出具体改进建议
4. 形成"答题 → 评分 → 改进 → 再答"的练习闭环

### 实施步骤

- [ ] **S1：扩展数据模型**
  - 在 `interview_questions` 表增加字段：`answer_text`、`answer_score`、`answer_feedback`、`answer_submitted_at`、`attempt_count`
  - 新增 Alembic 迁移（若已有迁移系统）或在模型中直接加字段
  - `answer_score` 为 0-100 整数
    验证：`cd backend && pytest -q`（确保现有测试不退化）
- [ ] **S2：新增回答评分服务**
  - 在 \[interview\_service.py]\(file:///e:/New project 2/backend/app/services/interview\_service.py) 新增 `score_answer(question, answer_text)`
  - 使用 `run_structured_agent()` 调用 LLM 评分
  - Schema：`AnswerScoreOutput(BaseModel)` 含 `score`、`correctness_feedback`、`completeness_feedback`、`clarity_feedback`、`improvement_suggestion`
  - 降级方案：LLM 不可用时给默认反馈"继续练习，尝试用自己的话复述核心概念"
    验证：`cd backend && pytest tests/test_interview_answer_scoring.py -q`
- [ ] **S3：新增提交回答 API**
  - `POST /api/interview/sessions/{id}/questions/{qid}/submit`
  - 请求体：`{"answer_text": "..."}`
  - 响应：更新后的 question 对象，含 score 和 feedback
  - 状态自动流转：not\_started → practicing（首次提交）→ 保持 practicing（允许重新提交）
    验证：`cd backend && pytest tests/test_interview_api.py -q`
- [ ] **S4：前端答题 UI**
  - \[InterviewDetailView\.vue]\(file:///e:/New project 2/frontend/src/views/InterviewDetailView\.vue) 每个题目增加答题区：
    - 文本输入框（textarea，2000 字限制）
    - "提交回答"按钮（loading 状态）
    - 评分展示（数字分 + 彩色进度条）
    - 分维度反馈（正确性/完整性/清晰度）
    - 改进建议
    - "重新作答"按钮
  - 完成状态追踪（已答/未答计数）
    验证：`cd frontend && npm test && npm run typecheck && npm run build`

***

## 功能 4：技能雷达图 + 目标岗位对比

### 现状

- 前端已有 \[SkillsRadarChart.vue]\(file:///e:/New project 2/frontend/src/components/report/SkillsRadarChart.vue)：支持雷达图 + 柱状图双模式，暗色模式，响应式
- 报告 API 返回 `score_items` 含 `name`、`score`、`threshold`
- **缺失**：
  - 雷达图组件在报告页中已加载但没有独立展示入口
  - 缺少多岗位横向对比功能

### 目标

1. 在报告页显眼位置展示雷达图
2. 新增目标岗位对比功能：选择 2-3 个岗位，横向对比技能维度要求
3. 可视化差异，帮助用户做求职方向决策

### 实施步骤

- [ ] **S1：增强报告页雷达图展示**
  - 在 \[ReportView\.vue]\(file:///e:/New project 2/frontend/src/views/ReportView\.vue) 中评分概览卡片之上/旁展示 `<SkillsRadarChart>`
  - 确保 `Dimension` 类型与报告 API 返回字段对齐（`name`、`score`、`threshold`）
  - 响应式布局：桌面端雷达图占报告宽度 50%，移动端全宽
    验证：`cd frontend && npm test -- ReportView && npm run build`
- [ ] **S2：新增岗位对比后端 API**
  - `POST /api/jobs/compare`：请求体 `{"job_ids": [1, 2, 3]}`
  - 对每个岗位解析 JD profile，提取技能维度
  - 返回对比矩阵：`[{job_id, job_title, dimensions: [{name, threshold}]}]`
  - 若岗位尚未分析过，仅返回维度要求（无用户匹配分）
    验证：`cd backend && pytest tests/test_job_comparison_api.py -q`
- [ ] **S3：前端岗位对比页面**
  - 在 \[JobsView\.vue]\(file:///e:/New project 2/frontend/src/views/JobsView\.vue) 增加"对比模式"切换
  - 选中 2-3 个岗位后点击"开始对比"
  - 对比视图：并列雷达图（每个岗位一条线）+ 维度差异表格
  - 差异高亮：某个维度 A 岗位要求 > B 岗位时加色提示
    验证：`cd frontend && npm test && npm run typecheck && npm run build`

***

## 功能 5：后台 Worker + 分析缓存

### 现状

- 已有 \[AnalysisThreadPool]\(file:///e:/New project 2/backend/app/core/thread\_pool.py)：`ThreadPoolExecutor(max_workers=5)` 管理后台分析任务
- 已有 \[LLMCache]\(file:///e:/New project 2/backend/app/llm/cache.py)：内存 TTL 缓存（3600s），基于输入 hash，带命中率统计
- 已有 `llm/client_cache.py` 和 `api/routes/analysis_cache.py`
- `POST /api/analysis` 当前是同步返回 task 后异步执行

### 目标

1. 分析任务完成后，对相同 JD + 相同简历的组合做分析结果缓存（完整报告级别，非仅 LLM 级别）
2. 用户再次分析相同组合时，在合理时间内（如 1 小时）返回缓存结果而非重新计算
3. 添加缓存状态查询和管理接口
4. 线程池增加健康检查和监控指标

### 实施步骤

- [ ] **S1：实现分析结果缓存服务**
  - 新增 `backend/app/services/analysis_cache_service.py`
  - 缓存 key：`hash(job_id + resume_id + schema_version)`
  - 缓存内容：完整 `AnalysisReport` 数据 + `AgentRun` 列表
  - TTL：默认 3600 秒（1 小时），可通过环境变量配置
  - 存储：内存字典（与 LLMCache 风格一致）或 SQLite 表
    验证：`cd backend && pytest tests/test_analysis_cache_service.py -q`
- [ ] **S2：集成缓存到分析流程**
  - \[analysis\_service.py]\(file:///e:/New project 2/backend/app/services/analysis\_service.py) 中 `create_analysis()` 先查缓存
  - 命中 → 直接复用已有 report 和 agent\_runs，标记 `from_cache: true`
  - 未命中 → 正常执行，完成后写入缓存
  - 缓存标记写入 API 响应，前端可展示"数据来自缓存"
    验证：`cd backend && pytest tests/test_analysis_flow.py -q`
- [ ] **S3：新增缓存管理 API**
  - 利用已有 `api/routes/analysis_cache.py`：
    - `GET /api/cache/stats`：命中率、缓存条目数、TTL
    - `POST /api/cache/clear`：手动清空缓存
  - `/api/capabilities` 增加 `cache` 状态字段
    验证：`cd backend && pytest tests/test_analysis_cache_service.py -q`
- [ ] **S4：线程池健康监控**
  - 在 `AnalysisThreadPool` 增加：队列长度、平均等待时间、失败任务数
  - `GET /api/health/workers` 返回线程池状态
    验证：`cd backend && pytest tests/test_health.py -q`

***

## 测试矩阵

| 测试目标      | 命令                                                              | 成功标准        |
| --------- | --------------------------------------------------------------- | ----------- |
| 后端全量      | `cd backend && pytest -q`                                       | 全部通过        |
| 前端全量      | `cd frontend && npm test && npm run typecheck && npm run build` | 全部通过        |
| Docker 集成 | `docker compose up --build`                                     | 三容器 healthy |
| PII 审计    | 本地等价 OWASP + STRIDE                                             | 无新增泄露面      |
| 文档检查      | `git diff --check`                                              | 无格式错误       |

***

## 评估监测

每个功能完成后记录评估指标：

| 指标       | Phase 2G | 简历解析                    | 面试评分 | 雷达图    | Worker+缓存 |
| -------- | -------- | ----------------------- | ---- | ------ | --------- |
| 新增测试数    | ≥ 15     | ≥ 8                     | ≥ 8  | ≥ 5    | ≥ 6       |
| 新增 API 数 | 0（升级）    | 1                       | 1    | 1      | 1         |
| 新增依赖     | 无        | pdfplumber, python-docx | 无    | 无      | 无         |
| 前端路由变更   | 无        | 无                       | 无    | 无（改现有） | 无         |

***

## 外延后事项（不进入本次范围）

- 更多岗位族知识库（数据科学、安全、嵌入式等）
- 每周求职进展总结
- 国际化 i18n
- 离线模式 / PWA
- 富文本简历编辑器
- 协作分享只读链接

