# CareerFit Agent Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first trustworthy end-to-end vertical slice: create a target job, create a resume version, run deterministic JD-resume analysis, persist an evidence-backed report, expose agent traces, and show the result in a Vue3 workspace.

**Architecture:** Use a FastAPI backend with SQLAlchemy models, Pydantic schemas, deterministic scoring, a LangGraph-compatible workflow boundary, PostgreSQL + pgvector storage, and a Vue3 frontend. Phase 1 keeps LLM calls behind replaceable agent node interfaces and ships with rule-based local fallbacks so the system can run in development without paid model access.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL, pgvector, LangGraph, Vue3, TypeScript, Vite, Docker Compose, pytest, Vitest, Playwright.

---

## Scope

This plan implements Phase 1 only. It intentionally does not implement login, HR workflows, mentor dashboards, PDF/DOCX parsing, full interview sessions, or production background workers.

Phase 1 must prove the core trust loop:

```text
seed knowledge
  -> create target job
  -> create resume version
  -> parse both
  -> retrieve standards
  -> score deterministically
  -> produce evidence-backed report
  -> block fabricated suggestions
  -> persist trace
  -> show report and next best action
```

## File Structure

Create this structure:

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
        agent_runs.py
        knowledge.py
    agents/
      graph.py
      nodes.py
      state.py
    core/
      config.py
      logging.py
    db/
      base.py
      models.py
      session.py
    rag/
      seed_data.py
      retriever.py
    schemas/
      jobs.py
      resumes.py
      analysis.py
      reports.py
      knowledge.py
    scoring/
      evidence.py
      rules.py
      rubric.py
    services/
      analysis_service.py
      job_service.py
      resume_service.py
      knowledge_service.py
  tests/
    test_jobs_api.py
    test_resumes_api.py
    test_scoring.py
    test_integrity_guard.py
    test_analysis_flow.py
frontend/
  src/
    App.vue
    main.ts
    api/
      client.ts
      jobs.ts
      resumes.ts
      analysis.ts
      reports.ts
    components/
      AgentTimeline.vue
      EvidenceTable.vue
      ScoreBreakdown.vue
      StatusBadge.vue
    views/
      WorkspaceView.vue
      ReportView.vue
  tests/
    WorkspaceView.test.ts
docker-compose.yml
```

Each layer has one job:

- API routes translate HTTP requests into service calls.
- Services coordinate database, scoring, and workflow execution.
- Agents create structured intermediate outputs and trace records.
- Scoring contains deterministic math only.
- RAG contains seed knowledge and retrieval.
- Frontend views compose reusable components.

## Task 1: Backend Project Skeleton

**Files:**

- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/models.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create backend dependencies**

Create `backend/pyproject.toml`:

```toml
[project]
name = "careerfit-agent-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "pydantic>=2.8.0",
  "pydantic-settings>=2.4.0",
  "sqlalchemy>=2.0.32",
  "psycopg[binary]>=3.2.1",
  "pgvector>=0.3.2",
  "langgraph>=0.2.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "httpx>=0.27.0",
  "ruff>=0.6.0",
]

