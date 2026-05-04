# CareerFit Agent Phase 2D RAG 知识库测试计划

日期：2026-05-04

## 测试目标

验证 Phase 2D 的 RAG 知识库是真实数据驱动、确定性、可解释且不泄露用户 PII。

---

## 后端测试

### 1. Embedding 模块 (`tests/test_rag_retrieval.py`)

```powershell
cd backend
pytest tests/test_rag_retrieval.py -q
```

**覆盖点**：
- `generate_embedding("FastAPI")` 返回 384 维浮点数组
- `generate_embeddings(["FastAPI", "Python"])` 返回两个 384 维数组
- 空字符串返回零向量或抛出明确错误
- 模型加载失败时回退到关键词匹配模式，不抛出异常

### 2. 向量检索 (`tests/test_rag_retrieval.py`)

**覆盖点**：
- `retrieve_by_skill(db, "FastAPI", top_k=3)` 返回相关文档列表
- 每个结果包含 `doc_id`、`doc_type`、`title`、`content_snippet`、`score`、`metadata`
- 结果按相似度降序排列
- 不存在的技能返回空列表，`available: false`
- `top_k` 限制生效
- `doc_type` 过滤生效

### 3. Knowledge API (`tests/test_knowledge_api.py`)

```powershell
cd backend
pytest tests/test_knowledge_api.py -q
```

**覆盖点**：
- `POST /api/knowledge/import` 批量导入文档，返回 `imported_count` 和 `skipped_count`
- 导入的文档包含 `schema_version`
- 重复导入幂等（相同 title + doc_type 不重复插入）
- `GET /api/knowledge/search?q=FastAPI` 返回相关文档
- `GET /api/knowledge/search?q=FastAPI&doc_type=skill` 只返回技能类型文档
- `GET /api/knowledge/search?q=FastAPI&limit=2` 限制返回数量
- 空查询返回空列表
- 响应不包含用户 PII

### 4. rag_retriever Agent 节点 (`tests/test_rag_agent_node.py`)

```powershell
cd backend
pytest tests/test_rag_agent_node.py -q
```

**覆盖点**：
- `rag_retriever(state)` 返回 `rag_results` 字段
- `rag_results` 按 `jd_profile.required_skills` 索引
- 每个技能有 `documents` 和 `available` 字段
- 有匹配文档时 `available: true`
- 无匹配文档时 `available: false` + 中文原因"知识库证据不足"
- 空技能列表返回空 `rag_results`

### 5. 评分层 knowledge_evidence (`tests/test_scoring_with_rag.py`)

```powershell
cd backend
pytest tests/test_scoring_with_rag.py -q
```

**覆盖点**：
- `score_match(jd_profile, resume_profile, rag_results)` 每个 score_item 包含 `knowledge_evidence`
- `knowledge_evidence` 包含 `doc_id`、`title`、`snippet`、`available`
- 无 rag_results 时 `knowledge_evidence` 为空列表
- 检索不到时 `available: false` + 中文原因
- 评分公式不变（RAG 不改变分数）

---

## 前端测试

### 1. EvidenceCard 知识库证据 (`tests/components/EvidenceCard.test.ts`)

```powershell
cd frontend
npm test -- --run tests/components/EvidenceCard.test.ts
```

**覆盖点**：
- `knowledge_evidence` 存在且 `available: true` 时展示知识库标准引用
- `knowledge_evidence` 存在且 `available: false` 时展示"知识库证据不足"标签
- 无 `knowledge_evidence` 时不展示知识库区域

### 2. Availability store (`tests/stores/availability.test.ts`)

**覆盖点**：
- `/api/capabilities` 返回 `knowledge: "ready"` 时 store 正确标记
- `/api/capabilities` 返回 `knowledge: "unavailable"` 时 store 正确标记

---

## 全量回归

```powershell
# 后端
cd backend && pytest -q

# 前端
cd frontend && npm test && npm run typecheck && npm run build

# 文档
git diff --check

# Docker smoke
docker compose up --build
```

**验收标准**：
- backend health OK
- `/api/capabilities` 返回 `knowledge: "ready"`
- `/api/knowledge/search?q=FastAPI` 返回至少 1 条结果
- `/api/knowledge/search?q=UnknownSkillXYZ` 返回空列表
- 分析报告的 score_items 包含 `knowledge_evidence` 字段

---

## 隐私检查

- ❌ 知识库 API 响应不包含用户 PII
- ❌ 检索查询不包含完整 JD 或简历原文
- ❌ Agent trace 不保存 embedding 向量或完整检索结果
- ❌ 前端 localStorage / IndexedDB 不保存知识库文档内容
- ⚠️ 如果触碰简历/JD 解析、Agent prompt 装配或向量入库，必须补跑 `gstack:cso`
