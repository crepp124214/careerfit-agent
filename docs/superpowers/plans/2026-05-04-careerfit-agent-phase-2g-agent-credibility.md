# CareerFit Phase 2G 多 Agent 可信分析实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 把当前“多节点 workflow + 单次 LLM 增强”升级为可验证的混合式多 Agent 可信分析，并修复数据分析师场景下评分维度缺失和 RAG 不相关问题。

**架构:** 后端新增独立 LLM Agent service 与 Pydantic 输出 schema；语义解析、检索规划、缺口解释、简历建议、面试题、学习路径、Next Best Action 分别有独立产物。最终数字评分仍由确定性 `match_scorer` 计算，RAG 执行和 Integrity Guard 硬规则保持可复现，Agent Trace 增加执行方式、fallback、schema 校验和模型元数据。

**技术栈:** FastAPI、Pydantic、SQLAlchemy、pytest、现有 OpenAI-compatible LLM client、Vue3、Pinia、Vitest。

---

## 文件结构

### 后端新增或修改

- 修改 `backend/app/agents/state.py`：增加 `skill_dimensions`、`rag_queries`、`agent_execution_meta`、`integrity_result` 等状态字段。
- 修改 `backend/app/agents/graph.py`：调整节点顺序；trace 写入 `execution_mode`、`agent_role`、`model_name`、`fallback_used`、`schema_valid`、`retry_count`。
- 修改 `backend/app/agents/nodes.py`：拆分当前单次 `generate_report_enhancement()` 依赖，改成各节点调用独立 service。
- 修改 `backend/app/db/models.py`：为 `AgentRun` 增加 `execution_meta` JSON 字段，避免 trace 顶层元数据无法落库。
- 修改 `backend/app/schemas/reports.py`：`AgentRunRead` 增加 `execution_meta` 字段，保持 API 合约显式。
- 修改 `backend/app/services/analysis_service.py`：确保 `run_workflow -> AgentRun DB -> /api/agent-runs` 全链路保留 `execution_meta`。
- 新增 `backend/app/llm/agent_schemas.py`：定义 `JDParseOutput`、`ResumeParseOutput`、`RagQueryPlanOutput`、`GapAnalysisOutput`、`ResumeSuggestionOutput`、`InterviewQuestionOutput`、`LearningPlanOutput`、`NextBestActionOutput`、`IntegrityCriticOutput`。
- 新增 `backend/app/llm/agent_prompts.py`：分别构建各 Agent 的中文 prompt；所有 prompt 只接收脱敏或结构化输入。
- 新增 `backend/app/llm/agent_service.py`：统一执行 LLM 调用、一次 JSON 修复重试、schema 校验、fallback 标记。
- 修改 `backend/app/llm/service.py`：保留兼容入口，逐步迁移到 `agent_service.py`。
- 修改 `backend/app/services/job_service.py`：规则 fallback 支持数据分析技能目录和岗位族识别。
- 修改 `backend/app/services/resume_service.py`：规则 fallback 支持数据分析技能和证据抽取。
- 修改 `backend/app/scoring/rules.py`：优先消费结构化 `skill_dimensions`；保留旧 `required_skills` 兼容。
- 修改 `backend/app/rag/retrieval.py`：增加岗位族、文档类型、阈值过滤。
- 修改 `backend/app/rag/loader.py`：加载数据分析种子文档。
- 新增 `backend/seeds/data_analysis.json`：SQL、Python 数据分析、统计方法、A/B 测试、数据可视化、机器学习基础、业务分析、数据分析面试题等文档。
- 修改 `backend/app/services/interview_service.py`：使用 `interview_coach_agent` 的分类题型，保持状态流转不变。
- 修改 `backend/app/services/learning_service.py`：使用 `learning_planner_agent` 的路径化任务，保持 PII 约束。

### 前端新增或修改

- 修改 `frontend/src/components/report/AgentTraceRow.vue`：展示执行方式、fallback、schema 校验和人类可读节点名。
- 修改 `frontend/src/components/report/AgentTraceTimeline.vue`：支持按执行方式筛选或折叠，不展示原文。
- 修改 `frontend/src/api/agentRuns.ts`：扩展后端 trace 响应类型并在 normalize 时保留 `execution_meta`，否则组件拿不到真实执行方式。
- 修改 `frontend/src/views/ReportView.vue`：报告维度增加知识库相关性提示；面试题和学习任务展示非模板化字段。
- 修改 `frontend/src/components/report/EvidenceCard.vue`：低相关 RAG 结果显示“知识库证据不足”，不展示无关文档。

### 测试

- 新增 `backend/tests/test_agent_schemas.py`
- 新增 `backend/tests/test_multi_agent_llm_flow.py`
- 新增 `backend/tests/test_data_analysis_dimension_extraction.py`
- 新增 `backend/tests/test_rag_relevance_filtering.py`
- 修改 `backend/tests/test_analysis_flow.py`
- 修改 `backend/tests/test_scoring.py`
- 修改 `backend/tests/test_interview_service.py`
- 修改 `backend/tests/test_learning_api.py`
- 修改 `frontend/tests/components/AgentTraceTimeline.test.ts`
- 修改 `frontend/tests/views/ReportView.test.ts`

---

## /autoplan 审查修订摘要

本计划已按 `gstack:autoplan` 口径完成 CEO/Product、Design、Eng、安全四类审查。外部 `codex` CLI 在本机不可用，错误为缺少 `@openai/codex-win32-x64` optional dependency；本次采用两个独立 explorer 声部 + 本地 Codex 审查，Codex CLI 声部标记为 unavailable。

### 自动采纳的 P0 修订

- **AgentRun 持久化契约必须前置**：`execution_meta` 不能只写在 `graph.py` trace dict 里，必须同步落到 `AgentRun` DB model、`AgentRunRead` schema、`/api/agent-runs` 响应和 `frontend/src/api/agentRuns.ts` normalize 层。
- **RAG 检索边界必须明确**：`rag_query_planner_agent` 只产出 query plan；真实 DB 检索保留在 `analysis_service` 或显式注入 workflow，禁止在没有 `db` 的 `rag_retriever` 节点里假装能查库。
- **Prompt PII 边界必须改写**：除 `jd_parser_agent` 和 `resume_parser_agent` 的受控解析边界外，其他 Agent 只接收脱敏或结构化输入；解析 Agent 的原文不得进入 trace、日志、异常详情、repair prompt 外泄或前端响应。
- **LLM 失败契约必须可追踪**：第二次 schema 校验失败时，必须记录 `schema_valid=false`、`retry_count=1`、`fallback_used`、`error_code`，并让 graph 写入 failed trace，不得只抛异常丢失上下文。
- **数据分析端到端验收必须写死**：使用 UX 评估里的数据分析师 JD/简历，报告必须产出至少 5 个维度，且每个维度包含 JD 证据、简历证据、评分项、知识库状态和缺口解释。

### 自动采纳的 P1 修订