[build-system]
requires = ["setuptools>=72.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: Add configuration**

Create `backend/app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+pysqlite:///./careerfit_dev.db"
    app_name: str = "CareerFit Agent"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CAREERFIT_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 3: Add database session**

Create `backend/app/db/session.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Add declarative base**

Create `backend/app/db/base.py`:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

- [ ] **Step 5: Add initial models**

Create `backend/app/db/models.py`:

```python
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisStatus(str, Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False)
    resume_version_id: Mapped[int] = mapped_column(ForeignKey("resume_versions.id"), nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(SQLEnum(AnalysisStatus), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    job: Mapped[JobDescription] = relationship()
    resume_version: Mapped[ResumeVersion] = relationship()


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("analysis_tasks.id"), nullable=False, unique=True)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    strengths: Mapped[list] = mapped_column(JSON, nullable=False)
    gaps: Mapped[list] = mapped_column(JSON, nullable=False)
    integrity_risks: Mapped[list] = mapped_column(JSON, nullable=False)
    resume_suggestions: Mapped[list] = mapped_column(JSON, nullable=False)
    interview_questions: Mapped[list] = mapped_column(JSON, nullable=False)
    learning_plan: Mapped[list] = mapped_column(JSON, nullable=False)
    next_best_action: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("analysis_tasks.id"), nullable=False)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    token_usage: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- [ ] **Step 6: Add FastAPI app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="CareerFit Agent")

    @app.on_event("startup")
    def create_tables() -> None:
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 7: Add test database fixture**

Create `backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

- [ ] **Step 8: Run skeleton test**

Run:

```powershell
cd backend
python -m pip install -e ".[dev]"
pytest -q
```

Expected:

```text
no tests ran
```

- [ ] **Step 9: Commit**

```powershell
git add backend
git commit -m "chore: scaffold backend application"
```

## Task 2: Job And Resume APIs

**Files:**

- Create: `backend/app/schemas/jobs.py`
- Create: `backend/app/schemas/resumes.py`
- Create: `backend/app/services/job_service.py`
- Create: `backend/app/services/resume_service.py`
- Create: `backend/app/api/routes/jobs.py`
- Create: `backend/app/api/routes/resumes.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_jobs_api.py`
- Test: `backend/tests/test_resumes_api.py`

- [ ] **Step 1: Write failing job API tests**

Create `backend/tests/test_jobs_api.py`:

```python
def test_create_job_from_text(client):
    response = client.post(
        "/api/jobs",
        json={
            "title": "大模型应用开发工程师",
            "company": "Example AI",
            "raw_text": "负责 RAG 应用开发，熟悉 FastAPI、LangGraph、PostgreSQL、pgvector。",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["title"] == "大模型应用开发工程师"
    assert "FastAPI" in body["parsed_profile"]["required_skills"]


def test_reject_empty_job(client):
    response = client.post("/api/jobs", json={"title": "空岗位", "raw_text": "   "})

    assert response.status_code == 422
```

- [ ] **Step 2: Write failing resume API tests**

Create `backend/tests/test_resumes_api.py`:

```python
def test_create_resume_version_from_text(client):
    response = client.post(
        "/api/resumes",
        json={
            "name": "v1-original",
            "raw_text": "项目：CareerFit Agent。使用 FastAPI、Vue3、PostgreSQL 和 LangGraph 构建求职分析系统。",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "v1-original"
    assert "FastAPI" in body["parsed_profile"]["skills"]


def test_reject_empty_resume(client):
    response = client.post("/api/resumes", json={"name": "empty", "raw_text": ""})

    assert response.status_code == 422
```

- [ ] **Step 3: Run tests and verify failure**

Run:

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

Expected: failures because routes do not exist.

- [ ] **Step 4: Add schemas**

Create `backend/app/schemas/jobs.py`:

```python
from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    company: str | None = Field(default=None, max_length=200)
    raw_text: str = Field(min_length=20)


class JobRead(BaseModel):
    id: int
    title: str
    company: str | None
    raw_text: str
    parsed_profile: dict

    model_config = {"from_attributes": True}
```

Create `backend/app/schemas/resumes.py`:

```python
from pydantic import BaseModel, Field


class ResumeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    raw_text: str = Field(min_length=20)


class ResumeRead(BaseModel):
    id: int
    name: str
    raw_text: str
    parsed_profile: dict

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Add services**

Create `backend/app/services/job_service.py`:

```python
from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jobs import JobCreate


KNOWN_SKILLS = ["FastAPI", "LangGraph", "PostgreSQL", "pgvector", "Vue3", "Docker", "RAG"]


def parse_job_profile(raw_text: str) -> dict:
    required_skills = [skill for skill in KNOWN_SKILLS if skill.lower() in raw_text.lower()]
    return {
        "schema_version": "job_profile.v1",
        "required_skills": required_skills,
        "preferred_skills": [],
        "responsibilities": [raw_text[:160]],
        "evidence": [{"source": "raw_jd", "text": raw_text[:240]}],
    }


def create_job(db: Session, payload: JobCreate) -> JobDescription:
    job = JobDescription(
        title=payload.title,
        company=payload.company,
        raw_text=payload.raw_text,
        parsed_profile=parse_job_profile(payload.raw_text),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> list[JobDescription]:
    return list(db.query(JobDescription).order_by(JobDescription.id.desc()).all())


def get_job(db: Session, job_id: int) -> JobDescription | None:
    return db.get(JobDescription, job_id)
```

Create `backend/app/services/resume_service.py`:

```python
from sqlalchemy.orm import Session

from app.db.models import ResumeVersion
from app.schemas.resumes import ResumeCreate
from app.services.job_service import KNOWN_SKILLS


def parse_resume_profile(raw_text: str) -> dict:
    skills = [skill for skill in KNOWN_SKILLS if skill.lower() in raw_text.lower()]
    return {
        "schema_version": "resume_profile.v1",
        "skills": skills,
        "projects": [{"name": "Parsed Project", "description": raw_text[:240]}],
        "evidence": [
            {"skill": skill, "source": "raw_resume", "text": raw_text[:240]} for skill in skills
        ],
    }


def create_resume(db: Session, payload: ResumeCreate) -> ResumeVersion:
    resume = ResumeVersion(
        name=payload.name,
        raw_text=payload.raw_text,
        parsed_profile=parse_resume_profile(payload.raw_text),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session) -> list[ResumeVersion]:
    return list(db.query(ResumeVersion).order_by(ResumeVersion.id.desc()).all())


def get_resume(db: Session, resume_id: int) -> ResumeVersion | None:
    return db.get(ResumeVersion, resume_id)
```

- [ ] **Step 6: Add routes**

Create `backend/app/api/routes/jobs.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import JobCreate, JobRead
from app.services.job_service import create_job, get_job, list_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job_endpoint(payload: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, payload)


@router.get("", response_model=list[JobRead])
def list_jobs_endpoint(db: Session = Depends(get_db)):
    return list_jobs(db)


@router.get("/{job_id}", response_model=JobRead)
def get_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
```

Create `backend/app/api/routes/resumes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.resumes import ResumeCreate, ResumeRead
from app.services.resume_service import create_resume, get_resume, list_resumes

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume_endpoint(payload: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db, payload)


@router.get("", response_model=list[ResumeRead])
def list_resumes_endpoint(db: Session = Depends(get_db)):
    return list_resumes(db)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume_endpoint(resume_id: int, db: Session = Depends(get_db)):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
```

- [ ] **Step 7: Register routes**

Modify `backend/app/main.py`:

```python
from fastapi import FastAPI

from app.api.routes import jobs, resumes
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="CareerFit Agent")

    @app.on_event("startup")
    def create_tables() -> None:
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(jobs.router)
    app.include_router(resumes.router)
    return app


app = create_app()
```

- [ ] **Step 8: Run tests and verify pass**

Run:

```powershell
cd backend
pytest tests/test_jobs_api.py tests/test_resumes_api.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```powershell
git add backend/app backend/tests
git commit -m "feat: add job and resume APIs"
```

## Task 3: Deterministic Scoring And Integrity Guard

**Files:**

- Create: `backend/app/scoring/rubric.py`
- Create: `backend/app/scoring/rules.py`
- Create: `backend/app/scoring/evidence.py`
- Create: `backend/tests/test_scoring.py`
- Create: `backend/tests/test_integrity_guard.py`

- [ ] **Step 1: Write failing scoring tests**

Create `backend/tests/test_scoring.py`:

```python
from app.scoring.rules import score_match


def test_score_match_uses_shared_skills_and_evidence():
    jd_profile = {
        "required_skills": ["FastAPI", "LangGraph", "pgvector"],
        "evidence": [{"source": "raw_jd", "text": "需要 FastAPI、LangGraph、pgvector"}],
    }
    resume_profile = {
        "skills": ["FastAPI", "LangGraph"],
        "evidence": [
            {"skill": "FastAPI", "source": "raw_resume", "text": "使用 FastAPI 构建接口"},
            {"skill": "LangGraph", "source": "raw_resume", "text": "使用 LangGraph 编排 Agent"},
        ],
    }

    result = score_match(jd_profile, resume_profile)

    assert 0 <= result["final_score"] <= 100
    assert result["score_breakdown"]["skill_score"] > 0
    assert len(result["score_items"]) == 3
    assert result["score_items"][0]["jd_evidence"]


def test_score_match_clamps_empty_inputs():
    result = score_match({"required_skills": []}, {"skills": []})

    assert result["final_score"] == 0
    assert result["score_breakdown"]["skill_score"] == 0
```

- [ ] **Step 2: Write failing integrity tests**

Create `backend/tests/test_integrity_guard.py`:

```python
from app.scoring.evidence import assess_integrity_risk


def test_blocks_unsupported_metric():
    suggestion = "将系统性能提升 40%，主导生产级招聘平台落地。"
    resume_text = "使用 FastAPI 构建求职分析系统原型。"

    risk = assess_integrity_risk(suggestion, resume_text)

    assert risk["risk_level"] == "high"
    assert "unsupported_metric" in risk["risk_types"]
    assert "unsupported_leadership_claim" in risk["risk_types"]


def test_allows_safe_rewording():
    suggestion = "使用 FastAPI 构建求职分析系统原型，支持岗位与简历文本分析。"
    resume_text = "使用 FastAPI 构建求职分析系统原型。"

    risk = assess_integrity_risk(suggestion, resume_text)

    assert risk["risk_level"] == "low"
```

- [ ] **Step 3: Run tests and verify failure**

Run:

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

Expected: import errors because scoring modules do not exist.

- [ ] **Step 4: Implement rubric**

Create `backend/app/scoring/rubric.py`:

```python
LEVEL_SCORES = {
    "not_mentioned": 0.0,
    "mentioned": 0.3,
    "basic_usage": 0.5,
    "project_practice": 0.75,
    "deep_experience": 1.0,
}


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))
```

- [ ] **Step 5: Implement evidence and integrity risk**

Create `backend/app/scoring/evidence.py`:

```python
import re


LEADERSHIP_TERMS = ["主导", "负责架构", "架构设计", "落地生产", "生产级"]


def find_resume_evidence(skill: str, resume_profile: dict) -> str:
    for item in resume_profile.get("evidence", []):
        if item.get("skill") == skill:
            return item.get("text", "")
    return ""


def assess_integrity_risk(suggestion: str, resume_text: str) -> dict:
    risk_types: list[str] = []
    if re.search(r"\d+%|\d+倍|\d+\s*ms", suggestion) and not re.search(r"\d+%|\d+倍|\d+\s*ms", resume_text):
        risk_types.append("unsupported_metric")
    if any(term in suggestion for term in LEADERSHIP_TERMS) and not any(term in resume_text for term in LEADERSHIP_TERMS):
        risk_types.append("unsupported_leadership_claim")
    return {
        "risk_level": "high" if risk_types else "low",
        "risk_types": risk_types,
        "suggestion": suggestion,
    }
```

- [ ] **Step 6: Implement scoring**

Create `backend/app/scoring/rules.py`:

```python
from app.scoring.evidence import find_resume_evidence
from app.scoring.rubric import clamp_score


def score_match(jd_profile: dict, resume_profile: dict) -> dict:
    required_skills = jd_profile.get("required_skills", [])
    resume_skills = set(resume_profile.get("skills", []))
    jd_evidence = " ".join(item.get("text", "") for item in jd_profile.get("evidence", []))

    if not required_skills:
        return {
            "final_score": 0,
            "score_breakdown": {
                "skill_score": 0,
                "project_score": 0,
                "domain_score": 0,
                "basic_requirement_score": 0,
                "expression_score": 0,
                "integrity_risk_penalty": 0,
            },
            "score_items": [],
        }

    score_items = []
    matched = 0
    for skill in required_skills:
        is_matched = skill in resume_skills
        matched += 1 if is_matched else 0
        score_items.append(
            {
                "skill": skill,
                "required_level": "project_practice",
                "resume_level": "project_practice" if is_matched else "not_mentioned",
                "score": 75 if is_matched else 0,
                "jd_evidence": jd_evidence,
                "resume_evidence": find_resume_evidence(skill, resume_profile),
                "knowledge_evidence": "Phase 1 local rubric: project evidence is required for strong match.",
                "reason": "Matched with resume evidence." if is_matched else "Required skill missing in resume.",
            }
        )

    skill_score = clamp_score((matched / len(required_skills)) * 100)
    project_score = clamp_score(skill_score * 0.8)
    domain_score = clamp_score(skill_score * 0.7)
    basic_requirement_score = 80 if matched else 0
    expression_score = clamp_score(skill_score * 0.75)
    integrity_risk_penalty = 0
    final_score = clamp_score(
        skill_score * 0.35
        + project_score * 0.25
        + domain_score * 0.15
        + basic_requirement_score * 0.10
        + expression_score * 0.10
        - integrity_risk_penalty * 0.05
    )

    return {
        "final_score": final_score,
        "score_breakdown": {
            "skill_score": skill_score,
            "project_score": project_score,
            "domain_score": domain_score,
            "basic_requirement_score": basic_requirement_score,
            "expression_score": expression_score,
            "integrity_risk_penalty": integrity_risk_penalty,
        },
        "score_items": score_items,
    }
```

- [ ] **Step 7: Run tests and verify pass**

Run:

```powershell
cd backend
pytest tests/test_scoring.py tests/test_integrity_guard.py -q
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```powershell
git add backend/app/scoring backend/tests/test_scoring.py backend/tests/test_integrity_guard.py
git commit -m "feat: add deterministic scoring and integrity guard"
```

## Task 4: Analysis Workflow And Reports

**Files:**

- Create: `backend/app/schemas/analysis.py`
- Create: `backend/app/schemas/reports.py`
- Create: `backend/app/agents/state.py`
- Create: `backend/app/agents/nodes.py`
- Create: `backend/app/agents/graph.py`
- Create: `backend/app/services/analysis_service.py`
- Create: `backend/app/api/routes/analysis.py`
- Create: `backend/app/api/routes/reports.py`
- Create: `backend/app/api/routes/agent_runs.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_analysis_flow.py`

- [ ] **Step 1: Write failing analysis flow test**

Create `backend/tests/test_analysis_flow.py`:

```python
def test_run_analysis_creates_report_and_agent_runs(client):
    job = client.post(
        "/api/jobs",
        json={
            "title": "大模型应用开发工程师",
            "raw_text": "负责 RAG 应用开发，熟悉 FastAPI、LangGraph、PostgreSQL、pgvector。",
        },
    ).json()
    resume = client.post(
        "/api/resumes",
        json={
            "name": "v1",
            "raw_text": "使用 FastAPI、LangGraph、PostgreSQL 构建 CareerFit Agent 求职分析系统。",
        },
    ).json()

    task_response = client.post(
        "/api/analysis",
        json={"job_id": job["id"], "resume_version_id": resume["id"]},
    )

    assert task_response.status_code == 201
    task = task_response.json()
    assert task["status"] == "success"

    report = client.get(f"/api/reports/{task['id']}").json()
    assert report["final_score"] > 0
    assert report["next_best_action"]["title"]
    assert report["score_breakdown"]["skill_score"] > 0

    runs = client.get(f"/api/agent-runs/{task['id']}").json()
    assert len(runs) >= 5
    assert runs[0]["node_name"] == "jd_parser"
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

Expected: route not found.

- [ ] **Step 3: Add schemas**

Create `backend/app/schemas/analysis.py`:

```python
from pydantic import BaseModel


class AnalysisCreate(BaseModel):
    job_id: int
    resume_version_id: int


class AnalysisTaskRead(BaseModel):
    id: int
    job_id: int
    resume_version_id: int
    status: str
    error_message: str | None

    model_config = {"from_attributes": True}
```

Create `backend/app/schemas/reports.py`:

```python
from pydantic import BaseModel


class ReportRead(BaseModel):
    id: int
    task_id: int
    final_score: float
    score_breakdown: dict
    strengths: list
    gaps: list
    integrity_risks: list
    resume_suggestions: list
    interview_questions: list
    learning_plan: list
    next_best_action: dict

    model_config = {"from_attributes": True}


class AgentRunRead(BaseModel):
    id: int
    task_id: int
    node_name: str
    input_snapshot: dict
    output_snapshot: dict
    latency_ms: int
    token_usage: dict
    status: str
    error_message: str | None

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Add workflow state and nodes**

Create `backend/app/agents/state.py`:

```python
from typing import TypedDict


class CareerFitState(TypedDict, total=False):
    raw_jd: str
    raw_resume: str
    jd_profile: dict
    resume_profile: dict
    match_result: dict
    gaps: list
    integrity_risks: list
    resume_suggestions: list
    interview_questions: list
    learning_plan: list
    next_best_action: dict
```

Create `backend/app/agents/nodes.py`:

```python
from app.scoring.evidence import assess_integrity_risk
from app.scoring.rules import score_match
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


def jd_parser(state: dict) -> dict:
    state["jd_profile"] = parse_job_profile(state["raw_jd"])
    return state


def resume_parser(state: dict) -> dict:
    state["resume_profile"] = parse_resume_profile(state["raw_resume"])
    return state


def match_scorer(state: dict) -> dict:
    state["match_result"] = score_match(state["jd_profile"], state["resume_profile"])
    return state


def gap_analyzer(state: dict) -> dict:
    gaps = []
    for item in state["match_result"]["score_items"]:
        if item["resume_level"] == "not_mentioned":
            gaps.append({"type": "missing_skill", "skill": item["skill"], "action": "Add learning task"})
        elif not item["resume_evidence"]:
            gaps.append({"type": "weak_evidence", "skill": item["skill"], "action": "Add project evidence"})
    state["gaps"] = gaps
    return state


def resume_optimizer(state: dict) -> dict:
    suggestions = []
    risks = []
    for item in state["match_result"]["score_items"]:
        if item["resume_evidence"]:
            text = f"围绕 {item['skill']} 补充项目中的具体职责和结果，但不新增未发生的指标。"
            risk = assess_integrity_risk(text, state["raw_resume"])
            suggestions.append({"skill": item["skill"], "optimized_text": text, "risk": risk})
            risks.append(risk)
    state["resume_suggestions"] = suggestions
    state["integrity_risks"] = [risk for risk in risks if risk["risk_level"] != "low"]
    return state


def interview_coach(state: dict) -> dict:
    state["interview_questions"] = [
        {"skill": item["skill"], "question": f"请讲讲你在项目中如何使用 {item['skill']}？"}
        for item in state["match_result"]["score_items"]
    ]
    return state


def learning_planner(state: dict) -> dict:
    state["learning_plan"] = [
        {
            "skill": gap["skill"],
            "objective": f"补齐 {gap['skill']} 的项目证据",
            "status": "not_started",
            "acceptance_criteria": f"能用一段项目经历解释 {gap['skill']} 的实际使用",
        }
        for gap in state["gaps"]
    ]
    return state


def next_best_action(state: dict) -> dict:
    if state["gaps"]:
        first_gap = state["gaps"][0]
        state["next_best_action"] = {
            "title": f"优先补齐 {first_gap['skill']}",
            "reason": "这是当前目标岗位中影响匹配分的最高优先级缺口。",
            "action_type": first_gap["type"],
        }
    else:
        state["next_best_action"] = {
            "title": "创建下一版简历并重新分析",
            "reason": "当前主要技能已经匹配，可以通过表达和证据质量继续提升。",
            "action_type": "create_resume_version",
        }
    return state
```

- [ ] **Step 5: Add graph runner with trace logging**

Create `backend/app/agents/graph.py`:

```python
from collections.abc import Callable
from time import perf_counter

from sqlalchemy.orm import Session

from app.agents import nodes
from app.db.models import AgentRun


NODE_SEQUENCE: list[tuple[str, Callable[[dict], dict]]] = [
    ("jd_parser", nodes.jd_parser),
    ("resume_parser", nodes.resume_parser),
    ("match_scorer", nodes.match_scorer),
    ("gap_analyzer", nodes.gap_analyzer),
    ("resume_optimizer", nodes.resume_optimizer),
    ("interview_coach", nodes.interview_coach),
    ("learning_planner", nodes.learning_planner),
    ("next_best_action", nodes.next_best_action),
]


def redact_state(state: dict) -> dict:
    redacted = dict(state)
    if "raw_jd" in redacted:
        redacted["raw_jd"] = "[redacted]"
    if "raw_resume" in redacted:
        redacted["raw_resume"] = "[redacted]"
    return redacted


def run_workflow(db: Session, task_id: int, initial_state: dict) -> dict:
    state = initial_state
    for node_name, node_func in NODE_SEQUENCE:
        started = perf_counter()
        input_snapshot = redact_state(state)
        try:
            state = node_func(state)
            status = "success"
            error_message = None
        except Exception as exc:
            status = "failed"
            error_message = str(exc)
            raise
        finally:
            elapsed_ms = int((perf_counter() - started) * 1000)
            db.add(
                AgentRun(
                    task_id=task_id,
                    node_name=node_name,
                    input_snapshot=input_snapshot,
                    output_snapshot=redact_state(state),
                    latency_ms=elapsed_ms,
                    token_usage={},
                    status=status,
                    error_message=error_message,
                )
            )
            db.commit()
    return state
```

- [ ] **Step 6: Add analysis service and routes**

Create `backend/app/services/analysis_service.py`:

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import run_workflow
from app.db.models import AnalysisReport, AnalysisStatus, AnalysisTask
from app.schemas.analysis import AnalysisCreate
from app.services.job_service import get_job
from app.services.resume_service import get_resume


def create_analysis(db: Session, payload: AnalysisCreate) -> AnalysisTask:
    job = get_job(db, payload.job_id)
    resume = get_resume(db, payload.resume_version_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    task = AnalysisTask(
        job_id=job.id,
        resume_version_id=resume.id,
        status=AnalysisStatus.running,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        state = run_workflow(
            db,
            task.id,
            {"raw_jd": job.raw_text, "raw_resume": resume.raw_text},
        )
        match_result = state["match_result"]
        report = AnalysisReport(
            task_id=task.id,
            final_score=match_result["final_score"],
            score_breakdown=match_result["score_breakdown"],
            strengths=[
                {"skill": item["skill"], "reason": item["reason"]}
                for item in match_result["score_items"]
                if item["score"] > 0
            ],
            gaps=state["gaps"],
            integrity_risks=state["integrity_risks"],
            resume_suggestions=state["resume_suggestions"],
            interview_questions=state["interview_questions"],
            learning_plan=state["learning_plan"],
            next_best_action=state["next_best_action"],
        )
        db.add(report)
        task.status = AnalysisStatus.success
        db.commit()
        db.refresh(task)
        return task
    except Exception as exc:
        task.status = AnalysisStatus.failed
        task.error_message = str(exc)
        db.commit()
        db.refresh(task)
        return task
```

Create `backend/app/api/routes/analysis.py`:

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import AnalysisCreate, AnalysisTaskRead
from app.services.analysis_service import create_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisTaskRead, status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)):
    return create_analysis(db, payload)
