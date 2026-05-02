# CareerFit Agent Design

Date: 2026-05-02

## Product Positioning

CareerFit Agent is a personal job-search growth workspace for computer science new graduates. It is not a one-shot JD and resume analyzer. The product helps a student maintain target jobs, resume versions, matching reports, interview preparation, learning tasks, and score trends over time.

The core value is an explainable RAG and multi-agent workflow that helps students understand how well a resume matches a target job, what evidence supports the score, which gaps are real capability gaps, which gaps are expression issues, and how to improve honestly without fabricating experience.

## Target User

The target user is a computer science student or new graduate applying for software engineering, backend, frontend, full-stack, AI application, or large language model application development roles.

The system is designed as a single-user product for portfolio and personal use. It persists data locally in PostgreSQL but does not include account login, multi-tenant permissions, HR workflows, teacher workflows, payment, or enterprise collaboration.

## Business Flow

The product supports a long-term job-search loop:

```text
Save target jobs
  -> Upload or maintain resume versions
  -> Run JD-resume matching analysis
  -> Review explainable score and evidence chain
  -> Identify capability gaps
  -> Generate honest resume optimization suggestions
  -> Generate interview questions and learning path
  -> Complete learning tasks
  -> Create a new resume version
  -> Re-run matching analysis
  -> Compare score and gap trends
```

This loop makes the system a persistent workspace rather than a demo that only accepts one JD and one resume.

## Scope

### In Scope

- Target job library with JD parsing.
- Resume version library with structured resume parsing.
- JD-resume matching analysis.
- Explainable score breakdown.
- Evidence chain linking JD requirements, resume evidence, and knowledge-base standards.
- Capability gap analysis.
- Integrity guard to prevent resume fabrication.
- Honest resume optimization suggestions.
- Interview question generation.
- Learning path planning.
- Learning task completion tracking.
- Score and gap trend tracking across resume versions.
- Agent run trace logging.
- RAG knowledge base using PostgreSQL and pgvector.
- Single-user persistent data model.
- Docker Compose deployment.

### Out of Scope

- Login, registration, and user permission management.
- HR candidate screening workflows.
- Teacher or mentor dashboards.
- Multi-tenant SaaS features.
- Payment, notification, and calendar integration.
- Fully automated resume rewriting that overwrites the user's resume.
- Claims that invent companies, projects, metrics, responsibilities, or technologies not supported by resume evidence.

## Core Product Modules

### 1. Target Job Library

The user can create and manage multiple target jobs by pasting or uploading JD text. Each JD is parsed into a structured job profile containing:

- Job title.
- Company name if available.
- Job level if inferable.
- Responsibilities.
- Required skills.
- Preferred skills.
- Technology stack.
- Project experience preferences.
- Education or graduation requirements.
- Interview focus areas.

The parsed profile is stored so later analysis does not need to re-parse unchanged JDs.

### 2. Resume Version Library

The user can maintain multiple resume versions, such as:

- `v1-original`
- `v2-project-expression-improved`
- `v3-rag-project-added`

Each version stores the raw resume text and a structured profile containing:

- Education background.
- Technical skills.
- Project experience.
- Internship experience.
- Competition, paper, certificate, or open-source experience.
- Quantified outcomes.
- Evidence snippets for each extracted capability.

The system supports comparing resume versions to show how expression, evidence, and matching scores changed.

### 3. Matching Analysis

The user selects one target job and one resume version, then starts a matching analysis task. The task runs a LangGraph workflow and persists:

- Task status.
- Agent run traces.
- Parsed input snapshots.
- Score breakdown.
- Evidence items.
- Gap analysis.
- Integrity risks.
- Resume suggestions.
- Interview questions.
- Learning plan.

The MVP may execute the workflow synchronously inside FastAPI, but the API is task-based so it can later move to a background worker without changing the frontend contract.

### 4. Explainable Matching Report

The report shows:

- Overall score.
- Score breakdown by dimension.
- Main strengths.
- Capability gaps.
- Resume expression gaps.
- Evidence quality issues.
- Integrity risks.
- Optimization suggestions.
- Interview questions.
- Learning path.

Each score item must be traceable to:

- A JD requirement.
- A resume evidence snippet.
- A retrieved knowledge-base standard when available.
- A generated explanation constrained by the evidence.

### 5. Capability Gap Analysis

Gaps are classified into three categories:

