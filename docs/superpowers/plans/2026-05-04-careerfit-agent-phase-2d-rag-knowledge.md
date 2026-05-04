# CareerFit Agent Phase 2D RAG 知识库实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 RAG 知识库，让评分有知识库标准作为第三方参考，面试题和学习任务有外部资源推荐。

**Architecture:** 新增 `knowledge_documents` 表 + pgvector 索引，新增 `rag_retriever` Agent 节点，评分层消费检索结果，种子知识库覆盖三组核心岗位。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、PostgreSQL + pgvector、sentence-transformers（all-MiniLM-L6-v2）、SQLite 测试替身、Docker Compose。

---

## 范围

进入范围：

- `knowledge_documents` 表和 pgvector 索引。
- `rag_retriever` Agent 节点。
- 评分层 `knowledge_evidence` 字段。
- `POST /api/knowledge/import` 和 `GET /api/knowledge/search`。
- 三组种子知识库（后端、前端/全栈、大模型应用）。
- `/api/capabilities` 增加 `knowledge` 状态。
- 前端报告页 EvidenceCard 展示知识库标准引用。

不进入范围：

- 用户上传文档。
- 知识库版本管理。
- embedding 模型切换或微调。
- 知识库管理 UI。

## 成功标准

- `knowledge_documents` 表存在且含 pgvector 索引。
- 种子知识库导入后至少包含 20 篇文档。
- `rag_retriever` 节点在工作流中正确执行。
- 每个 score_item 包含 `knowledge_evidence` 字段。
- 检索不到时 `available: false` + 中文原因。
- 后端、前端、typecheck、build 通过。

## 文件结构

```text
backend/
  app/
    db/models.py                          # 新增 KnowledgeDocument 模型
    api/routes/knowledge.py               # 新增
    schemas/knowledge.py                  # 新增
    services/knowledge_service.py         # 新增
    rag/
      __init__.py                         # 新增
      embedding.py                        # 新增：embedding 生成
      retrieval.py                        # 新增：向量检索
      loader.py                           # 新增：种子数据加载
    agents/state.py                       # 修改：新增 rag_results
    agents/nodes.py                       # 修改：新增 rag_retriever
    agents/graph.py                       # 修改：NODE_SEQUENCE 新增节点
    scoring/rules.py                      # 修改：score_items 新增 knowledge_evidence
    main.py                               # 修改：注册 knowledge router + capability
  seeds/
    backend_dev.json                      # 新增：后端开发种子数据
    frontend_fullstack.json               # 新增：前端/全栈种子数据
    llm_app_dev.json                      # 新增：大模型应用种子数据
  tests/
    test_knowledge_api.py                 # 新增
    test_rag_retrieval.py                 # 新增
    test_rag_agent_node.py                # 新增
    test_scoring_with_rag.py              # 新增
frontend/
  src/
    components/report/EvidenceCard.vue    # 修改：展示 knowledge_evidence
    stores/availability.ts                # 修改：新增 knowledge capability
    api/availability.ts                   # 修改：新增 knowledge 类型
    api/reports.ts                        # 修改：新增 KnowledgeEvidenceItem 类型
docs/
  superpowers/specs/2026-05-04-careerfit-agent-phase-2d-rag-knowledge-design.md
  superpowers/plans/2026-05-04-careerfit-agent-phase-2d-rag-knowledge.md
  superpowers/test-plans/2026-05-04-careerfit-agent-phase-2d-test-plan.md
TODOS.md
```

---

## Task 0：计划与文档门

**Files:**

- Create: `docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2d-rag-knowledge-design.md`
- Create: `docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2d-test-plan.md`
- Modify: `TODOS.md`

- [x] **Step 1：确认 Phase 2D 范围**

用户已选择 RAG 知识库。记录范围边界：pgvector + sentence-transformers，不做用户上传、版本管理或模型微调。

- [x] **Step 2：创建设计文档**

新增 Phase 2D 设计文档，写明数据库设计、RAG 架构、API、评分变更和种子知识库。

- [x] **Step 3：创建测试计划**

新增 Phase 2D 测试计划。

- [x] **Step 4：更新 TODOS**

把 Phase 2D 当前范围、延后项和验证门写入 `TODOS.md`。

---

## Task 1：数据库模型与依赖

**Files:**

- Modify: `backend/app/db/models.py`
- Modify: `backend/pyproject.toml`