```

Create `backend/app/api/routes/reports.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import AnalysisReport
from app.db.session import get_db
from app.schemas.reports import ReportRead

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{task_id}", response_model=ReportRead)
def get_report_endpoint(task_id: int, db: Session = Depends(get_db)):
    report = db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
```

Create `backend/app/api/routes/agent_runs.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import AgentRun
from app.db.session import get_db
from app.schemas.reports import AgentRunRead

router = APIRouter(prefix="/api/agent-runs", tags=["agent-runs"])


@router.get("/{task_id}", response_model=list[AgentRunRead])
def list_agent_runs_endpoint(task_id: int, db: Session = Depends(get_db)):
    return list(db.query(AgentRun).filter(AgentRun.task_id == task_id).order_by(AgentRun.id.asc()).all())
```

- [ ] **Step 7: Register routes**

Modify `backend/app/main.py`:

```python
from fastapi import FastAPI

from app.api.routes import agent_runs, analysis, jobs, reports, resumes
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="CareerFit Agent")

    @app.on_event("startup")
    def create_tables() -> None:
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(jobs.router)
    app.include_router(resumes.router)
    app.include_router(analysis.router)
    app.include_router(reports.router)
    app.include_router(agent_runs.router)
    return app


app = create_app()
```

- [ ] **Step 8: Run analysis tests**

Run:

```powershell
cd backend
pytest tests/test_analysis_flow.py -q
```

Expected: test passes.

- [ ] **Step 9: Run all backend tests**

Run:

```powershell
cd backend
pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 10: Commit**