- `missing_skill`: the target job requires a capability that the resume does not mention.
- `weak_evidence`: the resume mentions a capability, but the project or outcome evidence is weak.
- `expression_gap`: the capability may exist, but the resume wording does not align with the JD.

This distinction prevents the system from treating every issue as a writing problem. Some issues require learning or project work, not resume polishing.

### 6. Integrity Guard

The integrity guard enforces this rule:

> The system may improve expression, but it must not invent facts.

It checks whether generated suggestions introduce unsupported:

- Company names.
- Project names.
- Technical stacks.
- Performance metrics.
- User responsibilities.
- Production deployment claims.
- Leadership claims.
- Time ranges.
- Awards or certifications.

It also detects exaggeration patterns, such as changing "learned", "used", or "participated in" into "led", "designed the architecture", or "optimized performance by 40%" without evidence.

High-risk suggestions are either blocked or rewritten into honest alternatives.

### 7. Resume Optimization

Resume optimization output is structured as suggestions rather than a silently rewritten resume. Each suggestion contains:

- Original text.
- Problem diagnosis.
- Optimized text.
- Related JD requirement.
- Resume evidence used.
- Integrity risk level.
- Reasoning.

This makes the optimization auditable and protects the user from accidental fabrication.

### 8. Interview Training

The system generates interview preparation content based on the target job, resume projects, and gaps:

- Fundamental technical questions.
- Project deep-dive questions.
- Scenario design questions.
- Follow-up questions.
- Answer guidance.
- Interviewer evaluation focus.

Questions should reference the user's actual resume projects where possible.

### 9. Learning Path

The learning planner turns gaps into 7-day, 14-day, and 30-day tasks. Each task includes:

- Target skill.
- Learning objective.
- Recommended resource or resource type.
- Practice task.
- Acceptance criteria.
- Related JD requirement.
- Status: `todo`, `doing`, or `done`.

Completed tasks can be used as context when the user creates a new resume version and re-runs analysis.

### 10. Growth Trends

The system records score snapshots across job and resume combinations. The user can view:

- Score changes for the same target job across resume versions.
- Remaining gaps over time.
- Completed learning tasks.
- Resume optimization history.
- Interview preparation history.

## Multi-Agent Workflow

The workflow is implemented with LangGraph and a shared state object.

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

### Shared State

```text
CareerFitState
  raw_jd
  raw_resume
  jd_profile
  resume_profile
  retrieved_knowledge
  match_result
  gap_analysis
  integrity_report
  resume_optimization
  interview_plan
  learning_plan
  report
  trace_logs
```

### Agent Responsibilities

#### JD Parser Agent

Parses raw JD text into a structured job profile and normalizes skill names, such as mapping "Vue.js", "Vue", and "Vue3" to a consistent skill label.

#### Resume Parser Agent

Parses raw resume text into a structured resume profile and attaches evidence snippets to skills, projects, and achievements.

#### RAG Retriever Agent

Retrieves relevant knowledge documents from pgvector, including skill definitions, job profiles, interview questions, and learning resources.

#### Match Scoring Agent

Computes a rule-based score using JD requirements, resume evidence, and retrieved skill standards. It uses the LLM to generate explanations, not to invent the final score.

#### Gap Analysis Agent

Classifies gaps into missing skills, weak evidence, and expression gaps.

#### Integrity Guard Agent

Audits downstream suggestions for unsupported claims and exaggeration. It annotates risk levels and blocks or rewrites unsafe suggestions.

#### Resume Optimizer Agent

Generates evidence-constrained resume optimization suggestions.

#### Interview Coach Agent

Generates interview questions and answer guidance based on the JD, resume projects, and capability gaps.

#### Learning Planner Agent

Creates a staged learning path with measurable tasks and acceptance criteria.

#### Report Composer Agent

Assembles the final report and ensures each conclusion includes evidence references.

## RAG Knowledge Base

The knowledge base uses PostgreSQL and pgvector. Documents are split by type instead of being placed into one undifferentiated vector store.

### Document Types

```text
skill
  Skill definitions, synonyms, capability levels, project evidence standards.

job_profile
  Typical job profiles for backend, frontend, full-stack, AI application, and LLM application roles.

interview
  Interview questions, follow-up questions, difficulty levels, and evaluation points.

learning
  Learning resources, practice tasks, and acceptance criteria.
```

### Knowledge Document Model

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

The `metadata` field stores skill names, difficulty, related job family, source type, and tags.

