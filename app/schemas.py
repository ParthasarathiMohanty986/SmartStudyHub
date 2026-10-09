from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    due_date: date | None = None

    @field_validator("title", "description")
    @classmethod
    def strip_values(cls, value: str) -> str:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty.")
        return cleaned


class TaskRead(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime


class StudyPlanDay(BaseModel):
    day: int = Field(..., ge=1)
    focus: str = Field(..., min_length=1)
    tasks: List[str] = Field(..., min_length=1)
    minutes: int = Field(..., ge=10)


class StudyPlanRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    days: int = Field(..., ge=1, le=30)
    level: Literal["Beginner", "Intermediate", "Advanced"]
    daily_minutes: int = Field(..., ge=15, le=600)
    notes: str | None = Field(default=None, max_length=2000)


class StudyPlanResponse(BaseModel):
    subject: str
    days: int
    level: str
    daily_minutes: int
    notes: str | None = None
    plan: List[StudyPlanDay]


class SummaryStyle(str):
    pass


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    style: Literal["Short summary", "Detailed summary", "Important points"] = "Short summary"


class SummaryResponse(BaseModel):
    summary: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class QuizRequest(BaseModel):
    material: str = Field(..., min_length=20, max_length=20000)
    question_count: int = Field(..., ge=1, le=10)


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class ChatAgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatAgentResponse(BaseModel):
    answer: str
    tool_used: bool = False
