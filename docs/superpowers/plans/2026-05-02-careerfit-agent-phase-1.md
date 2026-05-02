# CareerFit Agent Phase 1 实施计划

> **给智能执行代理的要求：** 实施本计划时必须使用 `superpowers:subagent-driven-development`，推荐方式；或使用 `superpowers:executing-plans`。执行时必须逐项更新 checklist，把完成的步骤从 `- [ ]` 改成 `- [x]`。

**目标：** 实现第一条可信端到端主路径：创建目标岗位、创建简历版本、执行确定性 JD-简历分析、持久化带证据链的报告、暴露 Agent 轨迹，并在 Vue3 工作台展示结果。

**架构：** 后端使用 FastAPI、SQLAlchemy、Pydantic、PostgreSQL/pgvector 和 LangGraph-compatible workflow boundary。Phase 1 把 LLM 调用封装在可替换 Agent 节点接口后面，并提供规则化本地 fallback，保证开发环境没有付费模型也能跑通核心流程。

**技术栈：** FastAPI、Pydantic、SQLAlchemy、PostgreSQL、pgvector、LangGraph、Vue3、TypeScript、Vite、Docker Compose、pytest、Vitest、Playwright。

---

## 范围

本计划只实现 Phase 1。明确不做登录、HR 流程、导师看板、PDF/DOCX 解析、完整面试会话和生产级后台 worker。

Phase 1 必须证明核心信任链路：

```text
准备种子知识库
  -> 创建目标岗位
  -> 创建简历版本
  -> 解析岗位和简历
  -> 检索能力标准
  -> 执行确定性评分
  -> 生成带证据链的报告
  -> 阻止无证据建议
  -> 持久化运行轨迹
  -> 展示报告和下一步最佳行动
```

## 文件结构

需要创建以下结构：

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
  src/
    App.vue
    main.ts
    api/client.ts
    api/jobs.ts
    api/resumes.ts
    api/analysis.ts
    api/reports.ts
    components/AgentTimeline.vue
    components/EvidenceTable.vue
    components/ScoreBreakdown.vue
    components/StatusBadge.vue
    views/WorkspaceView.vue
    views/ReportView.vue
  tests/WorkspaceView.test.ts
docker-compose.yml
```

分层职责：

- API routes 只处理 HTTP 请求和响应。
- Services 编排数据库、评分和 workflow。
- Agents 负责结构化中间结果和 trace。
- Scoring 只放确定性评分逻辑。
- RAG 负责种子知识、chunk、embedding 和 retrieval。
- Frontend views 组合可复用组件。

## Task 1：后端项目骨架

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

在 `backend/app/main.py` 中实现 `create_app()`，启动时调用 `Base.metadata.create_all(bind=engine)`，并提供 `/health`。

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

## Task 2：目标岗位和简历 API

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

- [ ] **Step 7：注册路由**

在 `backend/app/main.py` 中 include `jobs.router` 和 `resumes.router`。

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

## Task 3：确定性评分和 Integrity Guard

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
- 无证据“主导/生产级/架构设计”触发 `unsupported_leadership_claim`。
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

需要识别百分比、倍数、ms 指标，以及“主导”“负责架构”“生产级”等领导力或生产化表述。

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

## Task 4：分析工作流和报告

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

- [ ] **Step 7：注册路由**

在 `main.py` 中 include `analysis`、`reports`、`agent_runs`。

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

## Task 5：前端工作台和报告页

**文件：**

- 创建 `frontend/package.json`
- 创建 `frontend/index.html`
- 创建 `frontend/tsconfig.json`
- 创建 `frontend/vite.config.ts`
- 创建 `frontend/src/main.ts`
- 创建 `frontend/src/App.vue`
- 创建 `frontend/src/api/client.ts`
- 创建 `frontend/src/api/jobs.ts`
- 创建 `frontend/src/api/resumes.ts`
- 创建 `frontend/src/api/analysis.ts`
- 创建 `frontend/src/api/reports.ts`
- 创建 `frontend/src/components/StatusBadge.vue`
- 创建 `frontend/src/components/ScoreBreakdown.vue`
- 创建 `frontend/src/components/EvidenceTable.vue`
- 创建 `frontend/src/components/AgentTimeline.vue`
- 创建 `frontend/src/views/WorkspaceView.vue`
- 创建 `frontend/src/views/ReportView.vue`
- 创建 `frontend/tests/WorkspaceView.test.ts`

- [ ] **Step 1：创建前端 package**

`package.json` 包含 Vue3、Vite、TypeScript、Vitest、Vue Test Utils、jsdom。脚本包含：

```text
npm run dev
npm run build
npm test
```

- [ ] **Step 2：创建 TypeScript 和 Vite 配置**

`tsconfig.json` 开启严格模式，包含 `src/**/*.ts`、`src/**/*.vue`、`tests/**/*.ts`。

`vite.config.ts` 使用 `@vitejs/plugin-vue`，Vitest 环境为 `jsdom`。

- [ ] **Step 3：创建 app shell**

`App.vue` 组合 `WorkspaceView` 和 `ReportView`。当分析完成后，把 `taskId` 传给报告页。

- [ ] **Step 4：创建 API client**

`client.ts` 封装 `requestJson<T>()`，默认 `VITE_API_BASE` 为 `http://localhost:8000`。