- `gap_analyzer_agent` 和 `integrity_critic_agent` 不能只出现在 schema，Task 5 必须明确调用或明确延后；本计划选择实现 `gap_analyzer_agent`，`integrity_critic_agent` 只做可选辅助解释，不能替代硬规则 `Integrity Guard`。
- Trace 默认展示用户语言的可信摘要，技术字段放展开详情；`model_name`、`retry_count`、fallback 不能压过用户真正关心的“这会不会影响结论”。
- 报告页必须至少做分组或折叠，避免 Phase 2G 增加更多维度和 trace meta 后继续纵向堆叠。
- 用户报告中提到但不进入 Phase 2G 的时间戳格式化、版本名称重复、报告返回入口，记录为 Phase 2G 外 deferred，不在本阶段混入。

### 决策审计

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
| 1 | CEO | Phase 2G 保持聚焦“分析可信度”，不混入列表视觉、空状态插图、趋势图等 P2 抛光 | Auto-decide | Hold Scope | 当前最伤用户信任的是分析质量和假多 Agent；UI 小修可延后 | 把 UX 报告所有 P1/P2 一次性纳入 |
| 2 | Eng | `execution_meta` 使用独立 DB/API 字段，而不是塞进 `output_snapshot` | Auto-decide | Explicit > clever | 独立字段能被 schema、API、前端类型和测试明确覆盖 | 把 meta 藏在 output snapshot |
| 3 | Eng | RAG 真实检索保留在 service 层，`rag_query_planner_agent` 只产出 query plan | Auto-decide | Clear boundaries | 当前 workflow 没有 db 注入；service 层已有 DB session，改动更小更可靠 | 给 `run_workflow` 引入 service locator |
| 4 | Security | 解析 Agent 可接收原文，但原文禁止进入 trace、日志、异常详情和前端响应 | Auto-decide | Sensitive boundary | JD/简历解析无法完全脱离原文，但传播面必须收窄 | 声称所有 prompt 都只接收脱敏输入 |
| 5 | Design | Trace 默认展示可信摘要，技术执行元数据放详情 | Auto-decide | User trust first | 普通应届生要先理解结果可靠性，不是先看内部调试字段 | 默认展开全部技术字段 |

### NOT in scope

- 时间戳格式化：用户已指出，但与多 Agent 可信度无直接依赖，延后到前端 UX 收口。
- 版本名称重复：用户已指出，延后到前端 UX 收口。
- 报告返回入口 / 面包屑：用户已指出，延后到报告信息架构收口。
- 岗位/简历列表视觉丰富化、空状态插图、进度条配色：P2 抛光项，不进入 Phase 2G。
- 面试回答评分闭环：需要新的用户输入和评分模型，不进入本阶段。

### What already exists

- `backend/app/agents/graph.py` 已有顺序 workflow 和 trace 结构，但缺少 `execution_meta`、失败 trace 和 DB schema 合约。
- `backend/app/llm/service.py` 已有 OpenAI-compatible client 接入和一次 JSON 修复重试，但当前只服务一次性报告增强。
- `backend/app/services/analysis_service.py` 已有 DB session 和分析任务编排，是 Phase 2G 保留真实 RAG 检索的正确边界。
- `backend/app/rag/retrieval.py` 已有 pgvector / JSON fallback 检索，但缺岗位族过滤、阈值过滤和最终报告级相关性测试。
- `frontend/src/api/agentRuns.ts` 已有后端 trace normalize 层，必须在这里接住 `execution_meta`，只改组件不够。

### Failure Modes Registry

| Failure mode | Impact | Planned coverage | Critical gap |
|---|---|---|---|
| `execution_meta` 顶层字段无法落库 | 分析任务在持久化 agent runs 时失败 | Task 1 新增 DB/schema/API 测试 | 否，已前置修订 |
| RAG 仍用旧 `required_skills` 检索 | 数据分析报告继续召回 FastAPI/后端文档 | Task 4 新增 analysis_service 集成测试 | 否，已前置修订 |
| 第二次 LLM JSON 修复仍失败 | trace 丢失失败原因，用户只看到任务失败 | Task 1 失败矩阵测试 | 否，已前置修订 |
| 解析 Agent 原文进入 repair prompt 或日志 | PII 二次传播 | Task 1/5 轻量 PII 测试 + Task 7 安全审计 | 否，已前置修订 |
| 前端组件测试通过但真实 API meta 丢失 | Trace 仍无法展示真实执行方式 | Task 6 增加真实后端响应 shape 测试 | 否，已前置修订 |
| SQLAlchemy 被误识别为数据分析 SQL | 后端岗被错误打成数据分析匹配 | Task 2 增加误匹配测试 | 否，已前置修订 |

### Error & Rescue Registry

| Error | User-visible result | Rescue behavior |
|---|---|---|
| LLM provider unavailable | 分析仍完成，但 trace 显示本地规则 fallback | fallback 输出通过同一 schema 校验 |
| LLM 返回非法 JSON，修复仍失败 | 对应 Agent 节点 failed，任务按可恢复策略降级或失败 | failed trace 记录 `schema_valid=false` 和 `error_code` |
| RAG 无相关数据分析文档 | 报告显示“知识库证据不足” | 不展示无关后端文档顶替 |
| 数据分析 JD 抽取少于 5 个维度 | 分析质量门失败 | 测试阻止 ship |
| Agent Trace 含 raw JD/resume | 前端不渲染，后端测试失败 | trace redaction 和 API 测试双层阻断 |

### Dream state delta

Phase 2G 后，CareerFit 会从“一个能跑的求职分析工具”变成“用户能看懂为什么可信的分析工作台”。距离 12 个月理想状态仍缺：更多岗位族知识库、面试回答评分、真实成本观测、生产级异步调度和可视化质量仪表盘。

### Cross-phase themes

- **可信度不是 Trace 字段数量**：CEO/UX 和 Eng 声部都指出，必须把技术 trace 转成用户能理解的可信摘要。
- **边界显式比聪明封装重要**：Eng 和 Security 声部都指出，`execution_meta`、RAG DB 检索、prompt 原文边界必须显式写进 schema 和服务层。
- **测试必须覆盖最终报告，不只覆盖纯函数**：两个声部都指出，`filter_relevant_documents()` 通过不等于用户报告可信。

## Task 1：建立多 Agent 输出 schema 与统一执行器

**Files:**

- Create: `backend/app/llm/agent_schemas.py`
- Create: `backend/app/llm/agent_service.py`
- Modify: `backend/app/db/models.py`
- Modify: `backend/app/schemas/reports.py`
- Modify: `backend/app/services/analysis_service.py`
- Create: `backend/tests/test_agent_schemas.py`
- Create: `backend/tests/test_multi_agent_llm_flow.py`
- Modify: `backend/tests/test_analysis_flow.py`

- [ ] **Step 1：写失败的 schema 测试**

在 `backend/tests/test_agent_schemas.py` 中新增测试：