## Explainable Scoring

The final score is computed using rules, retrieved standards, and evidence. The LLM explains the result but does not directly decide the number.

```text
final_score =
  skill_score * 0.35 +
  project_score * 0.25 +
  domain_score * 0.15 +
  basic_requirement_score * 0.10 +
  expression_score * 0.10 -
  integrity_risk_penalty * 0.05
```

### Capability Level Mapping

```text
not_mentioned     0.00
mentioned         0.30
basic_usage       0.50
project_practice  0.75
deep_experience   1.00
```

Each skill score is calculated from the required skill weight and the matched resume capability level.

### Score Item Structure

```json
{
  "skill": "LangGraph",
  "required_level": "project_practice",
  "resume_level": "project_practice",
  "score": 7,
  "jd_evidence": "熟悉 LangChain / LangGraph Agent 编排",
  "resume_evidence": "使用 LangGraph 编排 JD 解析、简历解析、评分等节点",
  "knowledge_evidence": "project_practice requires state design, node IO contracts, and error handling",
  "reason": "The resume shows project practice, but does not yet show checkpointing, retry handling, or human review nodes."
}
```

## Backend Architecture

### Technology

- FastAPI.
- Pydantic.
- SQLAlchemy.
- PostgreSQL.
- pgvector.
- LangGraph.
- Docker Compose.

### Suggested Structure

```text
backend/
  app/
    main.py
    api/
      routes/
        jobs.py
        resumes.py
        analysis.py
        reports.py
        learning.py
        interview.py
        knowledge.py
    core/
      config.py
      logging.py
    db/
      session.py
      models.py
      migrations/
    schemas/
      jobs.py
      resumes.py
      analysis.py
      reports.py
    services/
      job_service.py
      resume_service.py
      analysis_service.py
      knowledge_service.py
    agents/
      graph.py
      state.py
      nodes/
        jd_parser.py
        resume_parser.py
        retriever.py
        scorer.py
        gap_analyzer.py
        integrity_guard.py
        resume_optimizer.py
        interview_coach.py
        learning_planner.py
        report_composer.py
    rag/
      embeddings.py
      retriever.py
      chunker.py
      loaders.py
    scoring/
      rules.py
      rubric.py
      evidence.py
```

## Database Tables

### job_descriptions

Stores target jobs and parsed JD profiles.

```text
id
title
company
raw_text
parsed_profile JSONB
created_at
updated_at
```

### resume_versions

Stores raw resume text and parsed profiles.

```text
id
name
raw_text
parsed_profile JSONB
created_at
updated_at
```

### analysis_tasks

Stores task status for each JD-resume analysis.

```text
id
job_id
resume_version_id
status
error_message
created_at
updated_at
```

### analysis_reports

Stores final reports.

```text
id
task_id
final_score
score_breakdown JSONB
strengths JSONB
gaps JSONB
integrity_risks JSONB
resume_suggestions JSONB
interview_questions JSONB
learning_plan JSONB
created_at
```

### agent_runs

Stores workflow observability data.

```text
id
task_id
node_name
input_snapshot JSONB
output_snapshot JSONB
latency_ms
token_usage JSONB
status
error_message
created_at
```

### evidence_items

Stores evidence used in scoring and explanation.

```text
id
report_id
evidence_type
source_ref
content
related_skill
created_at
```

### learning_tasks

Stores generated learning tasks and completion state.

```text
id
report_id
skill
objective
resource
practice_task
acceptance_criteria
related_job_requirement
status
created_at
updated_at
```

### interview_sessions

Stores generated interview training sessions.

```text
id
report_id
questions JSONB
created_at
```

### score_snapshots

Stores trend data.

```text
id
job_id
resume_version_id
report_id
final_score
score_breakdown JSONB
created_at
```

## API Design

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

## Frontend Design

### Technology

- Vue3.
- TypeScript.
- Vite.
- REST API client.

### Pages

```text
Workspace
Target Job Library
Resume Version Library
Matching Analysis
Analysis Report
Evidence Explanation
Interview Training
Learning Path
Growth Trends
Agent Trace
```

### UX Principles

- The first screen is the personal job-search workspace, not a marketing landing page.
- Reports prioritize clarity, evidence, and next actions.
- Score explanations are expandable by dimension and skill.
- Resume optimization is shown as auditable suggestions.
- Integrity risks are visible and cannot be hidden behind polished wording.
- Agent traces are available for technical demonstration.

