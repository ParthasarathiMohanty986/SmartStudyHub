import os
from pathlib import Path

from fastapi.testclient import TestClient


os.environ.setdefault("GROQ_API_KEY", "test-api-key")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")
os.environ["DATABASE_URL"] = "sqlite:///./test_ai_study_assistant.db"

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_task_lifecycle():
    create_resp = client.post(
        "/api/tasks",
        json={
            "title": "Study Python",
            "description": "Review decorators and async patterns.",
            "due_date": "2026-10-12",
        },
    )
    assert create_resp.status_code == 201
    task = create_resp.json()
    assert task["title"] == "Study Python"

    list_resp = client.get("/api/tasks")
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert any(item["id"] == task["id"] for item in tasks)

    complete_resp = client.patch(f"/api/tasks/{task['id']}/complete")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"

    delete_resp = client.delete(f"/api/tasks/{task['id']}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["success"] is True


def test_invalid_task_payload():
    response = client.post("/api/tasks", json={"title": "", "description": ""})
    assert response.status_code == 422


def test_plan_validation():
    payload = {
        "subject": "Python",
        "days": 3,
        "level": "Beginner",
        "daily_minutes": 45,
        "notes": "Need basics",
    }
    response = client.post("/api/plans/generate", json=payload)
    assert response.status_code in {200, 503}


def test_quiz_generation_validation():
    payload = {"material": "Python is a language.", "question_count": 2}
    response = client.post("/api/quizzes/generate", json=payload)
    assert response.status_code in {200, 503}


def test_agent_invalid_arguments():
    response = client.post(
        "/api/chat/agent",
        json={"message": "Create a task with missing details"},
    )
    assert response.status_code in {200, 400, 503}


def test_missing_api_key_behavior(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from app import config
    config.load_settings()
    assert config.get_settings().groq_api_key in {None, ""}