```python
import pytest
from pydantic import ValidationError

from app.llm.agent_schemas import JDParseOutput, SkillDimension


def test_skill_dimension_requires_evidence_and_valid_weight():
    item = SkillDimension(
        name="SQL",
        canonical_key="sql",
        category="data_analysis",
        weight=0.2,
        required_level="project_practice",
        jd_evidence=["熟练使用 SQL 进行数据提取和分析"],
        aliases=["SQL", "数据库查询"],
    )

    assert item.canonical_key == "sql"


def test_skill_dimension_rejects_empty_evidence():
    with pytest.raises(ValidationError):
        SkillDimension(
            name="SQL",
            canonical_key="sql",
            category="data_analysis",
            weight=0.2,
            required_level="project_practice",
            jd_evidence=[],
            aliases=["SQL"],
        )


def test_jd_parse_output_requires_multiple_dimensions_for_data_analysis_fixture():
    output = JDParseOutput(
        job_family="data_analysis",
        dimensions=[
            SkillDimension(
                name="SQL",
                canonical_key="sql",
                category="data_analysis",
                weight=0.2,
                required_level="project_practice",
                jd_evidence=["熟练使用 SQL"],
                aliases=["SQL"],
            ),
            SkillDimension(
                name="Python",
                canonical_key="python",
                category="programming",
                weight=0.2,
                required_level="project_practice",
                jd_evidence=["熟悉 Python"],
                aliases=["Python"],
            ),
        ],
        evidence_summary="岗位要求数据提取、Python 分析和实验评估。",
    )

    assert output.job_family == "data_analysis"
    assert len(output.dimensions) == 2
```

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_agent_schemas.py -q
```

Expected: FAIL，提示 `app.llm.agent_schemas` 不存在。

- [ ] **Step 3：实现 `agent_schemas.py`**

实现以下 Pydantic 模型：

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    canonical_key: str
    category: str
    weight: float = Field(ge=0, le=1)
    required_level: Literal["mentioned", "basic_usage", "project_practice", "deep_experience"]
    jd_evidence: list[str] = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)

    @field_validator("name", "canonical_key", "category")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("字段不能为空")
        return stripped


class JDParseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_family: str
    dimensions: list[SkillDimension] = Field(min_length=1)
    evidence_summary: str


class ResumeEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    evidence: list[str] = Field(default_factory=list)
    expression_level: Literal["not_mentioned", "mentioned", "basic_usage", "project_practice", "deep_experience"]


class ResumeParseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[ResumeEvidenceItem]
    project_summary: str
    evidence_summary: str


class RagQueryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    query: str
    job_family: str
    doc_types: list[str] = Field(default_factory=list)


class RagQueryPlanOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queries: list[RagQueryItem] = Field(min_length=1)


class GapItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    gap_type: Literal["missing_skill", "weak_evidence", "expression_gap", "knowledge_insufficient"]
    reason: str
    priority: Literal["high", "medium", "low"]


class GapAnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gaps: list[GapItem]
    strengths: list[dict]


class ResumeSuggestionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[dict]


class InterviewQuestionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[dict]


class LearningPlanOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[dict]


class NextBestActionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    target_skill: str | None = None


class IntegrityCriticOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["low", "medium", "high"]
    risk_codes: list[str] = Field(default_factory=list)
    reason: str
```

- [ ] **Step 4：运行 schema 测试确认通过**

Run:

```powershell
cd backend
pytest tests/test_agent_schemas.py -q
```

Expected: PASS。

- [ ] **Step 5：写失败的 Agent 执行器测试**

在 `backend/tests/test_multi_agent_llm_flow.py` 中新增测试：

```python
from app.llm.agent_schemas import JDParseOutput
from app.llm.agent_service import run_structured_agent


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)


def test_run_structured_agent_repairs_invalid_json_once():
    client = FakeClient([
        "不是 JSON",
        '{"job_family":"data_analysis","dimensions":[{"name":"SQL","canonical_key":"sql","category":"data_analysis","weight":0.5,"required_level":"project_practice","jd_evidence":["熟练 SQL"],"aliases":["SQL"]}],"evidence_summary":"需要 SQL"}',
    ])

    result, meta = run_structured_agent(
        client=client,
        agent_role="jd_parser_agent",
        prompt="parse jd",
        output_model=JDParseOutput,
    )

    assert result.job_family == "data_analysis"
    assert meta["agent_role"] == "jd_parser_agent"
    assert meta["execution_mode"] == "llm"
    assert meta["schema_valid"] is True
    assert meta["retry_count"] == 1
    assert len(client.calls) == 2


def test_run_structured_agent_uses_fallback_when_disabled():
    fallback_value = JDParseOutput(
        job_family="data_analysis",
        dimensions=[{
            "name": "SQL",
            "canonical_key": "sql",
            "category": "data_analysis",
            "weight": 1,
            "required_level": "project_practice",
            "jd_evidence": ["熟练 SQL"],
            "aliases": ["SQL"],
        }],
        evidence_summary="规则解析结果",
    )

    result, meta = run_structured_agent(
        client=None,
        agent_role="jd_parser_agent",
        prompt="parse jd",
        output_model=JDParseOutput,
        enabled=False,
        fallback=lambda: fallback_value,
    )

    assert result.job_family == "data_analysis"
    assert meta["execution_mode"] == "rule"
    assert meta["fallback_used"] is True
    assert meta["schema_valid"] is True
```

- [ ] **Step 6：补充失败矩阵和 AgentRun 持久化测试**

在 `backend/tests/test_multi_agent_llm_flow.py` 追加：

```python
import pytest


def test_run_structured_agent_marks_schema_invalid_after_repair_failure():
    client = FakeClient(["不是 JSON", "仍然不是 JSON"])

    with pytest.raises(Exception):
        run_structured_agent(
            client=client,
            agent_role="jd_parser_agent",
            prompt="parse jd",
            output_model=JDParseOutput,
        )

    assert len(client.calls) == 2
```

在 `backend/tests/test_analysis_flow.py` 追加：

```python
def test_agent_run_execution_meta_persisted_and_returned(client):
    job_resp = client.post("/api/jobs", json={"title": "数据分析师", "raw_text": "需要 SQL 和 Python。"})
    resume_resp = client.post("/api/resumes", json={"candidate_name": "候选人", "version_label": "v1", "raw_text": "使用 SQL 和 Python 做过分析。"})
    task_resp = client.post("/api/analysis", json={"job_id": job_resp.json()["id"], "resume_id": resume_resp.json()["id"]})

    runs_resp = client.get(f"/api/agent-runs/{task_resp.json()['id']}")

    assert runs_resp.status_code == 200
    runs = runs_resp.json()
    assert runs
    assert "execution_meta" in runs[0]
    assert "execution_mode" in runs[0]["execution_meta"]
```

- [ ] **Step 7：运行执行器测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py tests/test_analysis_flow.py::test_agent_run_execution_meta_persisted_and_returned -q
```

Expected: FAIL，提示 `run_structured_agent` 不存在或 `execution_meta` 未落库。

- [ ] **Step 8：实现 `agent_service.py`**

实现统一执行函数：

```python
from __future__ import annotations

import json
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _repair_prompt(text: str) -> str:
    return "请把下面内容修复为严格 JSON，只保留指定字段，不要添加 Markdown：\n" + text