```powershell
git add backend/app backend/tests
git commit -m "feat: add analysis workflow and reports"
```

## Task 5: Frontend Workspace And Report View

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/jobs.ts`
- Create: `frontend/src/api/resumes.ts`
- Create: `frontend/src/api/analysis.ts`
- Create: `frontend/src/api/reports.ts`
- Create: `frontend/src/components/StatusBadge.vue`
- Create: `frontend/src/components/ScoreBreakdown.vue`
- Create: `frontend/src/components/EvidenceTable.vue`
- Create: `frontend/src/components/AgentTimeline.vue`
- Create: `frontend/src/views/WorkspaceView.vue`
- Create: `frontend/src/views/ReportView.vue`
- Create: `frontend/tests/WorkspaceView.test.ts`

- [ ] **Step 1: Create frontend package**

Create `frontend/package.json`:

```json
{
  "name": "careerfit-agent-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vue-tsc && vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0",
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@vue/test-utils": "^2.4.6",
    "jsdom": "^24.1.1",
    "typescript": "^5.5.0",
    "vitest": "^2.0.5",
    "vue-tsc": "^2.0.29"
  }
}
```

- [ ] **Step 2: Add TypeScript and Vite config**

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "sourceMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "types": ["vitest/globals"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "tests/**/*.ts"]
}
```

