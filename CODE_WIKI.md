# CareerFit Agent 项目代码百科

> 本文档为 CareerFit Agent 项目的结构化代码参考文档，包含项目架构、模块职责、关键类函数说明、依赖关系和运行方式等核心信息。

---

## 一、项目概览

### 1.1 项目定位

CareerFit Agent 是一个面向计算机应届生的**个人求职成长工作台**，核心功能闭环为：

```
目标岗位 → 简历版本 → 匹配分析 → 证据链评分 → 能力缺口 → 诚实简历优化 → Next Best Action → 学习任务 → 新简历版本 → 再分析和趋势对比
```

### 1.2 技术栈

| 层级 | 技术选型 |
|------|---------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | PostgreSQL + pgvector（向量存储） |
| LLM 集成 | OpenAI Compatible API + LangGraph |
| 前端框架 | Vue 3 + TypeScript + Pinia |
| 状态管理 | Pinia Store |
| 路由 | Vue Router 4 |
| 构建工具 | Vite |
| 容器化 | Docker Compose |

### 1.3 目录结构

```
e:\New project 2/
├── backend/                    # 后端应用
│   ├── app/
│   │   ├── agents/            # Agent 工作流编排（LangGraph 节点）
│   │   ├── api/routes/        # API 路由定义
│   │   ├── core/              # 核心配置与工具
│   │   ├── db/                # 数据库模型与会话管理
│   │   ├── llm/               # LLM 客户端与服务
│   │   ├── rag/               # 检索增强生成模块
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── scoring/            # 确定性评分规则
│   │   ├── services/          # 业务服务层
│   │   └── main.py            # FastAPI 应用入口
│   ├── seeds/                 # 种子数据
│   └── tests/                 # 后端测试
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API 调用封装
│   │   ├── components/        # Vue 组件
│   │   ├── composables/       # 组合式函数
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── styles/            # 全局样式
│   │   ├── utils/             # 工具函数
│   │   ├── views/             # 页面视图
│   │   ├── App.vue            # 根组件
│   │   └── main.ts            # 前端入口
│   └── tests/                 # 前端测试
├── docs/                       # 文档
├── docker-compose.yml          # Docker 编排配置
└── AGENTS.md                   # 项目协作约束
```

---

## 二、后端架构

### 2.1 模块职责分层

```
┌─────────────────────────────────────────────────────────┐
│                    API Routes 层                         │
│         (仅做参数接收、依赖注入、响应返回)                   │
├─────────────────────────────────────────────────────────┤
│                    Service 层                            │
│         (编排用例：创建分析、运行工作流、写入报告)            │
├─────────────────────────────────────────────────────────┤
│                    Agent 层                              │
│         (节点输入输出、prompt/fallback、trace)            │
├─────────────────────────────────────────────────────────┤
│                    Scoring 层                            │
│         (确定性评分逻辑，不调用 LLM、不访问 DB)            │
├─────────────────────────────────────────────────────────┤
│                    RAG 层                               │
│         (种子知识、chunk、embedding、retrieval)           │
├─────────────────────────────────────────────────────────┤
│                    DB 层                                 │
│         (SQLAlchemy ORM 模型与会话管理)                   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 API 路由模块

**路由文件位于**: `backend/app/api/routes/`

| 路由模块 | 前缀 | 职责 |
|---------|------|------|
| `jobs.py` | `/api/jobs` | 目标岗位 CRUD 操作 |
| `resumes.py` | `/api/resumes` | 简历版本 CRUD 操作 |
| `analysis.py` | `/api/analysis` | 分析任务创建与进度追踪 |
| `reports.py` | `/api/reports` | 分析报告查询 |
| `agent_runs.py` | `/api/agent_runs` | Agent 运行轨迹查询 |
| `learning.py` | `/api/learning` | 学习任务管理 |
| `interview.py` | `/api/interview` | 面试题管理 |
| `knowledge.py` | `/api/knowledge` | 知识库文档管理 |
| `llm.py` | `/api/llm` | LLM 能力查询 |
| `system.py` | `/api/system` | 系统级查询 |

### 2.3 核心服务

#### 2.3.1 Analysis Service

**文件**: `backend/app/services/analysis_service.py`

```python
# 核心函数
def create_analysis(db, payload: AnalysisCreate) -> AnalysisTask
    描述: 创建分析任务，支持缓存命中、同步/异步执行
    参数: 
        - db: 数据库会话
        - payload: AnalysisCreate (job_id, resume_id, mode)
    返回: AnalysisTask
    