def run_structured_agent(
    *,
    client: Any | None,
    agent_role: str,
    prompt: str,
    output_model: type[T],
    enabled: bool = True,
    fallback: Callable[[], T] | None = None,
    model_name: str | None = None,
) -> tuple[T, dict[str, Any]]:
    if not enabled or client is None:
        if fallback is None:
            raise ValueError("LLM disabled but fallback is missing")
        result = fallback()
        return result, {
            "agent_role": agent_role,
            "execution_mode": "rule",
            "model_name": None,
            "fallback_used": True,
            "schema_valid": True,
            "retry_count": 0,
        }

    retry_count = 0
    first_text = client.complete(prompt)
    try:
        result = output_model.model_validate_json(first_text)
    except (ValidationError, ValueError, json.JSONDecodeError):
        retry_count = 1
        repair_text = client.complete(_repair_prompt(first_text))
        result = output_model.model_validate_json(repair_text)

    return result, {
        "agent_role": agent_role,
        "execution_mode": "llm",
        "model_name": model_name,
        "fallback_used": False,
        "schema_valid": True,
        "retry_count": retry_count,
    }
```

- [ ] **Step 9：新增 AgentRun `execution_meta` 持久化契约**

修改 `backend/app/db/models.py` 的 `AgentRun`：

```python
execution_meta: Mapped[dict] = mapped_column(JSON, default=dict)
```

修改 `backend/app/schemas/reports.py` 的 `AgentRunRead`：

```python
execution_meta: dict = {}
```

修改 `backend/app/agents/graph.py`，确保每个 trace item 都有 `execution_meta`，默认 deterministic：

```python
execution_meta = output.pop("_execution_meta", {
    "agent_role": node_name,
    "execution_mode": "deterministic",
    "model_name": None,
    "fallback_used": False,
    "schema_valid": True,
    "retry_count": 0,
})
```

修改 `backend/app/services/analysis_service.py`，持久化 `AgentRun` 时允许 `execution_meta` 顶层字段进入 DB。

- [ ] **Step 10：运行 Task 1 测试确认通过**

Run:

```powershell
cd backend
pytest tests/test_agent_schemas.py tests/test_multi_agent_llm_flow.py tests/test_analysis_flow.py::test_agent_run_execution_meta_persisted_and_returned -q
```

Expected: PASS。

- [ ] **Step 11：提交 Task 1**

Run:

```powershell
git add backend/app/llm/agent_schemas.py backend/app/llm/agent_service.py backend/app/db/models.py backend/app/schemas/reports.py backend/app/services/analysis_service.py backend/tests/test_agent_schemas.py backend/tests/test_multi_agent_llm_flow.py backend/tests/test_analysis_flow.py docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "feat: add structured multi-agent execution contract"
```

## Task 2：修复数据分析师 JD 维度抽取

**Files:**

- Modify: `backend/app/services/job_service.py`
- Modify: `backend/app/services/resume_service.py`
- Modify: `backend/app/agents/nodes.py`
- Test: `backend/tests/test_data_analysis_dimension_extraction.py`

- [ ] **Step 1：写失败的数据分析师维度测试**

创建 `backend/tests/test_data_analysis_dimension_extraction.py`：

```python
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


DATA_ANALYST_JD = """
岗位：数据分析师
要求：熟练使用 SQL 进行数据提取、清洗和多表关联分析；
熟悉 Python 进行数据处理和自动化分析；
能够使用 Tableau、Power BI 或 ECharts 完成数据可视化；
理解统计方法，能够设计 A/B 测试并评估显著性；
了解机器学习基础，能与算法团队协作完成特征分析。
"""


DATA_ANALYST_RESUME = """
使用 Python 和 pandas 清洗 20 万行运营数据，完成留存分析。
使用 SQL 编写多表关联查询和窗口函数，支持销售看板。
使用 ECharts 构建包含折线图、漏斗图和转化率指标的数据看板。
参与 A/B 测试结果分析，使用统计检验判断实验效果。
"""


def test_data_analyst_jd_extracts_multiple_dimensions():
    profile = parse_job_profile(DATA_ANALYST_JD)
    keys = {item["canonical_key"] for item in profile["skill_dimensions"]}

    assert profile["job_family"] == "data_analysis"
    assert len(profile["skill_dimensions"]) >= 5
    assert {"sql", "python", "data_visualization", "statistics", "ab_testing"} <= keys


def test_data_analyst_resume_extracts_matching_evidence():
    profile = parse_resume_profile(DATA_ANALYST_RESUME)
    evidence = profile["evidence"]

    assert "sql" in evidence
    assert "python" in evidence
    assert "data_visualization" in evidence
    assert "ab_testing" in evidence


def test_backend_terms_do_not_false_match_data_analysis_sql():
    profile = parse_job_profile("后端工程师，要求 SQLAlchemy、FastAPI、PostgreSQL。")

    assert profile.get("job_family") != "data_analysis"
    keys = {item["canonical_key"] for item in profile.get("skill_dimensions", [])}
    assert "sql" not in keys


def test_react_dashboard_does_not_imply_data_visualization_without_analysis_context():
    profile = parse_resume_profile("使用 React 开发后台 dashboard 页面，负责组件拆分和路由。")

    assert "data_visualization" not in profile["evidence"]
```

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_data_analysis_dimension_extraction.py -q
```

Expected: FAIL，当前解析器没有 `skill_dimensions` 和数据分析岗位族。

- [ ] **Step 3：扩展技能目录**

在 `backend/app/services/job_service.py` 中新增数据分析技能目录：

```python
SKILL_CATALOG = {
    "sql": {
        "name": "SQL",
        "category": "data_analysis",
        "aliases": ["SQL", "数据库查询", "多表关联", "窗口函数", "数据提取"],
    },
    "python": {
        "name": "Python",
        "category": "programming",
        "aliases": ["Python", "pandas", "NumPy", "数据处理"],
    },
    "data_visualization": {
        "name": "数据可视化",
        "category": "data_analysis",
        "aliases": ["数据可视化", "Tableau", "Power BI", "ECharts", "看板", "图表"],
    },
    "statistics": {
        "name": "统计方法",
        "category": "statistics",
        "aliases": ["统计", "显著性", "置信区间", "假设检验", "统计检验"],
    },
    "ab_testing": {
        "name": "A/B 测试",
        "category": "statistics",
        "aliases": ["A/B 测试", "AB 测试", "实验设计", "对照实验"],
    },
    "machine_learning": {
        "name": "机器学习",
        "category": "machine_learning",
        "aliases": ["机器学习", "特征分析", "模型", "算法"],
    },
    "business_analysis": {
        "name": "业务分析",
        "category": "business",
        "aliases": ["业务分析", "转化率", "留存", "增长", "指标体系"],
    },
}
```

- [ ] **Step 4：实现岗位族和维度解析 fallback**

`parse_job_profile()` 输出兼容旧字段和新字段：

