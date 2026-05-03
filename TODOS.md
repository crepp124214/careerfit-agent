# CareerFit Agent TODOS

日期：2026-05-02
版本：v2（双门重写：前端 Phase 1.A + 后端 Phase 1.B 同步）

## 适用范围与文件优先级

- 本文件不覆盖 `CLAUDE.md`。如有冲突，以 `CLAUDE.md` 中的"当前核心产品约束"、"Phase 1 验收门"、"前端实现约束"、"隐私与安全约束"为准。
- 范围分类与 `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md` 中的 T1–T13 任务清单一一对应。
- 任何范围变化必须同步更新本文件、实施计划、测试计划与设计文档（`CLAUDE.md` 实施文档实时更新约束）。

## Phase 1 in-scope（不延后）

以下事项原本可能因主路径优先级被列为延后，但在双门重写后已明确归入 Phase 1，必须随计划完成。

### 当前进度

- [x] **前端 Phase 1.A（T1–T7）**：全部完成。77 测试通过，typecheck clean，Docker 化就绪，10/10 验收门 PASS。
- [x] **后端 Phase 1.B（T8–T11）**：由 Codex 完成。15 测试通过，可信主路径端到端闭环。
- [x] **全栈集成（T12–T13）**：已完成。全栈 Docker Compose 三容器 healthy，README 中文版就绪，双验收门全部通过。第三轮联调修复：Agent Trace 中间态 evidence 脱敏、报告页适配真实后端 snake_case 响应、favicon 404 修复、healthcheck localhost→127.0.0.1。

### 前端 Phase 1.A（T1–T7）

- 13 条 Vue Router 路由全部铺出，缺一不可。
- 工作台、Jobs/Resumes 列表与详情、分析提交、报告、HistoryView、VersionDiffView、LearningTasksView、AgentTraceView、SettingsView 全部支持空/加载/错误/部分数据状态机。
- 共享组件 TDD：`AppButton`、`RiskPill`（双通道）、`BackendNotReadyNotice`、`NextBestActionCallout`、`IntegrityGuardBanner`、`EvidenceCard`、`ScoringDimensionCard`、`ScoringOverviewCard`、`SuggestionCard`、`AgentTraceTimeline`、`AgentTraceRow`。
- `availability` Pinia store 消费 `/api/capabilities`；`frontend-only` 与 `fullstack` 两种模式均覆盖。
- 后端缺口必须用 `BackendNotReadyNotice` 用户可见占位；禁止 mock 数据。
- `useLocalStorageRef` + PII 白名单 + 内存回落；`careerfit:pref:*` 命名空间严格限定。
- 完整响应式：1440 / 1280 / 1024 / 768 / 480 五档。
- 完整无障碍：键盘可达 + ARIA + WCAG AA（axe-core 校验工作台、报告、Jobs、Settings 四视图）。
- 关键交互动效 200–300ms 过渡，禁止硬切换。
- `frontend/Dockerfile` 多阶段（nginx 运行）+ `docker-compose.frontend-only.yml` 可独立 `up --build`。

### 后端 Phase 1.B（T8–T11）

- 目标岗位、简历版本、分析任务、报告、Agent runs 的端到端可信主路径。
- 评分确定性：维度 clamp 0–100、原始因子持久化、LLM 不直接决定数字分。
- Integrity Guard：阻止无证据指标与夸大职责；最终输出前必须运行。
- Agent Trace 脱敏：服务端原始快照与对外响应分离。
- `/api/capabilities`：响应 schema 含 `schema_version`，缺失字段 fallback `pending`，每个后端任务完成后翻 `ready`。
- LangGraph 节点输出 Pydantic 校验；非法 JSON 仅允许 1 次修复重试。
- RAG 检索证据足够时才出结论，否则标记"知识库证据不足"。

### 全栈集成（T12–T13）

- `docker-compose.yml` 全栈启动：postgres + pgvector + backend + frontend（`fullstack` 变体）。
- README 中文版：`frontend-only`、`fullstack` 两种启动方式与验收门 checklist。
- 集成主路径端到端 UI 走查（10 步主路径 + 模式切换 11/12 步）。