def get_report_by_task(db, task_id) -> AnalysisReport | None
    描述: 根据任务ID获取分析报告
    
def get_analysis_task(db, task_id) -> AnalysisTask | None
    描述: 根据任务ID获取分析任务
    
def list_agent_runs(db, task_id) -> list[AgentRun]
    描述: 获取任务的 Agent 运行轨迹
```

#### 2.3.2 Job Service

**文件**: `backend/app/services/job_service.py`

```python
# 核心函数
def parse_job_profile(raw_text: str) -> dict
    描述: 解析职位描述文本，提取技能维度和证据
    返回: {
        schema_version, job_family, skill_dimensions, 
        required_skills, preferred_skills, domain_keywords,
        basic_requirements, evidence
    }
    
def create_job(db, payload: JobCreate) -> JobDescription
def list_jobs(db) -> list[JobDescription]
def get_job(db, job_id) -> JobDescription | None
def compare_jobs(db, job_ids) -> list[dict]
```

**技能目录**: `SKILL_CATALOG` 包含 50+ 技术技能的标准定义，包括：
- 编程语言: Python, Java, Go, JavaScript, TypeScript, C++, C#, Rust
- 后端框架: FastAPI, Django, Flask, Spring, Express
- 数据库: PostgreSQL, MySQL, MongoDB, Redis, SQL, Elasticsearch
- 前端框架: React, Vue, Angular
- DevOps: Docker, Kubernetes, AWS, 阿里云, CI/CD, Git, Linux
- AI/ML: 机器学习, 深度学习, LLM, RAG, LangChain, Prompt Engineering
- 数据科学: 数据分析, 数据可视化, 统计方法, A/B 测试

### 2.4 Agent 工作流

**文件**: `backend/app/agents/`

#### 2.4.1 工作流节点序列

```python
NODE_SEQUENCE = [
    ("jd_parser", nodes.jd_parser),              # JD 解析
    ("resume_parser", nodes.resume_parser),      # 简历解析
    ("rag_query_planner", nodes.rag_query_planner),  # 检索策略规划
    ("rag_retriever", nodes.rag_retriever),      # 知识库检索
    ("match_scorer", nodes.match_scorer),        # 匹配评分（确定性）
    ("gap_analyzer", nodes.gap_analyzer),        # 缺口分析
    ("resume_optimizer", nodes.resume_optimizer), # 简历优化
    ("interview_coach", nodes.interview_coach),  # 面试题生成
    ("learning_planner", nodes.learning_planner), # 学习计划
    ("next_best_action", nodes.next_best_action), # 下一步行动
]
```

#### 2.4.2 LLM 节点 vs 确定性节点

```python
LLM_NODES = {"resume_optimizer", "interview_coach", "learning_planner", "next_best_action"}
# 确定性节点: jd_parser, resume_parser, rag_query_planner, rag_retriever, match_scorer, gap_analyzer
```

#### 2.4.3 核心节点函数

| 节点名 | 文件 | 职责 | 备选方案 |
|--------|------|------|---------|
| `jd_parser` | `nodes.py:102` | 提取 JD 技能维度 | 规则引擎 fallback |
| `resume_parser` | `nodes.py:237` | 解析简历技能和项目 | 规则引擎 fallback |
| `match_scorer` | `nodes.py:502` | 确定性评分计算 | 无（确定性） |
| `gap_analyzer` | `nodes.py:509` | 分析能力缺口 | 本地 gap 分析 |
| `resume_optimizer` | `nodes.py:761` | 生成简历优化建议 | 本地建议生成 |
| `interview_coach` | `nodes.py:826` | 生成面试题 | 本地题目生成 |
| `next_best_action` | `nodes.py:955` | 推荐下一步行动 | 本地 NBA 生成 |

### 2.5 评分系统

**文件**: `backend/app/scoring/`

#### 2.5.1 评分版本

当前版本: `deterministic-v3`

#### 2.5.2 评分维度权重

```python
权重分配:
- skill_score: 45%           # 技能匹配得分
- project_score: 25%          # 项目经验得分
- domain_score: 10%          # 领域匹配得分
- basic_requirement_score: 10%  # 基础要求满足度
- expression_score: 10%       # 表达能力得分
- integrity_risk_penalty: 5%  # 诚信风险扣分
```

#### 2.5.3 核心评分函数

```python
# 文件: backend/app/scoring/rules.py
def score_match(jd_profile, resume_profile, rag_results=None) -> dict
    描述: 计算 JD 与简历的匹配得分
    返回: {
        scoring_version, final_score, score_breakdown, score_items
    }
    