Create `frontend/vite.config.ts`:

```ts
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "jsdom",
  },
});
```

- [ ] **Step 3: Add app shell**

Create `frontend/index.html`:

```html
<div id="app"></div>
<script type="module" src="/src/main.ts"></script>
```

Create `frontend/src/main.ts`:

```ts
import { createApp } from "vue";
import App from "./App.vue";

createApp(App).mount("#app");
```

Create `frontend/src/App.vue`:

```vue
<script setup lang="ts">
import { ref } from "vue";
import WorkspaceView from "./views/WorkspaceView.vue";
import ReportView from "./views/ReportView.vue";

const latestTaskId = ref<number | null>(null);
</script>

<template>
  <main class="app-shell">
    <WorkspaceView @analysis-complete="latestTaskId = $event" />
    <ReportView v-if="latestTaskId" :task-id="latestTaskId" />
  </main>
</template>

<style>
body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #172033;
  background: #f6f8fb;
}

.app-shell {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
}
</style>
```

- [ ] **Step 4: Add API clients**

Create `frontend/src/api/client.ts`:

```ts
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}
```

Create `frontend/src/api/jobs.ts`:

```ts
import { requestJson } from "./client";

export interface Job {
  id: number;
  title: string;
  company: string | null;
  raw_text: string;
  parsed_profile: { required_skills: string[] };
}

export function createJob(payload: { title: string; company?: string; raw_text: string }) {
  return requestJson<Job>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
```