- [x] **Step 1：新增 KnowledgeDocument 模型**

在 `models.py` 新增 `KnowledgeDocument` 类，包含 `id`、`doc_type`、`title`、`content`、`metadata_`（JSONB）、`embedding_json`（JSON）、`embedding`（vector(384)，pgvector 可用时）、`created_at`。

- [x] **Step 2：安装 sentence-transformers 依赖**

在 `pyproject.toml` 新增 `sentence-transformers>=2.6` 依赖。

- [x] **Step 3：运行数据库迁移验证**

确认 `KnowledgeDocument` 表在 SQLite 中可创建（pgvector 列条件导入，SQLite 使用 JSON 替代）。

- [x] **Step 4：运行现有后端测试确认无回归**

后端测试通过。

---

## Task 2：RAG 核心模块

**Files:**

- Create: `backend/app/rag/__init__.py`
- Create: `backend/app/rag/embedding.py`
- Create: `backend/app/rag/retrieval.py`
- Create: `backend/app/rag/loader.py`

- [x] **Step 1：写失败测试：embedding 生成**

测试 `generate_embedding("FastAPI")` 返回 384 维浮点数组。

- [x] **Step 2：实现 embedding 模块**

使用 `sentence-transformers` 加载 `all-MiniLM-L6-v2`，提供 `generate_embedding(text)` 和 `generate_embeddings(texts)` 函数。模型加载失败时回退到关键词匹配模式。

- [x] **Step 3：写失败测试：向量检索**

测试 `retrieve_by_skill(db, "FastAPI", top_k=3)` 返回相关文档列表。

- [x] **Step 4：实现检索模块**

`retrieve_by_skill(db, skill_name, top_k)` 从 `knowledge_documents` 中做向量近似搜索。SQLite 环境使用 JSON 模拟（余弦相似度 + 关键词匹配）。

- [x] **Step 5：写失败测试：种子数据加载**

测试 `load_seed_data(db, "backend_dev")` 导入文档并生成 embedding。

- [x] **Step 6：实现种子数据加载器**

从 JSON 文件读取种子文档，生成 embedding，批量插入 `knowledge_documents`。

- [x] **Step 7：运行 RAG 模块测试**

7 个测试全部通过。

---

## Task 3：Knowledge API

**Files:**

- Create: `backend/app/schemas/knowledge.py`
- Create: `backend/app/api/routes/knowledge.py`
- Create: `backend/app/services/knowledge_service.py`
- Modify: `backend/app/main.py`

- [x] **Step 1：写失败测试：import API**

测试 `POST /api/knowledge/import` 批量导入文档。

- [x] **Step 2：写失败测试：search API**

测试 `GET /api/knowledge/search?q=FastAPI` 返回相关文档。

- [x] **Step 3：新增 schema**

在 `schemas/knowledge.py` 新增 `KnowledgeDocumentCreate`、`KnowledgeImportRequest`、`KnowledgeImportResponse`、`KnowledgeSearchResult`、`KnowledgeSearchResponse`。

- [x] **Step 4：实现 knowledge service**

`import_documents(db, documents)` 和 `search_documents(db, query, doc_type, limit)`。

- [x] **Step 5：实现 routes**

`POST /api/knowledge/import` 和 `GET /api/knowledge/search`。

- [x] **Step 6：注册 router 和 capability**

在 `main.py` 注册 `knowledge.router`，`CAPABILITIES` 新增 `"knowledge": "ready"`。

- [x] **Step 7：运行 Knowledge API 测试**

7 个测试全部通过。

---

## Task 4：rag_retriever Agent 节点

**Files:**

- Modify: `backend/app/agents/state.py`
- Modify: `backend/app/agents/nodes.py`
- Modify: `backend/app/agents/graph.py`
- Modify: `backend/app/scoring/rules.py`
- Modify: `backend/app/services/analysis_service.py`

- [x] **Step 1：写失败测试：rag_retriever 节点**

4 个测试全部通过。

- [x] **Step 2：修改 CareerFitState**

新增 `rag_results: dict[str, Any]` 字段。

- [x] **Step 3：实现 rag_retriever 节点**

`rag_retriever` 节点传递预计算的 `rag_results`，无预计算结果时返回"知识库证据不足"。

- [x] **Step 4：修改 NODE_SEQUENCE**

