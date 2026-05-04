from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent_runs, analysis, interview, jobs, knowledge, learning, reports, resumes
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


CAPABILITIES = {
    "jobs": "ready",
    "resumes": "ready",
    "analysis": "ready",
    "reports": "ready",
    "agentRuns": "ready",
    "learning": "ready",
    "knowledge": "ready",
    "interview": "ready",
}


def llm_capability() -> str:
    settings = get_settings()
    if settings.llm_enabled and settings.llm_api_key and settings.llm_model:
        return "ready"
    return "unavailable"


def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/api/capabilities")
    def capabilities() -> dict[str, dict[str, str]]:
        return {"capabilities": {**CAPABILITIES, "llm": llm_capability()}}

    app.include_router(jobs.router)
    app.include_router(resumes.router)
    app.include_router(analysis.router)
    app.include_router(reports.router)
    app.include_router(agent_runs.router)
    app.include_router(knowledge.router)
    app.include_router(interview.router)
    app.include_router(learning.router)

    return app


app = create_app()
