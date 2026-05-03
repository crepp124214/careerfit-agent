from fastapi import FastAPI

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine


CAPABILITIES = {
    "jobs": "unavailable",
    "resumes": "unavailable",
    "analysis": "unavailable",
    "reports": "unavailable",
    "agentRuns": "unavailable",
    "learning": "unavailable",
}


def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/api/capabilities")
    def capabilities() -> dict[str, dict[str, str]]:
        return {"capabilities": CAPABILITIES}

    return app


app = create_app()