按资源拆分：

- `jobs.ts`
- `resumes.ts`
- `analysis.ts`
- `reports.ts`

- [ ] **Step 5：创建组件**

实现：

- `StatusBadge.vue`
- `ScoreBreakdown.vue`
- `AgentTimeline.vue`
- `EvidenceTable.vue`

组件必须有基本可访问性标签，风险状态不能只靠颜色表达。

- [ ] **Step 6：创建页面**

`WorkspaceView.vue`：展示 JD textarea、简历 textarea、开始分析按钮、运行状态和错误状态。

`ReportView.vue`：展示总分、Next Best Action、分项评分、优势、缺口和 Agent 时间线。

- [ ] **Step 7：创建前端 smoke test**

`WorkspaceView.test.ts` 断言页面包含“个人求职成长工作台”“目标岗位 JD”“当前简历版本”。

- [ ] **Step 8：运行前端测试**

```powershell
cd frontend
npm install
npm test
```

- [ ] **Step 9：提交**

```powershell
git add frontend
git commit -m "feat: add frontend workspace and report view"
```

## Task 6：Docker Compose 和冒烟验证

**文件：**

- 创建 `backend/Dockerfile`
- 创建 `frontend/Dockerfile`
- 创建 `docker-compose.yml`
- 创建 `.env.example`

- [ ] **Step 1：添加后端 Dockerfile**

后端镜像基于 `python:3.11-slim`，安装 `pyproject.toml` 依赖，启动命令为：

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- [ ] **Step 2：添加前端 Dockerfile**

前端镜像基于 `node:20-alpine`，执行 `npm install`，启动 `npm run dev`。

- [ ] **Step 3：添加 `.env.example`**

包含：

```text
CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit
VITE_API_BASE=http://localhost:8000
```

- [ ] **Step 4：添加 Docker Compose**

`docker-compose.yml` 包含：

- `postgres`：使用 `pgvector/pgvector:pg16`。
- `backend`：依赖 postgres healthcheck。
- `frontend`：依赖 backend。

端口：

```text
postgres 5432
backend 8000
frontend 5173
```

- [ ] **Step 5：运行 Docker 冒烟测试**

```powershell
docker compose up --build
```

验证：

- backend 监听 `0.0.0.0:8000`。
- frontend 监听 `0.0.0.0:5173`。
- postgres healthy。
- 打开 `http://localhost:5173`。
- 点击“开始分析”能生成报告。
- 报告展示总分、Next Best Action 和 Agent 时间线。

- [ ] **Step 6：提交**

```powershell
git add backend/Dockerfile frontend/Dockerfile docker-compose.yml .env.example
git commit -m "chore: add docker compose setup"
```

## Task 7：最终验证和 README

**文件：**

- 创建 `README.md`

- [ ] **Step 1：添加 README**

README 必须使用中文，包含：

- 项目简介。
- 技术栈。
- 本地运行命令。
- 前端地址 `http://localhost:5173`。
- 后端地址 `http://localhost:8000`。
- Phase 1 功能列表。

- [ ] **Step 2：运行全部后端测试**

```powershell
cd backend
pytest -q
```

- [ ] **Step 3：运行全部前端测试**

```powershell
cd frontend
npm test
```

- [ ] **Step 4：构建 Docker stack**

```powershell
docker compose up --build
```

- [ ] **Step 5：提交 README**

```powershell
git add README.md
git commit -m "docs: add project README"
```

## 自检清单

- [ ] Phase 1 信任闭环已实现。
- [ ] 每次分析都会产生报告。
- [ ] 每个报告都有分项评分。
- [ ] 每个报告都有 Next Best Action。
- [ ] Agent trace 对原始 JD 和简历文本脱敏。
- [ ] 评分是确定性的，并有测试覆盖。
- [ ] Integrity Guard 有测试覆盖。
- [ ] Docker Compose 能启动所有服务。
- [ ] README 说明如何运行项目。