# 关键子函数
def _score_skill(skill, resume_profile) -> tuple[level, weight, evidence]
    描述: 评估技能掌握程度（deep_experience/project_practice/basic_usage/mentioned/not_mentioned）
    
def _compute_integrity_penalty(score_items, resume_profile) -> float
    描述: 基于低分项比例计算诚信风险扣分
```

### 2.6 数据库模型

**文件**: `backend/app/db/models.py`

#### 2.6.1 核心数据表

| 模型名 | 表名 | 用途 |
|--------|------|------|
| `JobDescription` | `job_descriptions` | 目标岗位存储 |
| `ResumeVersion` | `resume_versions` | 简历版本存储 |
| `AnalysisTask` | `analysis_tasks` | 分析任务状态追踪 |
| `AnalysisReport` | `analysis_reports` | 分析报告结果 |
| `LearningTask` | `learning_tasks` | 学习任务管理 |
| `AgentRun` | `agent_runs` | Agent 节点执行轨迹 |
| `KnowledgeDocument` | `knowledge_documents` | 知识库文档 |
| `InterviewSession` | `interview_sessions` | 面试练习会话 |
| `InterviewQuestion` | `interview_questions` | 面试题目 |

#### 2.6.2 分析报告结构

```python
AnalysisReport.final_score: int          # 综合得分 0-100
AnalysisReport.score_breakdown: dict     # 分项得分
AnalysisReport.strengths: list          # 优势列表
AnalysisReport.gaps: list               # 能力缺口列表
AnalysisReport.resume_suggestions: list # 简历优化建议
AnalysisReport.interview_questions: list # 面试题列表
AnalysisReport.learning_plan: list      # 学习计划
AnalysisReport.next_best_action: dict   # 下一步行动
AnalysisReport.evidence: list           # 评分证据链
```

---

## 三、前端架构

### 3.1 页面路由

**文件**: `frontend/src/router/index.ts`

| 路径 | 名称 | 组件 | 职责 |
|------|------|------|------|
| `/` | workspace | `WorkspaceView` | 工作台首页 |
| `/jobs` | jobs | `JobsView` | 岗位管理 |
| `/jobs/:id` | job-detail | `JobDetailView` | 岗位详情 |
| `/resumes` | resumes | `ResumesView` | 简历管理 |
| `/resumes/:id` | resume-detail | `ResumeDetailView` | 简历详情 |
| `/analyses/new` | analysis-run | `AnalysisRunView` | 执行分析 |
| `/reports/:taskId` | report | `ReportView` | 分析报告 |
| `/history` | history | `HistoryView` | 历史趋势 |
| `/diff` | version-diff | `VersionDiffView` | 版本对比 |
| `/learning` | learning | `LearningTasksView` | 学习任务 |
| `/interview` | interview-list | `InterviewListView` | 面试题列表 |
| `/interview/:id` | interview-detail | `InterviewDetailView` | 面试题详情 |
| `/interview-bank` | interview-bank | `InterviewBankView` | 面试题库 |
| `/trace/:taskId` | agent-trace | `AgentTraceView` | Agent 运行轨迹 |
| `/settings` | settings | `SettingsView` | 设置页面 |

### 3.2 状态管理 (Pinia Stores)

**目录**: `frontend/src/stores/`

| Store | 文件 | 职责 |
|-------|------|------|
| `useJobsStore` | `jobs.ts` | 岗位列表、选中状态、对比功能 |
| `useResumesStore` | `resumes.ts` | 简历列表、选中状态 |
| `useAnalysesStore` | `analyses.ts` | 分析任务状态 |
| `useHistoryStore` | `history.ts` | 历史记录与趋势数据 |
| `useLearningStore` | `learning.ts` | 学习任务管理 |
| `useInterviewStore` | `interview.ts` | 面试题练习 |
| `useResumeDiffStore` | `resumeDiff.ts` | 简历版本对比 |
| `useAvailabilityStore` | `availability.ts` | 后端能力探测 |
| `usePreferencesStore` | `preferences.ts` | 用户偏好设置 |

### 3.3 API 客户端

**文件**: `frontend/src/api/client.ts`

```typescript
// API 基础配置
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
const DEFAULT_TIMEOUT = 120000  // 120秒超时（分析任务耗时较长）

