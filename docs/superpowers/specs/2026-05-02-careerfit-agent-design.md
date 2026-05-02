# CareerFit Agent 设计文档

日期：2026-05-02

## 产品定位

CareerFit Agent 是一个面向计算机专业应届生的个人求职成长工作台。它不是一次性的 JD 和简历分析器，而是帮助学生长期维护目标岗位、简历版本、匹配报告、面试训练、学习任务和分数趋势的个人系统。

核心价值是用 RAG 和多 Agent 工作流，让学生知道：自己的简历和目标岗位匹配到什么程度，评分依据是什么，哪些差距是真实能力差距，哪些只是表达问题，以及如何在不造假的前提下改进简历和补齐能力。

## 目标用户

目标用户是正在申请软件开发、后端、前端、全栈、AI 应用开发或大模型应用开发岗位的计算机专业学生和应届毕业生。

系统定位为单用户作品级产品，数据持久化到 PostgreSQL。本阶段不包含账号登录、多租户权限、HR 流程、导师流程、支付、通知或企业协作。

## 业务闭环

产品支持长期求职成长流程：

```text
保存目标岗位
  -> 上传或维护简历版本
  -> 执行 JD-简历匹配分析
  -> 查看可解释评分和证据链
  -> 识别能力缺口
  -> 生成诚实简历优化建议
  -> 生成面试题和学习路径
  -> 完成学习任务
  -> 创建新的简历版本
  -> 再次匹配分析
  -> 对比分数和缺口趋势
```

这个闭环让系统成为可持续使用的个人工作台，而不是只接收一份 JD 和一份简历的 Demo。

## 范围

### 范围内

- 目标岗位库和 JD 解析。
- 简历版本库和结构化简历解析。
- JD-简历匹配分析。
- 可解释分项评分。
- JD 要求、简历证据、知识库标准之间的证据链。
- 能力缺口分析。
- 防止简历造假的 Integrity Guard。
- 诚实简历优化建议。
- 面试题生成。
- 学习路径规划。
- 学习任务完成状态跟踪。
- 不同简历版本的分数和缺口趋势。
- Agent 运行轨迹记录。
- 基于 PostgreSQL 和 pgvector 的 RAG 知识库。
- 单用户数据持久化。
- Docker Compose 部署。

### 范围外

- 登录、注册和用户权限管理。
- HR 候选人筛选流程。
- 导师或就业老师看板。
- 多租户 SaaS 能力。
- 支付、通知和日历集成。
- 自动覆盖用户简历的完整改写。
- 无证据编造公司、项目、指标、职责或技术栈。

## 核心产品模块

### 1. 目标岗位库

用户可以通过粘贴或上传 JD 文本创建多个目标岗位。每个 JD 会被解析为结构化岗位画像，包括：岗位名称、公司名称、岗位级别、岗位职责、必备技能、加分技能、技术栈、项目经验偏好、学历或毕业要求、面试关注点。

解析后的岗位画像会被保存，后续分析不需要重复解析未变更的 JD。

### 2. 简历版本库

用户可以维护多个简历版本，例如：

```text
v1-original
v2-project-expression-improved
v3-rag-project-added
```

每个版本保存原始简历文本和结构化画像，包括教育背景、技术技能、项目经历、实习经历、竞赛/论文/证书/开源经历、量化成果，以及每项能力对应的证据片段。

系统支持比较两个简历版本，展示表达、证据和匹配分的变化。

### 3. 匹配分析

用户选择一个目标岗位和一个简历版本后，系统创建匹配分析任务。任务运行 LangGraph 工作流并持久化任务状态、Agent 运行轨迹、解析快照、评分拆解、证据项、能力缺口、真实性风险、简历建议、面试题和学习计划。

MVP 可以在 FastAPI 内同步执行工作流，但 API 设计必须采用任务式接口，便于后续切换到后台 worker。

### 4. 可解释匹配报告

报告展示总分、分项评分、主要优势、能力缺口、表达问题、证据质量问题、真实性风险、优化建议、面试题和学习路径。

每个评分项必须能追溯到：JD 要求、简历证据、知识库标准，以及受证据约束的解释。

### 5. 能力缺口分析

缺口分为三类：

- `missing_skill`：目标岗位要求某项能力，但简历完全没有体现。
- `weak_evidence`：简历提到了能力，但项目或结果证据不足。
- `expression_gap`：能力可能存在，但表达和 JD 不匹配。

这个分类可以避免把所有问题都粗暴归为“简历不会写”。有些问题需要学习和项目实践，而不是润色。

### 6. Integrity Guard

Integrity Guard 的核心规则是：