## 决策点（不允许静默选）

以下事项有合理但相互冲突的选项，必须显式决策并记录在实施计划对应任务的"决策记录"区。

| 决策点 | 选项 A | 选项 B | 当前默认 |
|---|---|---|---|
| LangGraph 接入方式 | 真 LangGraph 编排器 | 本地顺序 runner + 兼容 workflow boundary | 选 B，但保留切换边界（`CLAUDE.md` 依赖与技术取舍） |
| 测试 DB | SQLite + 行为差异显式覆盖 | PostgreSQL Docker 集成 + 不跑 SQLite | 双轨：单测用 SQLite，集成测试用 PostgreSQL |
| Agent trace 服务端原始快照保留期 | 仅本地开发保留 | 始终保留并显式 TTL（如 7 天） | 选 A，生产部署前再决议 |
| 前端 UI 库 | 无 UI 库纯手写 | 引入轻量库（如 Reka UI / Radix Vue） | 选 B：Reka UI（Phase 4 D4 审批通过） |
| 前端图表库 | Chart.js | ECharts | 选 B：ECharts（Phase 4 D5 审批通过） |
| 前端动效库 | 仅 CSS transitions | VueUse Motion / GSAP | 默认 CSS，复杂动效再决议 |
| 后端 SQLAlchemy 异步 vs 同步 | 全异步 | 同步 + worker 边界 | 选 B：同步 Phase 1（Phase 4 D6 审批通过） |

每次决策须写明：选择哪个、理由、影响范围、回滚条件。

## Phase 2+ 延后

以下事项有产品价值，但当前不进入 Phase 1，避免范围膨胀。

### 后端能力

- 简历优化建议稳定后，再加简历导出。
- 文本输入端到端跑通后，再加 PDF/DOCX 简历解析。
- 任务式 API 稳定后，再引入后台 worker（Celery / RQ / Arq）。
- 本地 Markdown 简历导入。
- 报告格式稳定后，再加报告导出（Markdown / PDF）。
- 知识库扩充更多岗位族（数据科学、安全、嵌入式、运维等）。
- 面试回答评分闭环。
- 每周求职进展总结。
- 多模型路由 / fallback / 成本观测。

### 前端能力

- 主题深度自定义（仅核心两套 + 切换由 Phase 1 完成；自定义色 / 字号 / 布局延后）。
- 国际化 i18n（Phase 1 仅中文）。
- 离线模式与 PWA。
- 富文本简历编辑器（Phase 1 用纯文本输入）。
- 报告 PDF 导出预览。
- 协作分享只读链接（前提是先确定分享是否触发账号边界，默认延后）。

### 架构与运维

- 真实账号系统（登录、注册、SSO）— `CLAUDE.md` 硬边界，禁止在 Phase 1 引入。
- 多用户多租户 — 同上。
- 生产级部署（K8s / 灰度 / 蓝绿） — Phase 2+。
- 监控仪表盘（Sentry / OpenTelemetry / Grafana）。
- CI/CD 全链路（lint / typecheck / test / build / deploy）。
- 容器镜像签名 / SBOM。

## 明确不做的范围（硬边界）

- 登录、注册和多用户账号管理。
- HR 候选人筛选和排序流程。
- 导师、就业老师或管理员看板。
- 支付、通知、日历或企业协作功能。
- 生产级岗位网站爬取。
- 把项目降级成一次性 Demo。

## 跨文件同步检查

每次变更范围或决策时，必须同时检查并更新：

- `CLAUDE.md`（如影响约束或边界）
- `AGENTS.md`（如影响约束或边界）
- `docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`
- `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md`
- `docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md`
- `C:\Users\qwer\.gstack\projects\Newproject\main-test-plan-2026-05-02-careerfit-agent.md`
- `docs/DESIGN.md`（如影响视觉系统或组件契约）
- 本文件

不同步即为违反 `CLAUDE.md` "实施文档实时更新" 节。

### Phase 4 决策审计（2026-05-03 用户审批通过）