// 核心方法
export const apiClient = {
  get<T>(path, options?): Promise<ApiResponse<T>>
  post<T>(path, body, options?): Promise<ApiResponse<T>>
  put<T>(path, body, options?): Promise<ApiResponse<T>>
  patch<T>(path, body, options?): Promise<ApiResponse<T>>
  delete<T>(path, options?): Promise<ApiResponse<T>>
}

// API 模块
export * from './jobs'       // 岗位 API
export * from './resumes'    // 简历 API
export * from './analysis'    // 分析 API
export * from './reports'    // 报告 API
export * from './learning'   // 学习任务 API
export * from './interview'  // 面试题 API
```

### 3.4 核心组件

#### 3.4.1 布局组件

| 组件 | 路径 | 职责 |
|------|------|------|
| `AppShell` | `components/layout/` | 应用外壳，集成导航栏 |
| `SideNav` | `components/layout/` | 侧边导航 |
| `MobileNav` | `components/layout/` | 移动端导航 |
| `StatusBar` | `components/layout/` | 状态栏（后端能力状态） |

#### 3.4.2 工作台组件

| 组件 | 路径 | 职责 |
|------|------|------|
| `WorkbenchContextPanel` | `components/workbench/` | 工作台上下文面板 |
| `AnalysisActionPanel` | `components/workbench/` | 分析操作面板 |
| `AnalysisLauncher` | `components/workbench/` | 分析启动器 |
| `JobSelector` | `components/workbench/` | 岗位选择器 |
| `ResumeSelector` | `components/workbench/` | 简历选择器 |
| `NextBestActionCallout` | `components/workbench/` | 下一步行动展示 |
| `OnboardingGuide` | `components/workbench/` | 新用户引导 |

#### 3.4.3 报告组件

| 组件 | 路径 | 职责 |
|------|------|------|
| `ScoreDimensionGrid` | `components/report/` | 评分维度网格 |
| `ScoringDimensionCard` | `components/report/` | 单项评分卡片 |
| `ScoringOverviewCard` | `components/report/` | 评分概览卡片 |
| `CapabilityGapCard` | `components/report/` | 能力缺口卡片 |
| `ResumeSuggestionReview` | `components/report/` | 简历建议审查 |
| `LearningPlanCard` | `components/report/` | 学习计划卡片 |
| `InterviewQuestionCard` | `components/report/` | 面试题卡片 |
| `EvidenceChainTable` | `components/report/` | 证据链表格 |
| `SkillsRadarChart` | `components/report/` | 技能雷达图 |
| `AgentTraceTimeline` | `components/report/` | Agent 轨迹时间线 |
| `AgentTraceRow` | `components/report/` | 单条轨迹记录 |

#### 3.4.4 反馈与状态组件

| 组件 | 路径 | 职责 |
|------|------|------|
| `EmptyState` | `components/feedback/` | 空状态提示 |
| `LoadingCard` | `components/feedback/` | 加载状态 |
| `ErrorBanner` | `components/feedback/` | 错误提示 |
| `BackendNotReadyNotice` | `components/feedback/` | 后端未就绪提示 |
| `SkeletonBlock` | `components/feedback/` | 骨架屏 |
| `RiskPill` | `components/risk/` | 风险标签 |
| `IntegrityGuardBanner` | `components/risk/` | 诚信守护横幅 |

### 3.5 样式系统

**目录**: `frontend/src/styles/`

| 文件 | 职责 |
|------|------|
| `tokens.css` | CSS 设计令牌（颜色、字体、间距） |
| `base.css` | 基础样式重置 |
| `a11y.css` | 无障碍样式（WCAG AA） |
| `animations.css` | 动画过渡效果 |

---

## 四、项目运行方式

### 4.1 环境要求

- **后端**: Python 3.10+, PostgreSQL 16+ (或 SQLite for dev)
- **前端**: Node.js 18+, npm/yarn/pnpm
- **容器**: Docker & Docker Compose

### 4.2 后端运行

#### 4.2.1 开发环境（SQLite）

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### 4.2.2 生产环境（PostgreSQL）

```bash
# 方式1: Docker Compose
docker compose up --build