## Docker Deployment

Docker Compose includes:

```text
frontend
backend
postgres-pgvector
```

Optional later services:

```text
redis
worker
```

The MVP should run with one command:

```text
docker compose up --build
```

## Portfolio Positioning

Suggested resume description:

> Designed and implemented CareerFit Agent, a personal AI job-search growth workspace for computer science new graduates. Built a RAG and LangGraph multi-agent workflow with FastAPI, PostgreSQL, pgvector, Vue3, and Docker, supporting target job management, resume versioning, explainable JD-resume matching, capability gap analysis, integrity-guarded resume optimization, interview question generation, learning path planning, and score trend tracking.

Suggested technical highlight:

> Decomposed JD parsing, resume parsing, RAG retrieval, matching scoring, gap analysis, integrity review, resume optimization, interview coaching, and learning planning into observable LangGraph nodes. Persisted node inputs, outputs, latency, token usage, evidence chains, and score breakdowns to PostgreSQL, enabling explainable and traceable AI workflow execution.

## Success Criteria

- A user can save multiple target jobs.
- A user can save multiple resume versions.
- A user can run analysis between any job and resume version.
- The report includes final score, score breakdown, evidence, gaps, integrity risks, resume suggestions, interview questions, and learning tasks.
- Every score explanation references JD evidence and resume evidence.
- Resume optimization suggestions do not invent unsupported facts.
- The user can mark learning tasks as done.
- The user can compare score changes across resume versions.
- Agent run traces are persisted and viewable.
- The whole system can run locally through Docker Compose.

## Risks and Mitigations

### Risk: The project becomes a simple prompt wrapper.

Mitigation: Persist jobs, resume versions, reports, learning tasks, score snapshots, and agent traces. Use rule-based scoring and evidence chains instead of direct LLM scoring.

### Risk: The system accidentally encourages resume fabrication.

Mitigation: Add an integrity guard before final resume suggestions. Require each suggestion to reference existing resume evidence. Block unsupported metrics and exaggerated responsibility claims.

### Risk: RAG becomes cosmetic.

Mitigation: Use retrieved documents in scoring standards, interview generation, and learning tasks. Store knowledge evidence in score items.

### Risk: Scope expands into a full HR SaaS.

Mitigation: Keep the system single-user and personal. Exclude login, multi-role dashboards, HR workflows, and enterprise collaboration.

### Risk: Synchronous analysis blocks API requests for too long.

Mitigation: Keep the task-based API shape from the start. The MVP can run synchronously, and a later version can move execution to a worker.

---

## Autoplan Review

Date: 2026-05-02

Branch: `main`

Plan file: `docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`

External review status:

- Codex CLI voice: unavailable. The Windows read-only runner failed before file access with `CreateProcessAsUserW failed: 5`.
- Claude subagent voice: unavailable in this session due tool policy limiting subagent creation unless explicitly requested.

The review below is the local autoplan review across product, design, and engineering dimensions.

### Phase 1: CEO / Product Review

#### Premise Challenge

The plan's strongest premise is correct: a persistent personal workspace is much better than a one-shot JD-resume analyzer. The danger is that the product still reads like many AI outputs grouped under one shell. The product becomes real only if the growth loop has friction, memory, and before/after proof.

The current spec has the right objects: target jobs, resume versions, reports, learning tasks, score snapshots. The missing product sharpness is the "daily use" path. A student needs to know what to do today, not just see a beautiful analysis report.

Auto-decision: add a `Next Best Action` concept to the workspace. It should pick one high-impact task from the latest report, such as "rewrite project bullet with existing evidence", "finish pgvector indexing practice", or "prepare 5 LangGraph follow-up answers".

#### What Already Exists

This is a new repository with only this design document. No application code, database schema, UI components, tests, or Docker files exist yet.

Existing assets:

```text
docs/superpowers/specs/2026-05-02-careerfit-agent-design.md
```

#### NOT in Scope

The following remain intentionally out of scope:

- Login and multi-user accounts. This would turn the project into auth work.
- HR ranking workflows. The user explicitly rejected a dual-end or HR product.
- Teacher or mentor management. Same reason.
- Payment, notifications, calendar integrations, and enterprise collaboration.
- Automatic resume fabrication or full resume overwrite.
- Production-scale job board crawling.

Deferred but worth tracking:

- Optional import from local markdown resume files.
- Optional export of an optimized resume draft.
- Optional background worker after the MVP task contract is stable.

