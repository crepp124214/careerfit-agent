from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.error_handlers import register_error_handlers
from app.api.routes import agent_runs, analysis, interview, interview_routes, jobs, knowledge, learning, llm, reports, resumes, system
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


def _init_database() -> None:
    """Initialize database: create extension and tables"""
    with engine.connect() as conn:
        # Enable pgvector extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


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
    if settings.database_url.startswith("sqlite"):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        _init_database()
    app = FastAPI(title=settings.app_name)
    
    # CORS 配置：生产环境允许所有来源，开发环境允许本地地址
    allow_origins = ["*"] if settings.environment == "production" else [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root() -> dict[str, str]:
        return {"status": "ok", "message": "CareerFit Agent API"}

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
    app.include_router(interview_routes.router)  # 新增：独立面试功能 API
    app.include_router(learning.router)
    app.include_router(llm.router)
    app.include_router(system.router)

    # 注册全局错误处理器
    register_error_handlers(app)

    return app


app = create_app()