```python
def parse_job_profile(raw_text: str) -> dict:
    dimensions = []
    evidence = {}
    for key, item in SKILL_CATALOG.items():
        matched = []
        for alias in item["aliases"]:
            matched.extend(_find_evidence(raw_text, alias))
        matched = list(dict.fromkeys(matched))
        if matched:
            evidence[key] = matched
            dimensions.append({
                "name": item["name"],
                "canonical_key": key,
                "category": item["category"],
                "weight": 1.0,
                "required_level": "project_practice",
                "jd_evidence": matched,
                "aliases": item["aliases"],
            })

    normalized_weight = 1 / len(dimensions) if dimensions else 0
    for dimension in dimensions:
        dimension["weight"] = normalized_weight

    legacy_skills = [dimension["name"] for dimension in dimensions]
    job_family = "data_analysis" if any(
        key in evidence for key in ["sql", "data_visualization", "statistics", "ab_testing"]
    ) else "software_engineering"

    return {
        "schema_version": "job-profile-v2",
        "job_family": job_family,
        "skill_dimensions": dimensions,
        "required_skills": legacy_skills,
        "preferred_skills": [],
        "domain_keywords": [job_family],
        "basic_requirements": [],
        "evidence": evidence,
    }
```

- [ ] **Step 5：实现简历证据解析 fallback**

`parse_resume_profile()` 使用同一目录，并保留旧字段：

```python
def parse_resume_profile(raw_text: str) -> dict:
    evidence = {}
    skills = []
    for key, item in SKILL_CATALOG.items():
        matched = []
        for alias in item["aliases"]:
            matched.extend(_find_evidence(raw_text, alias))
        matched = list(dict.fromkeys(matched))
        if matched:
            evidence[key] = matched
            skills.append(item["name"])

    projects = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?。！？\n])\s*", raw_text)
        if any(term in sentence for term in ["项目", "构建", "完成", "支持", "分析"])
    ]

    return {
        "schema_version": "resume-profile-v2",
        "skills": skills,
        "projects": projects,
        "domain_keywords": [],
        "evidence": evidence,
    }
```

- [ ] **Step 6：运行维度测试确认通过**

Run:

```powershell
cd backend
pytest tests/test_data_analysis_dimension_extraction.py -q
```

Expected: PASS。

- [ ] **Step 7：运行既有岗位和简历 API 测试**

Run:

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

Expected: PASS。

- [ ] **Step 8：提交 Task 2**

Run:

```powershell
git add backend/app/services/job_service.py backend/app/services/resume_service.py backend/tests/test_data_analysis_dimension_extraction.py docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "fix: extract data analyst dimensions from jd and resume"
```

## Task 3：让评分消费结构化维度但保持确定性

**Files:**

- Modify: `backend/app/scoring/rules.py`
- Test: `backend/tests/test_scoring.py`
- Test: `backend/tests/test_analysis_flow.py`

- [ ] **Step 1：写失败的多维评分测试**

在 `backend/tests/test_scoring.py` 中新增：

```python
from app.scoring.rules import score_match


def test_score_match_uses_skill_dimensions_and_resume_evidence_keys():
    jd_profile = {
        "skill_dimensions": [
            {
                "name": "SQL",
                "canonical_key": "sql",
                "category": "data_analysis",
                "weight": 0.5,
                "required_level": "project_practice",
                "jd_evidence": ["熟练 SQL"],
                "aliases": ["SQL"],
            },
            {
                "name": "数据可视化",
                "canonical_key": "data_visualization",
                "category": "data_analysis",
                "weight": 0.5,
                "required_level": "project_practice",
                "jd_evidence": ["使用 ECharts 做可视化"],
                "aliases": ["ECharts"],
            },
        ],
        "evidence": {},
    }
    resume_profile = {
        "skills": ["SQL"],
        "projects": ["使用 SQL 支持销售看板"],
        "evidence": {"sql": ["使用 SQL 支持销售看板"]},
    }

    result = score_match(jd_profile, resume_profile)

    assert len(result["score_items"]) == 2
    assert {item["skill_key"] for item in result["score_items"]} == {"sql", "data_visualization"}
    assert result["score_items"][0]["score"] > result["score_items"][1]["score"]
    assert 0 <= result["final_score"] <= 100
```

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_scoring.py::test_score_match_uses_skill_dimensions_and_resume_evidence_keys -q
```

Expected: FAIL，当前 `score_items` 没有 `skill_key`，且评分只消费 `required_skills`。

- [ ] **Step 3：修改 `score_match()`**

实现规则：

- 优先读取 `jd_profile["skill_dimensions"]`。
- 没有新字段时回退旧 `required_skills`。
- 每个评分项写入 `skill_key`、`skill`、`category`、`weight`。
- 最终分数仍由确定性权重计算，LLM 不参与。

核心逻辑：

```python
def _iter_dimensions(jd_profile: dict) -> list[dict]:
    dimensions = jd_profile.get("skill_dimensions") or []
    if dimensions:
        return dimensions
    return [
        {
            "name": skill,
            "canonical_key": skill,
            "category": "general",
            "weight": 1,
            "required_level": "project_practice",
            "jd_evidence": (jd_profile.get("evidence") or {}).get(skill, []),
            "aliases": [skill],
        }
        for skill in jd_profile.get("required_skills") or []
    ]
```

- [ ] **Step 4：运行评分测试确认通过**

Run:

```powershell
cd backend
pytest tests/test_scoring.py tests/test_scoring_with_rag.py -q
```

Expected: PASS。

- [ ] **Step 5：运行分析流测试**

Run:

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

Expected: PASS；如果报告 schema 因新增字段失败，更新 schema 映射但不得删除旧字段。

- [ ] **Step 6：提交 Task 3**

Run:

```powershell
git add backend/app/scoring/rules.py backend/tests/test_scoring.py backend/tests/test_analysis_flow.py docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "fix: score structured skill dimensions deterministically"
```

## Task 4：RAG 增加岗位族过滤、阈值和数据分析种子库

**Files:**

- Create: `backend/seeds/data_analysis.json`
- Modify: `backend/app/rag/loader.py`
- Modify: `backend/app/rag/retrieval.py`
- Modify: `backend/app/agents/nodes.py`
- Modify: `backend/app/services/analysis_service.py`
- Test: `backend/tests/test_rag_relevance_filtering.py`
- Test: `backend/tests/test_rag_retrieval.py`
- Test: `backend/tests/test_analysis_flow.py`

- [ ] **Step 1：写失败的 RAG 相关性测试**

创建 `backend/tests/test_rag_relevance_filtering.py`：

```python
from app.rag.retrieval import filter_relevant_documents


def test_filter_relevant_documents_rejects_wrong_job_family():
    docs = [
        {
            "doc_id": 1,
            "title": "FastAPI 技能定义",
            "doc_type": "backend",
            "score": 0.91,
            "metadata": {"job_family": "software_engineering"},
        },
        {
            "doc_id": 2,
            "title": "SQL 数据分析能力标准",
            "doc_type": "data_analysis",
            "score": 0.86,
            "metadata": {"job_family": "data_analysis"},
        },
    ]

    filtered = filter_relevant_documents(
        docs,
        job_family="data_analysis",
        allowed_doc_types=["data_analysis", "statistics"],
        min_score=0.75,
    )

    assert [doc["doc_id"] for doc in filtered] == [2]


def test_filter_relevant_documents_rejects_low_score():
    docs = [
        {
            "doc_id": 3,
            "title": "SQL 数据分析能力标准",
            "doc_type": "data_analysis",
            "score": 0.42,
            "metadata": {"job_family": "data_analysis"},
        }
    ]

    assert filter_relevant_documents(docs, "data_analysis", ["data_analysis"], 0.75) == []