#### Implementation Alternatives

Recommended path:

1. Build the single-user persistent workspace first.
2. Seed a small but high-quality knowledge base for 3 job families: LLM application developer, backend developer, frontend/full-stack developer.
3. Implement deterministic scoring before making the UI fancy.
4. Build the report, evidence chain, and agent trace views.
5. Add learning tasks and trend charts after the first end-to-end report works.

Rejected alternatives:

- Build all pages first with mocked data. This creates a pretty shell with no trust.
- Build LangGraph first without data persistence. This becomes a prompt demo.
- Build HR or mentor workflows. This violates the chosen product shape.

#### Error & Rescue Registry

| Error | User Experience | Rescue Path | Owner |
|---|---|---|---|
| JD parse fails | User cannot create a useful target job | Save raw JD, show editable fallback fields, allow re-parse | Backend + UI |
| Resume parse fails | User cannot analyze their resume | Save raw text, ask user to confirm extracted sections manually | Backend + UI |
| LLM returns invalid JSON | Analysis task fails | Validate with Pydantic, retry once with repair prompt, then mark failed with node trace | Agent layer |
| RAG returns no useful documents | Score explanation feels made up | Continue with rule scoring and mark knowledge evidence as missing | RAG + scoring |
| Integrity guard blocks too much | User gets no useful optimization | Return safer expression suggestions and explain what evidence is missing | Integrity agent |
| Long analysis time | User thinks app is frozen | Task timeline, node status, retry button | API + UI |

#### Failure Modes Registry

| Failure Mode | Severity | Mitigation |
|---|---:|---|
| The score looks scientific but is arbitrary | High | Keep scoring deterministic, expose rubric, store score items with evidence |
| Resume optimization fabricates achievements | Critical | Integrity guard must run before final report and block unsupported claims |
| Knowledge base is too thin | High | Seed curated documents before evaluating RAG quality |
| User does not know what to do after report | High | Add Next Best Action and convert gaps into tasks |
| Agent trace leaks full sensitive resume text | Medium | Store redacted summaries for UI trace, keep raw snapshots server-side only |
| Sync workflow times out | Medium | Task API shape now, worker later |

#### Dream State Delta

The 12-month ideal is a personal career operating system: it observes applications, interview outcomes, learning progress, project work, and resume changes, then gives the user weekly actions that improve their odds for specific roles.

This plan stops earlier, intentionally. It builds the core data loop and explainable analysis engine. That is enough for a strong portfolio project if the MVP proves score changes across resume versions.

#### CEO Completion Summary

| Area | Rating | Decision |
|---|---:|---|
| User value | 8/10 | Keep the personal growth loop |
| Differentiation | 7/10 | Strengthen with evidence chain, integrity guard, and score trends |
| Scope control | 8/10 | Keep single-user, no HR SaaS |
| Portfolio strength | 9/10 | Excellent if implemented with traces, tests, and real seed data |
| Main risk | 6/10 | Too many generated artifacts, not enough "what should I do today" |

Phase 1 result: passed with one required product addition, `Next Best Action`.

### Phase 2: Design Review

UI scope detected. The plan includes Vue3 pages and user-facing workflows.

#### Design Scope Rating

Current design completeness: 6/10.

The page list is solid, but it is still too generic. The spec names pages but does not define first-run onboarding, loading states, empty states, failure states, report scan order, or accessibility requirements.

#### Pass 1: Information Architecture

Finding: the workspace needs to lead with "today's next action", not just navigation to libraries and reports.

Fix: the first screen should show:

```text
Current target job
Current primary resume version
Latest score
Top 3 gaps
Next Best Action
Recent score trend
```

#### Pass 2: Interaction State Coverage

Missing states:

- No target jobs.
- No resume versions.
- Job parsed but needs user confirmation.
- Resume parsed but low confidence.
- Analysis running.
- Analysis failed at a specific agent node.
- Report generated with weak RAG evidence.
- Learning tasks all completed.

Fix: every main page must define empty, loading, error, success, and partial-data states before implementation.

#### Pass 3: User Journey

The emotional arc should be:

```text
I know where I stand
  -> I know why
  -> I know what I can honestly improve
  -> I know what to learn next
  -> I can see progress after updating my resume
```

The current spec covers the mechanics, but the UI must make the final step obvious. Add a prominent "Create next resume version" action after optimization and learning tasks.