# 方式2: 手动启动
# 先启动 PostgreSQL + pgvector
# 设置环境变量
export CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@localhost:5432/careerfit
export CAREERFIT_LLM_ENABLED=true
export CAREERFIT_LLM_API_KEY=your-api-key
export CAREERFIT_LLM_MODEL=your-model
# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 4.2.3 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `CAREERFIT_DATABASE_URL` | `sqlite+pysqlite:///./careerfit_dev.db` | 数据库连接 |
| `CAREERFIT_ENVIRONMENT` | `development` | 运行环境 |
| `CAREERFIT_LLM_ENABLED` | `false` | 是否启用 LLM |
| `CAREERFIT_LLM_PROVIDER` | `openai_compatible` | LLM 提供商 |
| `CAREERFIT_LLM_BASE_URL` | `https://api.openai.com/v1` | API 地址 |
| `CAREERFIT_LLM_API_KEY` | - | API 密钥 |
| `CAREERFIT_LLM_MODEL` | - | 模型名称 |
| `CAREERFIT_LLM_TIMEOUT_SECONDS` | `120` | 请求超时 |

### 4.3 前端运行

```bash
cd frontend
npm install
npm run dev      # 开发服务器 (默认 5173)
npm run build    # 生产构建
npm run typecheck  # 类型检查
npm test          # 运行测试
```

### 4.4 Docker Compose 服务

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: ["5432:5432"]
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: postgres (健康检查通过后)
    
  frontend:
    build: ./frontend
    ports: ["5173:80"]
    depends_on: backend (健康检查通过后)
```

### 4.5 种子数据

```bash
# 导入种子数据
cd backend
python import_seeds.py
```

种子文件位于 `backend/seeds/`:
- `backend_dev.json` - 后端开发岗位
- `frontend_fullstack.json` - 前端全栈岗位
- `llm_app_dev.json` - LLM 应用开发岗位
- `data_analysis.json` - 数据分析岗位

---

## 五、关键数据流

### 5.1 分析任务完整流程

```
1. 前端: 用户选择岗位 + 简历 → 创建分析任务 (POST /api/analysis)
2. 后端: 
   a. 验证岗位和简历存在
   b. 检查缓存
   c. 创建 AnalysisTask (状态=running)
   d. 提交到后台线程池
3. 后端线程:
   a. RAG 检索（按技能批量查询知识库）
   b. 执行 Agent 工作流（10个节点顺序执行）
   c. 每个节点记录 AgentRun
   d. 生成 AnalysisReport
   e. 更新任务状态为 success
4. 前端: SSE 流式获取进度 → 轮询报告状态 → 展示结果
```

### 5.2 Agent 节点执行流程

```
确定性节点:
  JD Parser → 简历 Parser → RAG 规划 → RAG 检索 → 评分计算
  
LLM 节点:
  Gap 分析 → 简历优化 → 面试教练 → 学习规划 → 下一步行动
       ↓
   LLM 调用
       ↓
   成功 → 返回结构化结果
       ↓
   失败 → 重试 (最多2次)
       ↓
   仍失败 → 回退到本地规则引擎
