from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.learning import (
    LearningTaskGenerateRequest,
    LearningTaskRead,
    LearningTaskUpdateRequest,
)
from app.services.learning_service import (
    generate_learning_tasks,
    list_learning_tasks,
    update_learning_task_status,
)

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/tasks", response_model=list[LearningTaskRead])
def list_learning_tasks_endpoint(db: Session = Depends(get_db)):
    return list_learning_tasks(db)


@router.post("/tasks/generate", response_model=list[LearningTaskRead], status_code=status.HTTP_201_CREATED)
def generate_learning_tasks_endpoint(
    payload: LearningTaskGenerateRequest, db: Session = Depends(get_db)
):
    try:
        return generate_learning_tasks(db, payload.task_id)
    except ValueError as exc:
        if str(exc) == "report_not_found":
            raise HTTPException(status_code=404, detail="Report not found") from exc
        raise


@router.patch("/tasks/{task_id}", response_model=LearningTaskRead)
def update_learning_task_status_endpoint(
    task_id: int, payload: LearningTaskUpdateRequest, db: Session = Depends(get_db)
):
    try:
        return update_learning_task_status(db, task_id, payload.status)
    except ValueError as exc:
        if str(exc) == "learning_task_not_found":
            raise HTTPException(status_code=404, detail="Learning task not found") from exc
        if str(exc) == "invalid_status_transition":
            raise HTTPException(status_code=400, detail="Invalid learning task status transition") from exc
        raise