#### Pass 4: AI Slop Risk

Risk: the report could become a wall of generated text.

Fix: report content should use structured cards and tables:

- Score cards for dimensions.
- Evidence rows for each skill.
- Gap rows with category, severity, and action.
- Suggestion rows with original text, improved text, evidence, and risk.

#### Pass 5: Design System Alignment

No existing `DESIGN.md` or component system exists.

Auto-decision: create a small internal design system during implementation:

- Buttons.
- Inputs.
- Text areas.
- File upload.
- Status badges.
- Score cards.
- Evidence table.
- Agent timeline.
- Drawer.

#### Pass 6: Responsive & Accessibility

Add minimum requirements:

- Keyboard-accessible navigation and buttons.
- Visible focus states.
- Color is not the only signal for risk.
- Report tables remain readable on mobile via stacked rows.
- Long JD and resume text areas have stable heights.
- Agent timeline has text labels, not only icons.

#### Pass 7: Unresolved Design Decisions

No taste decision needs user input now. The product should use a practical workbench UI, not a marketing or dashboard-heavy layout.

#### Design Completion Summary

| Dimension | Rating | Decision |
|---|---:|---|
| Information architecture | 7/10 | Add Next Best Action to workspace |
| State coverage | 5/10 | Must specify empty, loading, partial, error states |
| Journey clarity | 7/10 | Add Create Next Resume Version action |
| AI output readability | 6/10 | Use structured report components |
| Accessibility | 5/10 | Add explicit baseline requirements |

Phase 2 result: passed with required UI state and report structure additions.

### Phase 3: Engineering Review

#### Scope Challenge

The architecture is directionally sound, but several pieces that look simple are hard:

- LLM structured extraction.
- Resume and JD schema versioning.
- Deterministic scoring.
- Evidence traceability.
- pgvector seed data quality.
- Agent retry and failure isolation.

Auto-decision: implementation must start with schema contracts and deterministic scoring tests before building all frontend pages.

#### What Already Exists

No code exists yet. The implementation will start from scratch using the documented stack.

#### Architecture Diagram