```

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_rag_relevance_filtering.py -q
```

Expected: FAIL，`filter_relevant_documents` 不存在。

- [ ] **Step 3：实现过滤函数**

在 `backend/app/rag/retrieval.py` 中新增：

```python
def filter_relevant_documents(
    documents: list[dict[str, Any]],
    job_family: str,
    allowed_doc_types: list[str],
    min_score: float = 0.72,
) -> list[dict[str, Any]]:
    filtered = []
    for doc in documents:
        metadata = doc.get("metadata") or {}
        doc_family = metadata.get("job_family")
        doc_type = doc.get("doc_type")
        score = float(doc.get("score") or 0)
        family_matches = not doc_family or doc_family == job_family
        type_matches = not allowed_doc_types or doc_type in allowed_doc_types
        if family_matches and type_matches and score >= min_score:
            filtered.append(doc)
    return filtered
```

- [ ] **Step 4：新增数据分析种子文档**

创建 `backend/seeds/data_analysis.json`，至少包含 8 篇文档：

```json
[
  {
    "doc_type": "data_analysis",
    "title": "SQL 数据分析能力标准",
    "content": "数据分析师的 SQL 能力包括多表关联、窗口函数、聚合分析、数据质量检查和查询性能意识。项目实践级别要求能把业务问题转化为可复现查询，并解释指标口径。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "sql"}
  },
  {
    "doc_type": "data_analysis",
    "title": "Python 数据处理能力标准",
    "content": "Python 数据分析能力包括 pandas 数据清洗、缺失值处理、分组聚合、自动化分析脚本和可复现实验记录。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "python"}
  },
  {
    "doc_type": "statistics",
    "title": "A/B 测试与统计显著性",
    "content": "A/B 测试要求明确实验假设、指标口径、样本量、分流方式和显著性检验。简历证据应描述实验目标、评估指标和结论边界。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "ab_testing"}
  },
  {
    "doc_type": "data_analysis",
    "title": "数据可视化与看板能力标准",
    "content": "数据可视化能力包括选择合适图表、设计指标层级、避免误导性视觉编码，并能用看板支持业务决策。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "data_visualization"}
  },
  {
    "doc_type": "statistics",
    "title": "统计方法基础",
    "content": "统计方法基础包括描述性统计、假设检验、置信区间、相关与回归。应届生可通过实验分析或课程项目证明理解。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "statistics"}
  },
  {
    "doc_type": "data_analysis",
    "title": "业务分析指标体系",
    "content": "业务分析要求理解转化率、留存率、漏斗、分群和指标口径，能把业务问题拆成可验证的数据问题。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "business_analysis"}
  },
  {
    "doc_type": "machine_learning",
    "title": "机器学习协作基础",
    "content": "数据分析师不一定训练复杂模型，但需要理解特征、标签、评估指标和模型结果解释，能与算法团队协作。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "machine_learning"}
  },
  {
    "doc_type": "interview",
    "title": "数据分析师面试题型",
    "content": "SQL 题常考多表关联、窗口函数和慢查询定位；统计题常考 A/B 测试设计；可视化题常考图表选择和指标解释。",
    "metadata": {"schema_version": "1", "job_family": "data_analysis", "skill_key": "interview"}
  }
]
```

- [ ] **Step 5：更新 seed loader**

修改 `load_all_seeds()`：

```python
for seed_name in ["backend_dev", "frontend_fullstack", "llm_app_dev", "data_analysis"]:
    total += load_seed_data(db, seed_name)
```

- [ ] **Step 6：在 `rag_retriever` 节点应用过滤**

规则：

- `job_family=data_analysis` 时允许 `data_analysis`、`statistics`、`machine_learning`、`interview`。
- 过滤后为空则写入 `available=False` 和 `reason="知识库证据不足"`。
- 不把低相关文档塞进报告。
- `rag_query_planner_agent` 只产出 query plan；真实 DB 检索保留在 `analysis_service`，因为当前 `run_workflow(initial_state)` 没有 DB session 注入。
- `analysis_service` 必须在 `jd_parser` 产出 `skill_dimensions` 之后执行或补充 RAG 检索，禁止继续只基于旧 `required_skills` 预检索。

- [ ] **Step 7：补充分析服务级 RAG 集成测试**

在 `backend/tests/test_analysis_flow.py` 中新增：

```python
def test_data_analysis_analysis_flow_uses_relevant_rag_only(client):
    job_resp = client.post("/api/jobs", json={
        "title": "数据分析师",
        "raw_text": "需要 SQL、Python、A/B 测试和数据可视化。",
    })
    resume_resp = client.post("/api/resumes", json={
        "candidate_name": "候选人",
        "version_label": "v1",
        "raw_text": "使用 SQL、Python 和 ECharts 完成数据分析。",
    })

    task_resp = client.post("/api/analysis", json={
        "job_id": job_resp.json()["id"],
        "resume_id": resume_resp.json()["id"],
    })
    report_resp = client.get(f"/api/reports/{task_resp.json()['id']}")

    assert report_resp.status_code == 200
    report_text = str(report_resp.json())
    assert "FastAPI" not in report_text
    assert "后端开发岗位画像" not in report_text
```

- [ ] **Step 8：运行 RAG 测试**

Run:

```powershell
cd backend
pytest tests/test_rag_relevance_filtering.py tests/test_rag_retrieval.py tests/test_rag_agent_node.py tests/test_analysis_flow.py::test_data_analysis_analysis_flow_uses_relevant_rag_only -q
```

Expected: PASS。

- [ ] **Step 9：提交 Task 4**

Run:

```powershell
git add backend/app/rag/retrieval.py backend/app/rag/loader.py backend/app/agents/nodes.py backend/app/services/analysis_service.py backend/seeds/data_analysis.json backend/tests/test_rag_relevance_filtering.py backend/tests/test_rag_retrieval.py backend/tests/test_rag_agent_node.py backend/tests/test_analysis_flow.py docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "fix: filter rag evidence by job family relevance"
```

## Task 5：拆分单次 LLM 增强为独立生成 Agent

**Files:**

- Create: `backend/app/llm/agent_prompts.py`
- Modify: `backend/app/agents/nodes.py`
- Modify: `backend/app/llm/service.py`
- Test: `backend/tests/test_multi_agent_llm_flow.py`
- Test: `backend/tests/test_interview_service.py`
- Test: `backend/tests/test_learning_api.py`

- [ ] **Step 1：写失败的多 Agent 调用测试**

在 `backend/tests/test_multi_agent_llm_flow.py` 追加：