Create `frontend/src/api/resumes.ts`:

```ts
import { requestJson } from "./client";

export interface ResumeVersion {
  id: number;
  name: string;
  raw_text: string;
  parsed_profile: { skills: string[] };
}

export function createResume(payload: { name: string; raw_text: string }) {
  return requestJson<ResumeVersion>("/api/resumes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
```

Create `frontend/src/api/analysis.ts`:

```ts
import { requestJson } from "./client";

export interface AnalysisTask {
  id: number;
  job_id: number;
  resume_version_id: number;
  status: string;
  error_message: string | null;
}

export function createAnalysis(payload: { job_id: number; resume_version_id: number }) {
  return requestJson<AnalysisTask>("/api/analysis", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
```

Create `frontend/src/api/reports.ts`:

```ts
import { requestJson } from "./client";

export interface Report {
  id: number;
  task_id: number;
  final_score: number;
  score_breakdown: Record<string, number>;
  strengths: Array<Record<string, string>>;
  gaps: Array<Record<string, string>>;
  integrity_risks: Array<Record<string, unknown>>;
  resume_suggestions: Array<Record<string, unknown>>;
  interview_questions: Array<Record<string, string>>;
  learning_plan: Array<Record<string, string>>;
  next_best_action: { title: string; reason: string; action_type: string };
}

export interface AgentRun {
  id: number;
  node_name: string;
  status: string;
  latency_ms: number;
}

export function getReport(taskId: number) {
  return requestJson<Report>(`/api/reports/${taskId}`);
}

export function getAgentRuns(taskId: number) {
  return requestJson<AgentRun[]>(`/api/agent-runs/${taskId}`);
}
```

