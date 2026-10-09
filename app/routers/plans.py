import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SavedStudyPlan
from app.schemas import StudyPlanRequest, StudyPlanResponse
from app.services.llm_service import llm_service
from app.services.study_service import save_plan_to_db, serialize_saved_plan

router = APIRouter(prefix="/api")


@router.post("/plans/generate", response_model=StudyPlanResponse)
async def generate_study_plan(payload: StudyPlanRequest):
    try:
        plan = await llm_service.generate_study_plan(
            subject=payload.subject,
            days=payload.days,
            level=payload.level,
            daily_minutes=payload.daily_minutes,
            notes=payload.notes,
        )
        return plan
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - real API failure handling
        raise HTTPException(status_code=503, detail="The study plan service is currently unavailable.") from exc


@router.post("/plans")
def save_study_plan(payload: StudyPlanResponse, db: Session = Depends(get_db)):
    try:
        return save_plan_to_db(db, payload.model_dump())
    except Exception as exc:  # pragma: no cover - database safety
        raise HTTPException(status_code=400, detail="The plan could not be saved.") from exc


@router.get("/plans")
def list_study_plans(db: Session = Depends(get_db)):
    plans = db.query(SavedStudyPlan).order_by(SavedStudyPlan.created_at.desc()).all()
    return [serialize_saved_plan(plan) for plan in plans]