| 决策 | 选择 | 类型 | 理由 | 影响 | 回滚条件 |
|---|---|---|---|---|---|
| D1 产品形态 | 13 路由工作台 + 工作台首屏「下一步」卡片 | Auto-decide（用户批准） | 与 CLAUDE.md 工作台优先一致 | T1 路由表 + T3 工作台视图 | 用户研究表明工作台导航过载 |
| D2 评分展示 | 评分卡 + 证据并列 | Auto-decide | Design 共识：先看分会损害可信度 | T4 报告视图 + DESIGN.md ScoringDimensionCard | 用户反馈"证据太多看不过来" |
| D3 Agent trace 密度 | 折叠摘要 + 展开看完整节点 | Auto-decide | 平衡可信度与认知负载 | T5 AgentTraceView + DESIGN.md AgentTraceTimeline | 用户主动请求默认展开 |
| D4 UI 库 | Reka UI（轻量 headless） | Auto-decide | 仅引入需要的组件，避免设计系统冲突 | T1 依赖清单 + T2 共享组件 | Reka UI 与 Vue 3 不兼容 |
| D5 图表库 | ECharts | Auto-decide | HistoryView 趋势图主力 | T5 HistoryView | bundle 体积 > 200KB gzip |
| D6 SQLAlchemy 异步/同步 | 同步 Phase 1 | Auto-decide | greenfield 测试更简单；T8 之前无流式/高并发需求 | T8 backend 骨架 + T9 service | Phase 1 出现需要异步流式响应的功能 |
| D7 Agent trace 持久化 | 原始快照 + 对外脱敏分离 | Auto-decide | trace schema 演进比响应需求快 | T11 持久化 + T11 脱敏 | 隐私合规要求不持久化原始 trace |
| D8 Evidence 偏移坐标 | raw + normalized 双坐标 | Auto-decide | 双坐标支持 UI 高亮 + 后端复算 | T9 Evidence schema | 性能基准显示双坐标存储成本 > 30% |
| D9 LangGraph 类型层级 | adapter-only | Auto-decide | 保留可替换性 | T10 AgentRunner 边界 + ADR 0001 | LangGraph 真接入后不再需要边界 |
| D10 Capability 版本化 | schema_version + 四态枚举 | Auto-decide | 未来 capability 翻转和新 agent 能力都需要 | T8 capability 契约 + T2 availability store | 改用纯客户端能力探测 |
| D11 测试 DB 策略 | 双轨：SQLite 单测 + Postgres 集成 | Auto-decide | 与 TODOS.md 已记录决策一致 | 整个测试矩阵 | SQLite/Postgres 行为差异不可调和 |
| D12 DESIGN.md 480px 修订时机 | 随 T1 脚手架同时修 | User Challenge（用户批准 A） | 早对齐五档断点避免 T3-T7 返工 | T1 commit 同时改 DESIGN.md 第 540 行 + 已知缺口 #3 | T1 阻塞超过 1 个 work session |
| C1 BackendNotReadyNotice 必填 props | 是，作为 T2 强制门 | User Challenge（用户批准 A） | 防止退化为空白 div | T2 共享组件契约 + 测试用例 | runtime 校验在 SSR 场景下不兼容 |
| C2 Integrity Guard 伪积极黑名单 | 是，纳入黑名单 | User Challenge（用户批准 A） | 伪积极对求职者更危险 | T10 Integrity Guard + 测试样例（5+5） | 用户反馈黑名单过严，正常乐观表达被拦截 |

### autoplan 通过门后行动清单

- [x] Phase 0/0.5/1/2/3/3.5/4 全部通过审查。
- [x] 修订 `docs/DESIGN.md` 第 540 行 + 已知缺口 #3（D12 决议：480px 断点已写入，与 T1 同步完成）。
- [x] 把 14 项决策同步到 `TODOS.md` "决策点" 节（"决策点"节 + "Phase 4 决策审计"节双重记录）。
- [ ] 写 3 条 review-log（plan-ceo-review / plan-design-review / plan-eng-review，含双声标记）。
- [x] 建议下一步：T1–T13 全部完成，Phase 1 已交付。
- [ ] 提示：T8–T11 的 PII 入口逻辑必须跑 `gstack:cso` OWASP + STRIDE 安全审计。