> 系统可以增强表达，但不能编造事实。

它会检查生成建议是否引入无证据的公司、项目、技术栈、性能指标、职责、生产部署、领导力、时间范围、奖项或证书。

它还会识别夸大表达，例如把“学习过”“使用过”“参与过”改成“主导”“负责架构”“生产落地”，但原简历没有对应证据。

高风险建议必须被阻止，或改写成诚实版本。

### 7. 简历优化

简历优化以“建议”形式输出，而不是静默生成一份新简历。每条建议包含原文、问题诊断、优化表达、关联 JD 要求、使用的简历证据、真实性风险等级和原因。

这种结构让优化过程可审计，也能避免用户误用虚假表达。

### 8. 面试训练

系统根据目标岗位、简历项目和能力缺口生成面试准备内容，包括基础技术题、项目深挖题、场景设计题、追问题、回答建议和面试官关注点。

问题应尽量引用用户真实简历项目。

### 9. 学习路径

学习规划器把缺口转成 7 天、14 天、30 天任务。每个任务包含目标技能、学习目标、推荐资源或资源类型、实践任务、验收标准、关联 JD 要求和状态。

完成任务后，用户可以创建新的简历版本并再次分析。

### 10. 成长趋势

系统记录不同岗位和简历版本组合的分数快照。用户可以查看同一目标岗位下不同简历版本的分数变化、剩余缺口、已完成学习任务、简历优化历史和面试训练历史。

## 多 Agent 工作流

工作流使用 LangGraph 和共享状态对象实现：

```text
START
  -> JD Parser Agent
  -> Resume Parser Agent
  -> RAG Retriever Agent
  -> Match Scoring Agent
  -> Gap Analysis Agent
  -> Integrity Guard Agent
  -> Resume Optimizer Agent
  -> Interview Coach Agent
  -> Learning Planner Agent
  -> Report Composer Agent
  -> END
```

共享状态 `CareerFitState` 包含原始 JD、原始简历、岗位画像、简历画像、检索结果、匹配结果、缺口分析、真实性报告、简历优化、面试计划、学习计划、最终报告和 trace 日志。

各 Agent 职责：

- JD Parser Agent：解析 JD 并标准化技能名称。
- Resume Parser Agent：解析简历并把技能、项目、成果绑定到证据片段。
- RAG Retriever Agent：从 pgvector 检索技能定义、岗位画像、面试题和学习资源。
- Match Scoring Agent：基于规则计算分数，LLM 只负责解释，不直接决定最终分数。
- Gap Analysis Agent：识别缺失能力、证据不足和表达问题。
- Integrity Guard Agent：审查无证据事实和夸大表达。
- Resume Optimizer Agent：生成受证据约束的简历优化建议。
- Interview Coach Agent：生成面试题和回答建议。
- Learning Planner Agent：生成阶段化学习路径。
- Report Composer Agent：组装最终报告并确保结论包含证据引用。

## RAG 知识库

知识库使用 PostgreSQL 和 pgvector。文档按类型拆分，而不是混在一个向量表里。

文档类型：

- `skill`：技能定义、同义词、能力层级、项目证据标准。
- `job_profile`：后端、前端、全栈、AI 应用、大模型应用等岗位画像。
- `interview`：面试题、追问题、难度和评价点。
- `learning`：学习资源、实践任务和验收标准。

核心表：

```text
knowledge_documents
  id
  doc_type
  title
  content
  metadata JSONB
  embedding vector
  created_at
```

`metadata` 保存技能名、难度、岗位族、来源类型和标签。

## 可解释评分

最终分数由规则、检索标准和证据共同计算。LLM 负责解释结果，但不直接拍数字。

```text
final_score =
  skill_score * 0.35 +
  project_score * 0.25 +
  domain_score * 0.15 +
  basic_requirement_score * 0.10 +
  expression_score * 0.10 -
  integrity_risk_penalty * 0.05
```

能力层级映射：

```text
not_mentioned     0.00
mentioned         0.30
basic_usage       0.50
project_practice  0.75
deep_experience   1.00
```

每个评分项必须包含技能、岗位要求等级、简历体现等级、得分、JD 证据、简历证据、知识库证据和原因。

## 后端架构

技术栈：FastAPI、Pydantic、SQLAlchemy、PostgreSQL、pgvector、LangGraph、Docker Compose。

建议结构：

```text
backend/app
  api/routes        HTTP 路由
  core              配置和日志
  db                数据库连接和模型
  schemas           Pydantic 输入输出结构
  services          业务编排
  agents            LangGraph 状态和节点
  rag               chunk、embedding、retrieval、loader
  scoring           规则评分、rubric、证据处理
```

