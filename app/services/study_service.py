import json
from datetime import date

from sqlalchemy.orm import Session

from app.models import SavedStudyPlan


def save_plan_to_db(db: Session, payload: dict) -> dict:
    saved = SavedStudyPlan(
        subject=str(payload["subject"]).strip(),
        days=int(payload["days"]),
        level=str(payload["level"]).strip(),
        daily_minutes=int(payload["daily_minutes"]),
        notes=(payload.get("notes") or "").strip() or None,
        plan_data=json.dumps(payload.get("plan", [])),
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {
        "id": saved.id,
        "subject": saved.subject,
        "days": saved.days,
        "level": saved.level,
        "daily_minutes": saved.daily_minutes,
        "notes": saved.notes,
        "plan": json.loads(saved.plan_data),
        "created_at": saved.created_at.isoformat(),
    }


def serialize_saved_plan(saved: SavedStudyPlan) -> dict:
    return {
        "id": saved.id,
        "subject": saved.subject,
        "days": saved.days,
        "level": saved.level,
        "daily_minutes": saved.daily_minutes,
        "notes": saved.notes,
        "plan": json.loads(saved.plan_data),
        "created_at": saved.created_at.isoformat(),
    }


def parse_due_date(due_date: str | None) -> date | None:
    if not due_date:
        return None
    return date.fromisoformat(due_date)