- [ ] **Step 5: Add components**

Create `frontend/src/components/StatusBadge.vue`:

```vue
<script setup lang="ts">
defineProps<{ status: string }>();
</script>

<template>
  <span class="badge" :data-status="status">{{ status }}</span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: #eef2ff;
  color: #3446a8;
}

.badge[data-status="failed"] {
  background: #fff1f2;
  color: #b42318;
}
</style>
```

Create `frontend/src/components/ScoreBreakdown.vue`:

```vue
<script setup lang="ts">
defineProps<{ scores: Record<string, number> }>();
</script>

<template>
  <section class="score-grid" aria-label="Score breakdown">
    <article v-for="(value, key) in scores" :key="key" class="score-card">
      <div class="score-key">{{ key }}</div>
      <div class="score-value">{{ value }}</div>
    </article>
  </section>
</template>

<style scoped>
.score-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.score-card {
  background: white;
  border: 1px solid #d9e2ef;
  border-radius: 8px;
  padding: 14px;
}

.score-key {
  font-size: 13px;
  color: #64748b;
}

.score-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 700;
}
</style>
```

Create `frontend/src/components/AgentTimeline.vue`:

```vue
<script setup lang="ts">
import StatusBadge from "./StatusBadge.vue";

defineProps<{ runs: Array<{ id: number; node_name: string; status: string; latency_ms: number }> }>();
</script>

<template>
  <ol class="timeline" aria-label="Agent run timeline">
    <li v-for="run in runs" :key="run.id">
      <span>{{ run.node_name }}</span>
      <StatusBadge :status="run.status" />
      <small>{{ run.latency_ms }}ms</small>
    </li>
  </ol>
</template>

<style scoped>
.timeline {
  display: grid;
  gap: 8px;
  padding: 0;
  list-style: none;
}

.timeline li {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  align-items: center;
  background: white;
  border: 1px solid #d9e2ef;
  border-radius: 8px;
  padding: 10px 12px;
}
</style>
```

Create `frontend/src/components/EvidenceTable.vue`:

```vue
<script setup lang="ts">
defineProps<{ rows: Array<Record<string, string>> }>();
</script>

<template>
  <table class="evidence-table">
    <thead>
      <tr>
        <th>技能</th>
        <th>说明</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, index) in rows" :key="index">
        <td>{{ row.skill }}</td>
        <td>{{ row.reason || row.action || row.question }}</td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.evidence-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border: 1px solid #d9e2ef;
}

th,
td {
  padding: 10px;
  border-bottom: 1px solid #edf2f7;
  text-align: left;
}
</style>
```

- [ ] **Step 6: Add views**

Create `frontend/src/views/WorkspaceView.vue`:

```vue
<script setup lang="ts">
import { ref } from "vue";
import { createAnalysis } from "../api/analysis";
import { createJob } from "../api/jobs";
import { createResume } from "../api/resumes";

const emit = defineEmits<{ "analysis-complete": [taskId: number] }>();

const jobText = ref("负责 RAG 应用开发，熟悉 FastAPI、LangGraph、PostgreSQL、pgvector。");
const resumeText = ref("使用 FastAPI、LangGraph、PostgreSQL 构建 CareerFit Agent 求职分析系统。");
const status = ref("ready");
const error = ref("");

async function runAnalysis() {
  status.value = "running";
  error.value = "";
  try {
    const job = await createJob({ title: "大模型应用开发工程师", raw_text: jobText.value });
    const resume = await createResume({ name: "v1-original", raw_text: resumeText.value });
    const task = await createAnalysis({ job_id: job.id, resume_version_id: resume.id });
    status.value = task.status;
    emit("analysis-complete", task.id);
  } catch (err) {
    status.value = "failed";
    error.value = err instanceof Error ? err.message : "分析失败";
  }
}
</script>

<template>
  <section class="workspace">
    <header>
      <p class="eyebrow">CareerFit Agent</p>
      <h1>个人求职成长工作台</h1>
    </header>

    <div class="input-grid">
      <label>
        目标岗位 JD
        <textarea v-model="jobText" />
      </label>
      <label>
        当前简历版本
        <textarea v-model="resumeText" />
      </label>
    </div>

    <div class="actions">
      <button :disabled="status === 'running'" @click="runAnalysis">
        {{ status === "running" ? "分析中" : "开始分析" }}
      </button>
      <span>{{ status }}</span>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<style scoped>
.workspace {
  display: grid;
  gap: 20px;
}

.eyebrow {
  color: #2563eb;
  font-weight: 700;
}

h1 {
  margin: 0;
  font-size: 32px;
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  font-weight: 700;
}

textarea {
  min-height: 180px;
  resize: vertical;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 12px;
  font: inherit;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

button {
  min-height: 40px;
  border: 0;
  border-radius: 8px;
  padding: 0 16px;
  background: #2563eb;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.error {
  color: #b42318;
}
</style>
```