## 数据库表

核心表：

- `job_descriptions`：目标岗位和解析后的 JD 画像。
- `resume_versions`：简历版本和解析画像。
- `analysis_tasks`：每次分析任务状态。
- `analysis_reports`：最终报告。
- `agent_runs`：Agent 节点运行轨迹。
- `evidence_items`：评分和解释使用的证据。
- `learning_tasks`：学习任务和完成状态。
- `interview_sessions`：生成的面试训练内容。
- `score_snapshots`：趋势数据。

所有结构化 JSON 必须带 `schema_version`，方便后续演进。

## API 设计

```text
POST /api/jobs
GET  /api/jobs
GET  /api/jobs/{id}
DELETE /api/jobs/{id}

POST /api/resumes
GET  /api/resumes
GET  /api/resumes/{id}
GET  /api/resumes/compare?from=&to=
DELETE /api/resumes/{id}

POST /api/analysis
GET  /api/analysis/{task_id}
GET  /api/reports/{task_id}
GET  /api/agent-runs/{task_id}

GET  /api/learning/tasks
PATCH /api/learning/tasks/{id}

POST /api/interview/sessions
GET  /api/interview/sessions/{id}

POST /api/knowledge/import
GET  /api/knowledge/search

GET  /api/trends/scores
```

## 前端设计

技术栈：Vue3、TypeScript、Vite、REST API client。

页面：工作台、目标岗位库、简历版本库、匹配分析页、分析报告页、证据解释页、面试训练页、学习路径页、成长趋势页、Agent 轨迹页。

体验原则：

- 第一屏是个人求职工作台，不是营销落地页。
- 报告优先展示清晰结论、证据和下一步动作。
- 评分解释可按维度和技能展开。
- 简历优化以可审计建议展示。
- 真实性风险必须可见，不能隐藏在漂亮文案后面。
- Agent 轨迹用于技术展示和调试。

## Docker 部署

Docker Compose 包含：

```text
frontend
backend
postgres-pgvector
```

可选后续服务：

```text
redis
worker
```

MVP 应支持：

```text
docker compose up --build
```

## 简历项目包装

简历描述建议：

> 设计并实现 CareerFit Agent，一个面向计算机应届生的 AI 求职成长工作台。项目基于 FastAPI、LangGraph、PostgreSQL、pgvector、Vue3 和 Docker 构建 RAG + 多 Agent 工作流，支持目标岗位管理、简历版本管理、可解释 JD-简历匹配、能力缺口分析、Integrity Guard 简历优化、面试题生成、学习路径规划和分数趋势追踪。

技术亮点建议：

> 将 JD 解析、简历解析、RAG 检索、匹配评分、缺口分析、真实性审查、简历优化、面试训练和学习规划拆分为可观测 LangGraph 节点，并将节点输入输出、耗时、token 使用、证据链和评分拆解持久化到 PostgreSQL，实现可解释、可追踪的 AI 工作流。

## 成功标准

- 用户可以保存多个目标岗位。
- 用户可以保存多个简历版本。
- 用户可以在任意岗位和简历版本之间执行分析。
- 报告包含总分、分项评分、证据、缺口、真实性风险、简历建议、面试题和学习任务。
- 每个评分解释都引用 JD 证据和简历证据。
- 简历优化建议不能引入无证据事实。
- 用户可以标记学习任务完成。
- 用户可以比较不同简历版本的分数变化。
- Agent 运行轨迹被持久化并可查看。
- 系统可以通过 Docker Compose 本地启动。

## 风险与缓解

- 风险：项目变成 prompt 包装器。缓解：持久化岗位、简历版本、报告、学习任务、分数快照和 Agent 轨迹，使用规则评分和证据链。
- 风险：系统鼓励简历造假。缓解：最终建议前必须运行 Integrity Guard，所有建议引用简历证据。
- 风险：RAG 变成装饰。缓解：检索结果必须进入评分标准、面试题和学习任务。
- 风险：范围扩张成 HR SaaS。缓解：保持单用户个人工作台，不做 HR、导师、登录和多租户。
- 风险：同步分析阻塞接口太久。缓解：从一开始采用任务式 API，后续可迁移到 worker。

---

## Autoplan 审查

日期：2026-05-02

分支：`main`

计划文件：`docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`

外部审查状态：

- Codex CLI voice：不可用。Windows read-only runner 在读取文件前失败，错误为 `CreateProcessAsUserW failed: 5`。
- Claude subagent voice：当前会话工具策略不允许在用户未明确要求时创建 subagent，因此不可用。