```

### 5.3 评分计算流程

```
输入: JD Profile + Resume Profile + RAG Results
  ↓
1. 技能匹配 (45%):
   - 遍历 JD 技能维度
   - 在简历中查找证据
   - 分类为: deep_experience/project_practice/basic_usage/mentioned/not_mentioned
  ↓
2. 项目经验 (25%):
   - 统计简历项目数量
   - 3+项目=100分, 2项目=85分, 1项目=70分
  ↓
3. 领域匹配 (10%):
   - JD 领域关键词与简历领域重叠度
  ↓
4. 基础要求 (10%):
   - 简历满足 JD 基础要求的程度
  ↓
5. 表达能力 (10%):
   - 技能与 JD 相关性比例
  ↓
6. 诚信风险扣分 (5%):
   - 基于低分项和弱证据项比例
  ↓
输出: final_score (0-100) + score_items (详细评分因子)
```

---

## 六、关键约定

### 6.1 API 设计约定

- 所有 API 返回统一包装: `{ ok: true, data: T }` 或 `{ ok: false, code: string, message: string }`
- 列表默认按创建时间倒序
- 分页参数: `page`, `page_size`
- 错误状态码: 400(参数错误), 404(资源不存在), 500(服务器错误)

### 6.2 数据脱敏约定

Agent Trace 对 UI 展示必须脱敏:
- 原始 JD 和简历文本 → `[redacted]`
- 证据详情 → `[redacted evidence]`
- API Key → `[redacted]`

### 6.3 Integrity Guard 约束

简历优化建议必须包含:
- 原始依据
- 优化表达
- 关联 JD 要求
- 使用的简历证据
- 风险等级

### 6.4 Gap 类型分类

| 类型 | 说明 | 优先级判定 |
|------|------|-----------|
| `missing_skill` | 简历未提及该技能 | 高(权重≥0.7)/中 |
| `weak_evidence` | 证据薄弱 | 高(权重≥0.7)/中 |
| `expression_gap` | 有经验但表达不足 | 中(权重≥0.5)/低 |
| `knowledge_insufficient` | 知识深度可能不足 | 中 |

---

## 七、测试策略

### 7.1 后端测试

```bash
cd backend
pytest -q                    # 快速运行
pytest -v                    # 详细输出
pytest tests/test_scoring.py  # 评分专项测试
```

测试覆盖:
- 评分规则 (`test_scoring.py`)
- Integrity Guard (`test_integrity_guard.py`)
- 分析流程 (`test_analysis_flow.py`)
- API 路由 (`test_api_routes.py`)
- RAG 检索 (`test_rag_retrieval.py`)
- LLM Agent (`test_llm_agent_flow.py`)

### 7.2 前端测试

```bash
cd frontend
npm test                     # 运行测试
npm run test:watch          # 监听模式
npm run typecheck           # 类型检查
```

### 7.3 集成测试

```bash
docker compose up --build   # 启动完整环境
# 访问 http://localhost:5173 验证功能
```

---

## 八、隐私与安全约束

1. **PII 处理**: 简历、JD、Agent 输入输出默认按敏感数据处理
2. **日志脱敏**: 不得在日志中输出完整简历原文
3. **Trace 脱敏**: UI 展示的 Agent Trace 必须使用脱敏摘要
4. **环境变量**: `.env`、API Key、数据库密码不得提交到仓库
5. **本地存储**: 前端 localStorage 仅存 UI 偏好，不得存 PII 内容
6. **URL 参数**: 不得通过 URL 传递 JD 原文、简历原文等 PII

---

## 九、扩展阅读

| 文档 | 位置 | 说明 |
|------|------|------|
| `AGENTS.md` | 根目录 | 项目协作约束 |
| `CLAUDE.md` | 根目录 | Agent 行为准则 |
| `TODOS.md` | 根目录 | 当前阶段进度 |
| `docs/DESIGN.md` | docs/ | 设计文档 |
| `docs/INDEX.md` | docs/ | 索引目录 |

---

*本文档由代码分析自动生成，如有疑问请联系项目维护者。*