Create `frontend/src/views/ReportView.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from "vue";
import AgentTimeline from "../components/AgentTimeline.vue";
import EvidenceTable from "../components/EvidenceTable.vue";
import ScoreBreakdown from "../components/ScoreBreakdown.vue";
import { getAgentRuns, getReport, type AgentRun, type Report } from "../api/reports";

const props = defineProps<{ taskId: number }>();

const report = ref<Report | null>(null);
const runs = ref<AgentRun[]>([]);
const error = ref("");

onMounted(async () => {
  try {
    report.value = await getReport(props.taskId);
    runs.value = await getAgentRuns(props.taskId);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "报告加载失败";
  }
});
</script>

<template>
  <section class="report">
    <p v-if="error" class="error">{{ error }}</p>
    <template v-if="report">
      <header class="report-header">
        <div>
          <p class="eyebrow">匹配报告</p>
          <h2>{{ report.final_score }} / 100</h2>
        </div>
        <aside class="next-action">
          <strong>{{ report.next_best_action.title }}</strong>
          <span>{{ report.next_best_action.reason }}</span>
        </aside>
      </header>

      <ScoreBreakdown :scores="report.score_breakdown" />
      <h3>优势</h3>
      <EvidenceTable :rows="report.strengths" />
      <h3>缺口</h3>
      <EvidenceTable :rows="report.gaps" />
      <h3>Agent 运行轨迹</h3>
      <AgentTimeline :runs="runs" />
    </template>
  </section>
</template>

<style scoped>
.report {
  margin-top: 28px;
  display: grid;
  gap: 16px;
}

.report-header {
  display: grid;
  grid-template-columns: 1fr minmax(260px, 420px);
  gap: 16px;
  align-items: stretch;
}

.eyebrow {
  color: #2563eb;
  font-weight: 700;
}

h2 {
  margin: 0;
  font-size: 42px;
}

.next-action {
  display: grid;
  gap: 8px;
  padding: 16px;
  background: #ecfdf5;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
}

.error {
  color: #b42318;
}

@media (max-width: 760px) {
  .report-header {
    grid-template-columns: 1fr;
  }
}
</style>
```

- [ ] **Step 7: Add frontend smoke test**

Create `frontend/tests/WorkspaceView.test.ts`:

```ts
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import WorkspaceView from "../src/views/WorkspaceView.vue";

describe("WorkspaceView", () => {
  it("shows the analysis workspace", () => {
    const wrapper = mount(WorkspaceView);

    expect(wrapper.text()).toContain("个人求职成长工作台");
    expect(wrapper.text()).toContain("目标岗位 JD");
    expect(wrapper.text()).toContain("当前简历版本");
  });
});
```

- [ ] **Step 8: Run frontend tests**

Run:

```powershell
cd frontend
npm install
npm test
```

Expected: all frontend tests pass.

- [ ] **Step 9: Commit**

```powershell
git add frontend
git commit -m "feat: add frontend workspace and report view"
```

## Task 6: Docker Compose And Smoke Verification

**Files:**

- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Add backend Dockerfile**

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Add frontend Dockerfile**

Create `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
```

- [ ] **Step 3: Add environment example**

Create `.env.example`:

```text
CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit
VITE_API_BASE=http://localhost:8000
```

- [ ] **Step 4: Add Docker Compose**

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: careerfit
      POSTGRES_PASSWORD: careerfit
      POSTGRES_DB: careerfit
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U careerfit -d careerfit"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: ./backend
    environment:
      CAREERFIT_DATABASE_URL: postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
    environment:
      VITE_API_BASE: http://localhost:8000
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

- [ ] **Step 5: Run Docker smoke test**

Run:

```powershell
docker compose up --build
```

Expected:

```text
backend listening on 0.0.0.0:8000
frontend listening on 0.0.0.0:5173
postgres healthy
```

Open:

```text
http://localhost:5173
```

Verify:

- Workspace loads.
- Clicking "开始分析" produces a report.
- Report shows final score.
- Report shows Next Best Action.
- Agent timeline shows node names.

- [ ] **Step 6: Commit**

```powershell
git add backend/Dockerfile frontend/Dockerfile docker-compose.yml .env.example
git commit -m "chore: add docker compose setup"
```

## Task 7: Final Verification

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Add README**

Create `README.md`:

```markdown
# CareerFit Agent

CareerFit Agent is a personal job-search growth workspace for computer science new graduates. It stores target jobs, resume versions, analysis reports, agent traces, and score trends.

## Tech Stack

- FastAPI
- LangGraph-compatible workflow boundary
- PostgreSQL + pgvector
- Vue3 + TypeScript + Vite
- Docker Compose

## Run Locally

```powershell
docker compose up --build
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

## Phase 1 Features

- Create target job from JD text.
- Create resume version from text.
- Run deterministic JD-resume matching analysis.
- Persist analysis report.
- Show explainable score breakdown.
- Show Next Best Action.
- Show redacted agent trace timeline.
- Block obvious fabricated resume claims through an integrity guard.
```

- [ ] **Step 2: Run all backend tests**

Run:

```powershell
cd backend
pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 3: Run all frontend tests**

Run:

```powershell
cd frontend
npm test
```

Expected: all frontend tests pass.

- [ ] **Step 4: Build Docker stack**

Run:

```powershell
docker compose up --build
```

Expected: backend, frontend, and postgres start successfully.

- [ ] **Step 5: Commit README**

```powershell
git add README.md
git commit -m "docs: add project README"
```

## Self-Review Checklist

- [ ] The plan implements the Phase 1 trust loop from the spec.
- [ ] Every persisted analysis has a report.
- [ ] Every report has a score breakdown.
- [ ] Every report has a Next Best Action.
- [ ] Agent traces redact raw JD and resume text.
- [ ] Scoring is deterministic and tested.
- [ ] Integrity guard is tested.
- [ ] Docker Compose starts all services.
- [ ] README explains how to run the project.