以下为本地 autoplan 对产品、设计和工程三个维度的审查结果。

### Phase 1：产品 / CEO 审查

核心判断：持久化个人工作台的方向正确，明显强于一次性 JD-简历分析器。但产品不能只是 AI 输出合集，必须让用户知道“今天最该做什么”。

自动决策：在工作台加入 `Next Best Action`。它从最新报告中选择一个高影响动作，例如改写某条项目经历、补齐 pgvector 索引实践、准备 5 个 LangGraph 追问题。

已有内容：当前仓库是新仓库，只有设计文档，没有应用代码、数据库 schema、UI、测试或 Docker 文件。

保持范围外：登录、多用户、HR 排名、导师管理、支付、通知、日历、企业协作、自动简历造假、生产级岗位爬虫。

推荐实现顺序：

1. 先做单用户持久化工作台。
2. 为 3 类岗位准备高质量种子知识库：大模型应用开发、后端、前端/全栈。
3. 先实现确定性评分，再做复杂 UI。
4. 做报告、证据链和 Agent trace。
5. 在端到端报告稳定后再做学习任务和趋势图。

### 错误与救援表

| 错误 | 用户体验 | 救援方式 | 责任层 |
|---|---|---|---|
| JD 解析失败 | 用户无法创建有效目标岗位 | 保存原文，展示可编辑字段，允许重新解析 | 后端 + UI |
| 简历解析失败 | 用户无法分析简历 | 保存原文，让用户确认抽取结果 | 后端 + UI |
| LLM 返回非法 JSON | 分析任务失败 | Pydantic 校验，修复 prompt 重试一次，失败节点写入 trace | Agent 层 |
| RAG 无结果 | 解释像编的 | 继续规则评分，并标记知识证据不足 | RAG + scoring |
| Integrity Guard 过度拦截 | 用户得不到建议 | 给出更保守的表达建议，并说明缺少什么证据 | Integrity Agent |
| 分析时间太长 | 用户以为卡死 | 时间线、节点状态、重试按钮 | API + UI |

### 失败模式表

| 失败模式 | 严重度 | 缓解 |
|---|---:|---|
| 分数看似科学但实际随意 | 高 | 确定性评分、公开 rubric、保存评分因子和证据 |
| 简历优化编造成果 | 致命 | Integrity Guard 必须在最终报告前运行 |
| 知识库太薄 | 高 | 先准备高质量种子文档 |
| 用户看完报告不知道下一步 | 高 | 加入 Next Best Action，把缺口转为任务 |
| Agent trace 泄露完整简历 | 中 | UI 只展示脱敏摘要，原始快照仅服务端保存 |
| 同步工作流超时 | 中 | API 保持任务式，后续切 worker |

### 产品结论

产品方向通过。评分：用户价值 8/10，差异化 7/10，范围控制 8/10，简历项目强度 9/10。主要补强点是 `Next Best Action`。

### Phase 2：设计审查

UI 范围存在。当前页面列表完整，但设计还需要补足首屏层级、首次使用、加载、空状态、失败状态、弱证据状态和可访问性要求。

工作台首屏必须优先展示：当前目标岗位、当前主简历版本、最近分数、Top 3 缺口、Next Best Action、最近分数趋势。

缺失状态必须补齐：无目标岗位、无简历版本、岗位已解析但需确认、简历解析低置信度、分析运行中、某个 Agent 节点失败、报告生成但 RAG 证据弱、学习任务全部完成。

用户情绪路径应是：

```text
我知道自己处在哪
  -> 我知道为什么
  -> 我知道能诚实改什么
  -> 我知道下一步学什么
  -> 更新简历后能看到进步
```

报告不能是一整墙 AI 文本。应使用结构化卡片和表格：评分卡、技能证据行、缺口行、建议行、风险行。

前端实施时需要小型内部组件体系：Button、Input、Textarea、File Upload、Status Badge、Score Card、Evidence Table、Agent Timeline、Drawer。

可访问性要求：键盘可操作、焦点可见、风险不能只靠颜色表达、移动端报告表格可读、长文本区域高度稳定、Agent 时间线有文字标签。

设计结论：通过，但必须补齐状态设计和结构化报告。当前完整度 6/10。

### Phase 3：工程审查

架构方向正确，但实现难点集中在：LLM 结构化输出、JD/简历 schema 版本、确定性评分、证据可追溯、pgvector 种子数据质量、Agent 重试和失败隔离。

自动决策：实现必须从 schema contract 和确定性评分测试开始，而不是先铺满前端页面。

架构图：

