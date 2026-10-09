from fastapi import APIRouter, HTTPException

from app.schemas import QuizRequest, QuizResponse
from app.services.llm_service import LLMConfigurationError, llm_service

router = APIRouter(prefix="/api")


@router.post("/quizzes/generate", response_model=QuizResponse)
async def generate_quiz(payload: QuizRequest):
    try:
        quiz_data = await llm_service.generate_quiz(payload.material, payload.question_count)
        return QuizResponse.model_validate(quiz_data)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - real API failure handling
        raise HTTPException(status_code=503, detail="The quiz service is currently unavailable.") from exc
