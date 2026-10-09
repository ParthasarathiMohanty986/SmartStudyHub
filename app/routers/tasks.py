from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskRead

router = APIRouter(prefix="/api")


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status="pending",
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    status: Literal["pending", "completed", "all"] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if status and status != "all":
        query = query.filter(Task.status == status)
    return query.order_by(Task.created_at.desc()).all()


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.status = "completed"
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
    return {"success": True, "task_id": task_id}
