from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routers import chat, plans, quizzes, summaries, tasks

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Study & Task Assistant", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(tasks.router)
app.include_router(plans.router)
app.include_router(summaries.router)
app.include_router(quizzes.router)
app.include_router(chat.router)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def dashboard(request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/plans")
def plans_page(request):
    return templates.TemplateResponse("plans.html", {"request": request})


@app.get("/summarizer")
def summarizer_page(request):
    return templates.TemplateResponse("summarizer.html", {"request": request})


@app.get("/quiz")
def quiz_page(request):
    return templates.TemplateResponse("quiz.html", {"request": request})


@app.get("/tasks")
def tasks_page(request):
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/chat")
def chat_page(request):
    return templates.TemplateResponse("chat.html", {"request": request})