```python
from app.agents.graph import run_workflow


def test_workflow_records_independent_agent_roles_when_llm_enabled(monkeypatch):
    calls = []

    def fake_run_structured_agent(**kwargs):
        calls.append(kwargs["agent_role"])
        fallback = kwargs.get("fallback")
        if fallback:
            return fallback(), {
                "agent_role": kwargs["agent_role"],
                "execution_mode": "llm",
                "model_name": "fake-model",
                "fallback_used": False,
                "schema_valid": True,
                "retry_count": 0,
            }
        raise AssertionError("fallback required in test")

    monkeypatch.setattr("app.agents.nodes.run_structured_agent", fake_run_structured_agent)

    _, trace = run_workflow({
        "raw_jd": "需要 SQL、Python、A/B 测试和数据可视化。",
        "raw_resume": "使用 SQL 和 Python 完成数据分析项目。",
        "llm_enabled": True,
    })

    assert "jd_parser_agent" in calls
    assert "resume_parser_agent" in calls
    assert "rag_query_planner_agent" in calls
    assert "resume_optimizer_agent" in calls
    assert "gap_analyzer_agent" in calls
    assert "interview_coach_agent" in calls
    assert "learning_planner_agent" in calls
    assert "next_best_action_agent" in calls
    assert any(item.get("execution_meta", {}).get("execution_mode") == "llm" for item in trace)
```

- [ ] **Step 2：运行测试确认失败**

Run:

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py::test_workflow_records_independent_agent_roles_when_llm_enabled -q
```

Expected: FAIL，当前 workflow 只有一次增强调用，trace 没有 `execution_meta`。

- [ ] **Step 3：新增独立 prompt builder**

在 `backend/app/llm/agent_prompts.py` 中创建函数：

- `build_jd_parse_prompt(raw_jd: str) -> str`
- `build_resume_parse_prompt(raw_resume: str) -> str`
- `build_rag_query_plan_prompt(jd_profile: dict) -> str`
- `build_gap_analysis_prompt(match_result: dict) -> str`
- `build_resume_suggestion_prompt(gaps: list, strengths: list) -> str`
- `build_interview_prompt(score_items: list, gaps: list) -> str`
- `build_learning_plan_prompt(gaps: list, knowledge: dict) -> str`
- `build_next_best_action_prompt(gaps: list, score: int) -> str`

所有 prompt 都必须包含中文约束：

```text
只输出严格 JSON，不要 Markdown。
不得编造简历中不存在的经历。
不得输出完整 JD 或完整简历原文。
如果证据不足，明确标记证据不足。
```

安全边界必须写进 prompt builder 注释和测试：

- 只有 `jd_parser_agent` 和 `resume_parser_agent` 可以接收原始 JD/简历，且仅用于受控解析。
- 其他 Agent 只能接收结构化证据、脱敏摘要或评分项，不接收完整原文。
- repair prompt 不得无长度限制地回传模型首次输出；实现时只保留 JSON 候选片段，或截断到安全长度。
- 任何 prompt、request body、response body、API key 都不得写日志。

- [ ] **Step 4：修改节点调用独立 Agent**

在 `backend/app/agents/nodes.py` 中：

- `jd_parser` 调用 `jd_parser_agent`，fallback 为 `parse_job_profile()`。
- `resume_parser` 调用 `resume_parser_agent`，fallback 为 `parse_resume_profile()`。
- 新增或改造 `rag_query_planner`，fallback 根据技能维度生成 query。
- `gap_analyzer` 调用 `gap_analyzer_agent`，fallback 为当前规则缺口分析。
- `resume_optimizer` 只生成简历建议。
- `interview_coach` 独立生成题目。
- `learning_planner` 独立生成学习路径。
- `next_best_action` 独立生成下一步建议。
- `integrity_critic_agent` 在 Phase 2G 只允许作为辅助解释风险的可选节点，不能替代现有硬规则 `Integrity Guard`，不能决定建议是否放行。

每个节点输出同时带内部 `_execution_meta`，供 `graph.py` 写 trace；写入 state 前删除内部字段，避免污染报告响应。

- [ ] **Step 5：修改 trace 写入**

在 `backend/app/agents/graph.py` 中把节点返回的 `_execution_meta` 写到 trace：

```python
execution_meta = output.pop("_execution_meta", {
    "agent_role": node_name,
    "execution_mode": "deterministic",
    "model_name": None,
    "fallback_used": False,
    "schema_valid": True,
    "retry_count": 0,
})
trace.append({
    "node_name": node_name,
    "status": "success",
    "execution_meta": execution_meta,
    ...
})
```

- [ ] **Step 6：运行多 Agent 测试**

Run:

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py -q
```

Expected: PASS。

- [ ] **Step 7：运行生成相关测试**

Run:

```powershell
cd backend
pytest tests/test_interview_service.py tests/test_learning_api.py tests/test_llm_agent_flow.py -q
```

Expected: PASS；如果旧测试仍假设一次性 `llm_enhancement`，改为断言独立产物。

- [ ] **Step 8：运行轻量 PII 安全断言**

Run:

```powershell
cd backend
pytest tests/test_multi_agent_llm_flow.py::test_prompt_and_trace_do_not_persist_raw_jd_resume -q
```

Expected: PASS；该测试必须断言 prompt 日志、Agent trace、异常详情不会持久化完整 JD/简历/API key。如果测试尚不存在，先补测试再实现。

- [ ] **Step 9：提交 Task 5**

Run:

```powershell
git add backend/app/llm/agent_prompts.py backend/app/agents/nodes.py backend/app/agents/graph.py backend/app/llm/service.py backend/tests/test_multi_agent_llm_flow.py backend/tests/test_interview_service.py backend/tests/test_learning_api.py backend/tests/test_llm_agent_flow.py docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "feat: split report enhancement into independent agents"
```

## Task 6：前端 Trace 展示真实执行方式

**Files:**

- Modify: `frontend/src/api/agentRuns.ts`
- Modify: `frontend/src/components/report/AgentTraceRow.vue`
- Modify: `frontend/src/components/report/AgentTraceTimeline.vue`
- Modify: `frontend/tests/components/AgentTraceTimeline.test.ts`
- Modify: `frontend/tests/views/ReportView.test.ts`

- [ ] **Step 1：写失败的 Trace 执行方式测试**

在 `frontend/tests/components/AgentTraceTimeline.test.ts` 中新增：

```ts
it('展示 Agent 执行方式、fallback 和 schema 校验状态', () => {
  const wrapper = mount(AgentTraceTimeline, {
    props: {
      nodes: [
        {
          node_name: 'jd_parser',
          status: 'success',
          execution_meta: {
            agent_role: 'jd_parser_agent',
            execution_mode: 'llm',
            model_name: 'fake-model',
            fallback_used: false,
            schema_valid: true,
            retry_count: 0
          },
          input_snapshot: {},
          output_snapshot: {}
        },
        {
          node_name: 'match_scorer',
          status: 'success',
          execution_meta: {
            agent_role: 'match_scorer',
            execution_mode: 'deterministic',
            model_name: null,
            fallback_used: false,
            schema_valid: true,
            retry_count: 0
          },
          input_snapshot: {},
          output_snapshot: {}
        }
      ]
    }
  })

  expect(wrapper.text()).toContain('解析岗位要求')
  expect(wrapper.text()).toContain('LLM')
  expect(wrapper.text()).toContain('fake-model')
  expect(wrapper.text()).toContain('计算匹配分数')
  expect(wrapper.text()).toContain('确定性规则')
})
```

- [ ] **Step 2：运行前端测试确认失败**

Run:

```powershell
cd frontend
npm test -- AgentTraceTimeline
```

