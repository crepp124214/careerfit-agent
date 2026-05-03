from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reports import AgentRunRead
from app.services.analysis_service import list_agent_runs

router = APIRouter(prefix="/api/agent-runs", tags=["agent-runs"])


@router.get("/{task_id}", response_model=list[AgentRunRead])
def list_agent_runs_endpoint(task_id: int, db: Session = Depends(get_db)):
    return list_agent_runs(db, task_id)
