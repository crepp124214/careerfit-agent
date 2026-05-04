# CareerFit Agent Phase 2D RAG 知识库设计文档

日期：2026-05-04

## 背景

Phase 1–2C 已完成核心业务闭环：岗位→简历→分析→评分→证据链→Integrity Guard→优化建议→学习任务→Next Best Action→历史趋势→版本对比→LLM 增强。

但当前评分完全基于 JD 和简历的文本匹配，缺少知识库标准作为第三方参考。设计蓝图要求"每个评分项必须能追溯到 JD 要求、简历证据、**知识库标准**"，目前缺少知识库标准这一环。

RAG 检索结果应进入评分标准、面试题和学习任务，而不是装饰。

## 目标

1. 新增 `knowledge_documents` 表和 pgvector 索引，存储技能定义、岗位画像、面试题和学习资源四类文档。
2. 新增 `rag_retriever` Agent 节点，在工作流中 `match_scorer` 之前执行检索。
3. 评分层消费检索结果：每个 score_item 增加可选的 `knowledge_evidence` 字段。
4. 检索不到相关文档时标记"知识库证据不足"，不编造来源。
5. 新增 `POST /api/knowledge/import` 和 `GET /api/knowledge/search` API。
6. 提供三组种子知识库：后端开发、前端/全栈、大模型应用开发。
7. `/api/capabilities` 增加 `knowledge` 状态。

## 非目标

- 不新增用户上传文档功能（Phase 2D 只支持管理员种子导入）。
- 不新增向量数据库服务（使用已有的 pgvector）。
- 不新增 embedding 模型服务（使用 sentence-transformers 本地模型或 OpenAI embedding API）。
- 不做知识库版本管理或增量更新。
- 不让 LLM 直接决定检索策略或评分。

## 数据库设计

### knowledge_documents 表

```text
knowledge_documents
  id              SERIAL PRIMARY KEY
  doc_type        VARCHAR(50) NOT NULL     -- skill / job_profile / interview / learning
  title           VARCHAR(500) NOT NULL
  content         TEXT NOT NULL
  metadata        JSONB NOT NULL DEFAULT '{}'  -- 含 schema_version
  embedding       vector(384)               -- pgvector 向量列，维度取决于 embedding 模型
  created_at      TIMESTAMPTZ DEFAULT now()
```

索引：
- `idx_knowledge_doc_type` ON (doc_type)
- `idx_knowledge_embedding` ON (embedding) USING ivfflat WITH (lists = 100) -- 向量近似搜索

`metadata` 字段结构：
```json
{
  "schema_version": "1",
  "skill_name": "FastAPI",
  "difficulty": "intermediate",
  "job_family": ["backend"],
  "source_type": "seed",
  "tags": ["python", "web", "api"]
}
```

## RAG 架构

### Embedding 策略

Phase 2D 使用本地 sentence-transformers 模型（`all-MiniLM-L6-v2`，384 维），避免依赖外部 API。如果后续需要更高精度，可切换到 OpenAI embedding API。

### 检索流程

```text
用户提交分析
  -> jd_parser 解析 JD
  -> resume_parser 解析简历
  -> rag_retriever 检索知识库
     -> 从 jd_profile.required_skills 提取技能关键词
     -> 对每个技能关键词生成 embedding
     -> 在 knowledge_documents 中做向量近似搜索
     -> 返回每个技能的 top-k 相关文档片段
  -> match_scorer 评分（消费检索结果）
  -> gap_analyzer
  -> resume_optimizer
  -> interview_coach（消费检索结果）
  -> learning_planner（消费检索结果）
  -> next_best_action
```

### 检索结果结构

```json
{
  "skill_name": {
    "documents": [
      {
        "doc_id": 1,
        "doc_type": "skill",
        "title": "FastAPI 技能定义",
        "content_snippet": "...",
        "score": 0.87,
        "metadata": {"skill_name": "FastAPI", "difficulty": "intermediate"}
      }
    ],
    "available": true
  },
  "UnknownSkill": {
    "documents": [],
    "available": false,
    "reason": "知识库证据不足"
  }
}
```

## API 设计

### POST /api/knowledge/import

导入知识文档（批量）。

请求体：
```json
{
  "documents": [
    {
      "doc_type": "skill",
      "title": "FastAPI 技能定义",
      "content": "FastAPI 是一个高性能 Python Web 框架...",
      "metadata": {"skill_name": "FastAPI", "difficulty": "intermediate", "job_family": ["backend"]}
    }
  ]
}
```

响应：
```json
{
  "schema_version": "1",
  "imported_count": 1,
  "skipped_count": 0
}
```

### GET /api/knowledge/search

搜索知识文档。

参数：`q`（查询文本）、`doc_type`（可选过滤）、`limit`（默认 5）。

响应：
```json
{
  "schema_version": "1",
  "results": [
    {
      "id": 1,
      "doc_type": "skill",
      "title": "FastAPI 技能定义",
      "content_snippet": "...",
      "score": 0.92,
      "metadata": {"skill_name": "FastAPI"}
    }
  ]
}
```

## 评分层变更

### score_items 新增字段

每个 score_item 新增可选字段：