Expected: FAIL，当前组件没有展示 `execution_meta`。

- [ ] **Step 3：扩展 API normalize 层**

修改 `frontend/src/api/agentRuns.ts`：

- `BackendAgentRun` 增加 `execution_meta?: AgentExecutionMeta`。
- `AgentNode` 增加 `execution_meta?: AgentExecutionMeta`。
- `normalizeAgentRun()` 把后端 `execution_meta` 原样映射到每个 node。
- summary 优先使用后端脱敏摘要；没有摘要时再使用字段名 fallback。

新增或修改前端测试，必须使用真实后端响应 shape，而不是只手写组件 props：

```ts
const backendPayload = [{
  id: 1,
  task_id: 1,
  node_name: 'jd_parser',
  status: 'success',
  input_snapshot: {},
  output_snapshot: {},
  execution_meta: {
    agent_role: 'jd_parser_agent',
    execution_mode: 'llm',
    model_name: 'fake-model',
    fallback_used: false,
    schema_valid: true,
    retry_count: 0
  }
}]
```

- [ ] **Step 4：实现中文节点名和执行方式映射**

在组件中使用映射：

```ts
const nodeLabels: Record<string, string> = {
  jd_parser: '解析岗位要求',
  resume_parser: '解析简历证据',
  rag_query_planner: '规划知识库检索',
  rag_retriever: '检索知识库',
  match_scorer: '计算匹配分数',
  gap_analyzer: '分析能力缺口',
  resume_optimizer: '生成简历建议',
  integrity_guard: '检查真实性风险',
  interview_coach: '生成面试题',
  learning_planner: '生成学习路径',
  next_best_action: '选择下一步行动'
}

const modeLabels: Record<string, string> = {
  llm: 'LLM',
  rule: '本地规则',
  rag: 'RAG',
  deterministic: '确定性规则'
}
```

- [ ] **Step 5：渲染 fallback 和 schema 状态**

每行展示：

- 执行方式 badge。
- 模型名；为空时显示“本地规则”。
- fallback 使用时显示“已使用 fallback”。
- schema 无效时显示高风险标签。
- 重试次数大于 0 时显示“JSON 修复重试 X 次”。
- 默认展示用户语言的可信摘要；技术字段进入展开详情或 tooltip，避免 Trace 变成工程日志。

- [ ] **Step 6：报告页信息架构收口**

`ReportView` 必须把 Phase 2G 新增信息做分组或折叠：

- 评分维度默认展示摘要和风险状态。
- JD 证据、简历证据、知识库证据默认摘要，点击展开。
- 知识库正文默认只显示 `title` 和短摘要。
- Agent Trace 默认折叠技术字段。

- [ ] **Step 7：确认不渲染原文**

保留现有测试：如果 `raw_jd` 或 `raw_resume` 出现在 props，组件必须不渲染原文。

- [ ] **Step 8：运行前端测试**

Run:

```powershell
cd frontend
npm test -- AgentTraceTimeline
npm test -- ReportView
npm run typecheck
```

Expected: PASS。

- [ ] **Step 9：提交 Task 6**

Run:

```powershell
git add frontend/src/api/agentRuns.ts frontend/src/components/report/AgentTraceRow.vue frontend/src/components/report/AgentTraceTimeline.vue frontend/tests/components/AgentTraceTimeline.test.ts frontend/tests/views/ReportView.test.ts docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2g-agent-credibility.md TODOS.md
git commit -m "feat(frontend): show real agent execution modes in trace"
```

## Task 7：端到端回归与文档同步

**Files:**

- Modify: `docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2g-test-plan.md`
- Modify: `TODOS.md`
- Modify: `C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md`

- [ ] **Step 1：运行后端完整测试**

Run:

```powershell
cd backend
pytest -q
```

Expected: PASS。

- [ ] **Step 2：运行前端完整测试**

Run:

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

Expected: PASS。

- [ ] **Step 3：运行文档检查**

Run:

```powershell
git diff --check
```

Expected: 无 trailing whitespace 或冲突标记。

- [ ] **Step 4：补跑 PII 安全审计**

若当前环境有 `gstack:cso`：

```powershell
gstack cso
```

若仍无 CLI 入口，按本地等价审计记录：

- LLM prompt 不包含完整 JD/简历。
- Agent trace 对外响应不包含完整 JD/简历/prompt。
- localStorage 不保存原文。
- 日志不输出 prompt、API key、原文。

审计结果写入 `docs/superpowers/review-logs/2026-05-04-phase-2g-agent-credibility-security-review.md`。

- [ ] **Step 5：同步外部测试计划副本**

Run:

```powershell
Copy-Item docs\superpowers\test-plans\2026-05-04-careerfit-agent-phase-2g-test-plan.md C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md
```

- [ ] **Step 6：更新 TODO 完成状态**

把 `TODOS.md` 中 Phase 2G 对应后端、前端、验证门 checklist 按实际结果从 `- [ ]` 改为 `- [x]`。如果 Docker 或安全审计无法运行，保留未完成并写明原因。

- [ ] **Step 7：最终提交**

Run:

```powershell
git add backend frontend docs TODOS.md C:\Users\qwer\.gstack\projects\Newproject\phase-2g-test-plan-2026-05-04-careerfit-agent.md
git commit -m "feat: complete multi-agent credibility upgrade"
```

## 自审清单

- [ ] 数据分析师 JD 不再只产出单一 Python 维度。
- [ ] RAG 不再用后端、FastAPI、大模型应用文档顶替数据分析知识。
- [ ] `match_scorer` 没有调用 LLM。
- [ ] 至少 7 个语义 Agent 有独立 `agent_role` 和 trace meta。
- [ ] LLM 关闭时 workflow 仍可完成。
- [ ] Agent Trace 不展示完整 JD、完整简历、完整 prompt。
- [ ] 前端展示中文节点名和执行方式。
- [ ] 测试计划已同步外部副本。

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/autoplan` | Scope & strategy | 1 | issues_open | 4 P0 修订已写回：端到端可信报告验收、gap agent 闭环、Integrity critic 边界、无关 RAG 报告级测试 |
| Codex Review | `codex CLI` | Independent 2nd opinion | 0 | unavailable | 本机 `codex --version` 失败，缺少 `@openai/codex-win32-x64` optional dependency |
| Eng Review | `/autoplan` | Architecture & tests | 1 | issues_open | 7 个工程补丁已写回：AgentRun meta 持久化、RAG service 边界、prompt PII 边界、失败契约、前端 normalize、端到端测试、PII 前移 |
| Design Review | `/autoplan` | UI/UX gaps | 1 | issues_open | Trace 默认可信摘要、报告分组/折叠、移动端 badge 验收已写回 |

- **CROSS-MODEL:** 产品/UX 与工程声部都指出“可信度不是 Trace 字段数量”，需要用户语言摘要 + 显式工程边界。
- **UNRESOLVED:** 0 个需要用户拍板的方向性冲突；所有修订都属于补齐既定 Phase 2G 目标。
- **VERDICT:** CEO + Design + Eng 计划审查已完成，存在已写回的实施前置补丁；按修订后计划执行。