```text
Vue3 App
  |
  | REST
  v
FastAPI API
  |
  | creates analysis task
  v
Analysis Service
  |
  | invokes
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

#### Engineering Findings

| Finding | Severity | Fix |
|---|---:|---|
| Parsed profiles lack schema version fields | High | Add `schema_version` to parsed JD, parsed resume, report, and score breakdown |
| Score formula has no clamping or calibration rules | High | Clamp all dimensions to 0-100 and store raw factors |
| LLM output validation not explicit enough | High | Define Pydantic output schemas for every agent node |
| Agent snapshots may store too much raw personal data | Medium | Store full data internally, expose redacted summaries in UI |
| Knowledge import API lacks source quality controls | Medium | Seed from checked-in fixture files first, then allow import |
| File upload parsing is underspecified | Medium | MVP should support text first, then PDF/DOCX if dependencies are stable |
| Task API supports polling but not retry semantics | Medium | Add retry endpoint or retry action for failed node/task |

#### Code Quality Review

No code exists, so there are no concrete code smells yet. The biggest future code quality risk is mixing LLM prompts, parsing, scoring, DB writes, and HTTP handlers in the same files.

Auto-decision: keep these boundaries strict:

- API routes only handle request and response.
- Services coordinate use cases.
- Agents own prompt and node logic.
- Scoring owns deterministic math.
- RAG owns chunking, embeddings, and retrieval.
- Repositories or DB layer own persistence.

#### Test Review

Test diagram:

| Flow / Codepath | Test Type | Required Coverage |
|---|---|---|
| Create target job from text | API + service test | Valid JD, empty JD, parse failure |
| Create resume version from text | API + service test | Valid resume, empty resume, low-confidence parse |
| Run analysis task | Integration test | Success path, agent failure, invalid LLM JSON |
| Score calculation | Unit test | Skill score, project score, risk penalty, clamping |
| Evidence chain creation | Unit + integration test | Every score item has JD and resume evidence |
| Integrity guard | Unit + eval tests | Unsupported metric, exaggerated responsibility, safe rewrite |
| RAG retrieval | Integration test | Seed docs retrieve expected skill documents |
| Learning task update | API test | todo -> doing -> done transitions |
| Resume version comparison | Service test | Added, removed, changed sections |
| Frontend report page | Component/E2E test | Loading, error, success, weak evidence state |
| Agent trace page | Component/E2E test | Redacted node summaries and failure node |
| Docker boot | Smoke test | frontend, backend, postgres health |

LLM evals required:

- JD parser extraction accuracy on 5 sample JDs.
- Resume parser extraction accuracy on 5 sample resumes.
- Integrity guard blocks unsupported claims.
- Report composer includes evidence references.

#### Performance Review

Main risks:

- Embedding all knowledge on every boot.
- Large JSON snapshots in `agent_runs`.
- Re-running JD and resume parsing for unchanged inputs.
- Slow report rendering if every evidence item is expanded by default.

Fixes:

- Seed embeddings once.
- Store summaries plus references for trace UI.
- Reuse parsed profiles.
- Paginate or collapse evidence-heavy sections.

#### Security and Privacy Review

Even single-user apps handle sensitive resume data.

Minimum requirements:

- Do not log raw resume text to console.
- Redact personal contact fields in agent trace UI.
- Validate file size and type before upload.
- Store API keys only in environment variables.
- Do not expose `.env` through Docker or frontend build.

#### Failure Modes Registry

| Failure Mode | Critical Gap? | Mitigation |
|---|---|---|
| Invalid LLM JSON breaks workflow | Yes | Pydantic schemas, repair retry, node-level error |
| Score cannot be reproduced | Yes | Deterministic score engine and stored raw factors |
| RAG evidence missing but report sounds confident | Yes | Mark weak evidence and lower confidence |
| Resume data leaks through logs or UI traces | Yes | Redaction and logging rules |
| Docker setup fails due pgvector extension | Medium | Health checks and migration script enabling extension |
| Upload parser fails on PDF/DOCX | Medium | Text-first MVP, optional parsers later |

#### Engineering Completion Summary

| Area | Rating | Decision |
|---|---:|---|
| Architecture | 8/10 | Good boundaries, add schema contracts |
| Data model | 7/10 | Add schema versions and score raw factors |
| Testing | 5/10 | Needs explicit unit, integration, E2E, and LLM evals |
| Performance | 7/10 | Manageable if embeddings and trace data are controlled |
| Security/privacy | 6/10 | Add redaction and upload validation |
| Deployment | 7/10 | Docker Compose is right, pgvector migration must be explicit |

Phase 3 result: passed with engineering additions required before implementation.

### Cross-Phase Themes

Theme: the app must produce action, not just analysis. Flagged in product and design review. Add `Next Best Action` and "Create next resume version" flows.

Theme: trust is the product. Flagged in all phases. Deterministic scoring, evidence chains, integrity guard, redaction, and weak-evidence labels are not extras. They are the core.

Theme: scope is correct now. Flagged in product and engineering review. Do not re-add HR, mentor, or auth scope.

### Autoplan Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
| 1 | Product | Add `Next Best Action` to workspace | Auto-decided | Complete user loop | The user needs an action today, not only a report | Report-only workspace |
| 2 | Product | Keep single-user scope | Auto-decided | Respect explicit user direction | User rejected dual-end product | HR/mentor workflows |
| 3 | Design | Add explicit empty/loading/error/partial states | Auto-decided | Complete implementation | These states appear in normal use and affect trust | Happy-path UI only |
| 4 | Design | Use structured report rows, not long generated prose | Auto-decided | User comprehension | Evidence and risk must be scannable | Wall-of-text report |
| 5 | Design | Add accessibility baseline | Auto-decided | Quality bar | Keyboard and non-color risk signals are cheap to include | Visual-only UI |
| 6 | Engineering | Start with schemas and deterministic scoring tests | Auto-decided | De-risk core system | Trust depends on reproducible scoring | Frontend-first build |
| 7 | Engineering | Add schema version fields | Auto-decided | Future-proof data | Parsed JSON will evolve during development | Unversioned JSONB |
| 8 | Engineering | Use redacted agent trace summaries in UI | Auto-decided | Privacy | Resume data is sensitive even in a local app | Raw trace display |

### Autoplan Final Recommendation

Approve the plan with the additions above. The direction is strong now: a single-user career growth workspace with persistent memory, explainable scoring, integrity protection, and score trends.

Do not start by building all pages. Start by making one analysis trustworthy end to end:

```text
seed knowledge
  -> create job
  -> create resume
  -> parse both
  -> retrieve standards
  -> score deterministically
  -> produce evidence-backed report
  -> block fabricated suggestions
  -> persist trace
```
