# CareerFit Agent Test Plan

Date: 2026-05-02

## Affected Pages and Routes

- Workspace
- Target Job Library
- Resume Version Library
- Matching Analysis
- Analysis Report
- Evidence Explanation
- Interview Training
- Learning Path
- Growth Trends
- Agent Trace

## Backend API Coverage

| API | Required Tests |
|---|---|
| `POST /api/jobs` | valid JD, empty JD, malformed JD, parser failure |
| `GET /api/jobs` | empty list, populated list |
| `GET /api/jobs/{id}` | found, not found |
| `POST /api/resumes` | valid text resume, empty resume, low-confidence parse |
| `GET /api/resumes/compare` | added section, removed section, changed section |
| `POST /api/analysis` | valid job + resume, missing job, missing resume |
| `GET /api/analysis/{task_id}` | pending, running, success, failed |
| `GET /api/reports/{task_id}` | complete report, weak evidence report, not found |
| `GET /api/agent-runs/{task_id}` | success nodes, failed node, redacted summaries |
| `PATCH /api/learning/tasks/{id}` | `todo -> doing`, `doing -> done`, invalid transition |
| `GET /api/knowledge/search` | expected hit, no hit, invalid query |

## Core Unit Tests

- Score formula clamps all dimensions to 0-100.
- Integrity risk penalty cannot make final score negative.
- Skill level mapping returns expected numeric values.
- Evidence chain validation rejects score items without JD evidence.
- Evidence chain validation rejects score items without resume evidence.
- Integrity guard blocks unsupported metrics.
- Integrity guard blocks unsupported leadership claims.
- Integrity guard allows safe wording improvements.
- Resume version comparison detects added, removed, and changed bullets.

## LangGraph and Agent Tests

- JD Parser Agent returns schema-valid output.
- Resume Parser Agent returns schema-valid output.
- RAG Retriever Agent returns typed document groups.
- Match Scoring Agent does not call LLM for final numeric score.
- Gap Analysis Agent emits `missing_skill`, `weak_evidence`, and `expression_gap`.
- Integrity Guard Agent runs before Resume Optimizer output is finalized.
- Report Composer Agent includes evidence references for every score item.
- Workflow records `agent_runs` for every node.
- Workflow marks task failed when a node fails after retry.

## RAG Evaluation

Use seed documents for:

- LLM application developer.
- Backend developer.
- Frontend/full-stack developer.

Required checks:

- Query `LangGraph Agent 编排` retrieves LangGraph skill standards.
- Query `pgvector 索引` retrieves vector database standards.
- Query `Vue3 项目经验` retrieves frontend/full-stack standards.
- Query with no matching skill returns an empty or low-confidence result, not a fabricated source.

## LLM Evaluation

Use at least:

- 5 sample JDs.
- 5 sample resumes.
- 5 unsafe resume optimization examples.

Eval criteria:

- Parser extracts required skills with acceptable recall.
- Parser preserves evidence snippets.
- Integrity guard blocks fabricated facts.
- Report composer does not generate unsupported claims.
- Interview questions reference actual resume projects when available.

## Frontend Tests

- Workspace empty state.
- Workspace with latest report and Next Best Action.
- Job creation loading and error states.
- Resume creation loading and error states.
- Analysis timeline running state.
- Analysis timeline failed node state.
- Report success state.
- Report weak evidence state.
- Evidence detail expansion.
- Learning task status update.
- Agent trace redaction.
- Mobile stacked report layout.
- Keyboard navigation through primary actions.

## Docker Smoke Test

Run:

```text
docker compose up --build
```

Verify:

- PostgreSQL starts with pgvector extension enabled.
- Backend health check passes.
- Frontend loads.
- Backend can connect to database.
- Initial migrations run.
- Seed knowledge import succeeds.

## Critical Paths

1. Create target job.
2. Create resume version.
3. Run analysis.
4. View report.
5. Confirm every score item has evidence.
6. View integrity risks.
7. Mark a learning task done.
8. Create next resume version.
9. Re-run analysis.
10. View score trend.
