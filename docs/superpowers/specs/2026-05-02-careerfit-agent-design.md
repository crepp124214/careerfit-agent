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