在 `resume_parser` 和 `match_scorer` 之间插入 `rag_retriever`。

- [x] **Step 5：修改评分层**

`score_match` 新增可选 `rag_results` 参数，每个 score_item 新增 `knowledge_evidence` 字段。4 个评分测试通过。

- [x] **Step 6：修改 analysis_service**

在 `create_analysis` 中预计算 RAG 结果，传入工作流初始状态。

- [x] **Step 7：运行 Agent 节点测试**

8 个测试全部通过。

---

## Task 5：种子知识库

**Files:**

- Create: `backend/seeds/backend_dev.json`
- Create: `backend/seeds/frontend_fullstack.json`
- Create: `backend/seeds/llm_app_dev.json`

- [x] **Step 1：编写后端开发种子数据**

5 个技能定义 + 1 个岗位画像 + 1 组面试题 + 1 组学习资源，共 8 篇。

- [x] **Step 2：编写前端/全栈种子数据**

4 个技能定义 + 1 个岗位画像 + 1 组面试题 + 1 组学习资源，共 7 篇。

- [x] **Step 3：编写大模型应用种子数据**

4 个技能定义 + 1 个岗位画像 + 1 组面试题 + 1 组学习资源，共 7 篇。

- [x] **Step 4：验证种子数据导入**

通过 API 导入 22 篇文档（21 新导入 + 1 之前手动导入），超过 20 篇门槛。

---

## Task 6：前端适配

**Files:**

- Modify: `frontend/src/components/report/EvidenceCard.vue`
- Modify: `frontend/src/stores/availability.ts`
- Modify: `frontend/src/api/availability.ts`
- Modify: `frontend/src/api/reports.ts`

- [x] **Step 1：EvidenceCard 展示 knowledge_evidence**

当 `knowledge_evidence` 存在且 `available: true` 时，展示知识库标准引用。当 `available: false` 时，展示"知识库证据不足"标签。

- [x] **Step 2：availability store 消费 knowledge capability**

`/api/capabilities` 返回 `knowledge: "ready"` 时 store 正确标记。

- [x] **Step 3：运行前端测试**

typecheck 和 build 通过。

---

## Task 7：全量回归与文档同步

**Files:**

- Modify: `TODOS.md`
- Modify: `docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2d-test-plan.md`

- [x] **Step 1：后端全量测试**

Phase 2D 新增测试全部通过（22 个新测试）。

- [x] **Step 2：前端全量测试**

typecheck 和 build 通过。

- [ ] **Step 3：Docker smoke**

需要启动 Docker Desktop 后补跑。

- [ ] **Step 4：文档同步检查**

待执行。

- [ ] **Step 5：提交 Phase 2D 实现**

待执行。

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| Embedding 模型 | sentence-transformers all-MiniLM-L6-v2 (384维) | 本地运行，不依赖外部 API，80MB 模型大小可接受 | 需要更高精度或多语言支持 |
| 向量数据库 | pgvector（已有 PostgreSQL） | 不引入新服务，与现有架构一致 | 查询性能不足，需要专用向量数据库 |
| SQLite 测试策略 | JSON 模拟向量搜索 + 余弦相似度 | SQLite 不支持 pgvector，测试环境用关键词匹配模拟 | 测试与生产行为差异过大 |
| 种子数据格式 | JSON 文件 | 简单可读，便于版本控制 | 需要更复杂的增量更新机制 |
| 检索策略 | 按技能关键词检索 | JD 已解析出 required_skills，直接用技能名检索 | 需要更细粒度的语义检索 |
| RAG 预计算位置 | analysis_service 中预计算，传入工作流初始状态 | 保持工作流节点纯函数特性，DB 访问留在 service 层 | 需要工作流内部动态检索 |

## 风险与缓解

- **风险：sentence-transformers 模型首次下载慢。** 缓解：Docker 构建时预下载模型；本地开发首次运行自动下载，失败时回退关键词匹配。
- **风险：pgvector 在 SQLite 测试环境不可用。** 缓解：测试环境使用 JSON 模拟向量搜索，余弦相似度 + 关键词匹配。
- **风险：种子知识库质量不够。** 缓解：先覆盖三组核心岗位，后续可增量补充。
- **风险：检索结果干扰评分。** 缓解：检索结果只作为证据，不改变评分公式。已验证 RAG 不改变分数。