```text
Vue3 App
  |
  | REST
  v
FastAPI API
  |
  | 创建分析任务
  v
Analysis Service
  |
  | 调用
  v
LangGraph Workflow
  |        |          |
  |        |          +--> Agent Run Logger
  |        |
  |        +--> Scoring Engine
  |
  +--> RAG Retriever
          |
          v
PostgreSQL + pgvector
  |
  +--> job_descriptions
  +--> resume_versions
  +--> analysis_tasks
  +--> analysis_reports
  +--> agent_runs
  +--> evidence_items
  +--> learning_tasks
  +--> score_snapshots
  +--> knowledge_documents
```

工程发现：

| 问题 | 严重度 | 修复 |
|---|---:|---|
| 解析画像缺少 schema version | 高 | JD、简历、报告、评分拆解都加 `schema_version` |
| 评分公式缺少 clamp 和校准规则 | 高 | 所有维度限制在 0-100，并保存原始因子 |
| LLM 输出校验不明确 | 高 | 每个 Agent 节点定义 Pydantic 输出结构 |
| Agent 快照可能保存过多个人数据 | 中 | 服务端保存完整数据，UI 展示脱敏摘要 |
| 知识导入缺少质量控制 | 中 | 先使用仓库内 fixture 种子文档 |
| 文件上传解析不明确 | 中 | MVP 先支持文本，再加 PDF/DOCX |
| 任务 API 没有重试语义 | 中 | 后续增加任务或节点重试接口 |

测试图：

| 流程 | 测试类型 | 覆盖 |
|---|---|---|
| 创建目标岗位 | API + service | 有效 JD、空 JD、解析失败 |
| 创建简历版本 | API + service | 有效简历、空简历、低置信度解析 |
| 运行分析任务 | 集成测试 | 成功、Agent 失败、非法 JSON |
| 评分计算 | 单元测试 | 技能分、项目分、风险扣分、clamp |
| 证据链 | 单元 + 集成 | 每个评分项都有 JD 和简历证据 |
| Integrity Guard | 单元 + eval | 无证据指标、夸大职责、安全改写 |
| RAG 检索 | 集成测试 | 种子文档能召回预期技能 |
| 前端报告页 | 组件/E2E | 加载、错误、成功、弱证据状态 |
| Agent trace 页 | 组件/E2E | 脱敏摘要和失败节点 |
| Docker 启动 | Smoke | frontend、backend、postgres health |

工程结论：通过。架构 8/10，数据模型 7/10，测试计划 5/10，性能 7/10，隐私安全 6/10，部署 7/10。

### 跨阶段主题

- 产品必须产生行动，而不只是分析。`Next Best Action` 和“创建下一版简历”是必要流程。
- 信任就是产品核心。确定性评分、证据链、Integrity Guard、脱敏和弱证据标签不是附加项。
- 范围现在是正确的。不要重新加入 HR、导师、登录、多租户。

### Autoplan 决策日志

| # | 阶段 | 决策 | 类型 | 原则 | 理由 | 拒绝方案 |
|---|---|---|---|---|---|---|
| 1 | 产品 | 增加 `Next Best Action` | 自动决策 | 完成用户闭环 | 用户需要今天能做的动作，而不只是报告 | 只有报告的工作台 |
| 2 | 产品 | 保持单用户范围 | 自动决策 | 尊重用户边界 | 用户明确拒绝双端产品 | HR/导师流程 |
| 3 | 设计 | 补齐空/加载/错误/部分数据状态 | 自动决策 | 完整实现 | 这些状态在真实使用中必然出现 | 只做 happy path |
| 4 | 设计 | 报告使用结构化行而非长文本 | 自动决策 | 可读性 | 证据和风险必须可扫描 | AI 文本墙 |
| 5 | 设计 | 加入可访问性基线 | 自动决策 | 质量基线 | 键盘和非颜色提示成本低但价值高 | 只做视觉 UI |
| 6 | 工程 | 先做 schema 和确定性评分测试 | 自动决策 | 降低核心风险 | 信任依赖可复现评分 | 前端优先 |
| 7 | 工程 | 增加 schema version | 自动决策 | 支持演进 | JSONB 结构会持续变化 | 无版本 JSON |
| 8 | 工程 | UI 展示脱敏 Agent trace | 自动决策 | 隐私保护 | 简历数据敏感 | 原始 trace 直出 |

### 最终建议

批准当前计划，并按 Phase 1 先实现可信端到端闭环：

```text
准备种子知识库
  -> create job
  -> 创建简历
  -> 解析岗位和简历
  -> 检索能力标准
  -> 执行确定性评分
  -> 生成带证据链的报告
  -> 阻止无证据建议
  -> 持久化运行轨迹
```