```json
{
  "skill": "FastAPI",
  "level": "project_practice",
  "score": 75,
  "jd_evidence": ["Need FastAPI experience"],
  "resume_evidence": ["Built FastAPI backend services"],
  "knowledge_evidence": [
    {
      "doc_id": 1,
      "title": "FastAPI 技能定义",
      "snippet": "项目实践级别要求能独立设计和实现 API 端点...",
      "available": true
    }
  ]
}
```

当检索不到时：
```json
{
  "knowledge_evidence": [
    {
      "available": false,
      "reason": "知识库证据不足"
    }
  ]
}
```

### 评分公式不变

RAG 检索结果只作为证据和标准来源，不改变评分公式。LLM 不直接决定最终分数。

## CareerFitState 变更

新增字段：

```python
class CareerFitState(TypedDict, total=False):
    # ... 现有字段 ...
    rag_results: dict[str, Any]  # 按技能名索引的检索结果
```

## 工作流变更

```text
NODE_SEQUENCE 变更：
  jd_parser
  resume_parser
  rag_retriever      # 新增
  match_scorer       # 消费 rag_results
  gap_analyzer
  resume_optimizer
  interview_coach    # 消费 rag_results
  learning_planner   # 消费 rag_results
  next_best_action
```

## 种子知识库

三组种子文档，每组覆盖 5–8 个核心技能：

### 后端开发

| 技能 | doc_type | 内容 |
|------|----------|------|
| FastAPI | skill | 技能定义、能力层级、项目证据标准 |
| SQLAlchemy | skill | 技能定义、能力层级、项目证据标准 |
| PostgreSQL | skill | 技能定义、能力层级、项目证据标准 |
| Redis | skill | 技能定义、能力层级、项目证据标准 |
| Docker | skill | 技能定义、能力层级、项目证据标准 |
| 后端开发岗位画像 | job_profile | 核心技能、加分技能、面试关注点 |
| 后端面试题 | interview | 基础题、项目深挖题、场景设计题 |
| 后端学习资源 | learning | 学习路径、实践任务、验收标准 |

### 前端/全栈

| 技能 | doc_type | 内容 |
|------|----------|------|
| React | skill | 技能定义、能力层级、项目证据标准 |
| TypeScript | skill | 技能定义、能力层级、项目证据标准 |
| Vue.js | skill | 技能定义、能力层级、项目证据标准 |
| CSS/响应式 | skill | 技能定义、能力层级、项目证据标准 |
| 前端岗位画像 | job_profile | 核心技能、加分技能、面试关注点 |
| 前端面试题 | interview | 基础题、项目深挖题、场景设计题 |
| 前端学习资源 | learning | 学习路径、实践任务、验收标准 |

### 大模型应用开发

| 技能 | doc_type | 内容 |
|------|----------|------|
| LangChain/LangGraph | skill | 技能定义、能力层级、项目证据标准 |
| Prompt Engineering | skill | 技能定义、能力层级、项目证据标准 |
| RAG | skill | 技能定义、能力层级、项目证据标准 |
| Vector Database | skill | 技能定义、能力层级、项目证据标准 |
| 大模型应用岗位画像 | job_profile | 核心技能、加分技能、面试关注点 |
| 大模型面试题 | interview | 基础题、项目深挖题、场景设计题 |
| 大模型学习资源 | learning | 学习路径、实践任务、验收标准 |

## 前端变更

- 前端不直接消费知识库 API；知识库结果通过报告的 `knowledge_evidence` 字段间接展示。
- 报告页 EvidenceCard 新增可选的"知识库标准"引用。
- 如果 `knowledge_evidence` 为空或 `available: false`，展示"知识库证据不足"标签。
- `/api/capabilities` 新增 `knowledge` 状态，前端 availability store 消费。

## 隐私约束

- 知识库文档不包含用户 PII，只包含公开技术知识。
- 检索查询不包含完整 JD 或简历原文，只使用技能关键词。
- Agent trace 不保存 embedding 向量或完整检索结果，只保存检索摘要（命中数量和 top-1 标题）。
- `/api/knowledge/search` 响应不包含用户数据。

## 依赖

- `sentence-transformers`：本地 embedding 模型（`all-MiniLM-L6-v2`，约 80MB）。
- `pgvector`：已在 Docker Compose 中配置，SQLite 测试环境使用 JSON 模拟。

## 成功标准

- `knowledge_documents` 表存在且含 pgvector 索引。
- 种子知识库导入后至少包含 20 篇文档。
- `rag_retriever` 节点在工作流中正确执行，检索结果写入 `rag_results`。
- 每个 score_item 包含 `knowledge_evidence` 字段。
- 检索不到时 `available: false` + 中文原因。
- `POST /api/knowledge/import` 和 `GET /api/knowledge/search` 可用。
- `/api/capabilities` 返回 `knowledge: "ready"`。
- 后端全量测试通过。
- 前端全量测试、typecheck、build 通过。

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| sentence-transformers 模型下载慢或失败 | 首次启动时自动下载，失败时回退到关键词匹配 |
| pgvector 在 SQLite 测试环境不可用 | 测试环境使用 JSON 模拟向量搜索 |
| 种子知识库质量不够 | 先覆盖三组核心岗位，后续可增量补充 |
| embedding 维度与模型不匹配 | 固定使用 all-MiniLM-L6-v2 (384维)，不混用模型 |
| 检索结果干扰评分 | 检索结果只作为证据，不改变评分公式 |
