from fastapi import APIRouter, HTTPException

from app.schemas import SummaryRequest, SummaryResponse
from app.services.llm_service import LLMConfigurationError, llm_service

router = APIRouter(prefix="/api")


@router.post("/summaries/generate", response_model=SummaryResponse)
async def summarize_notes(payload: SummaryRequest):
    try:
        summary = await llm_service.summarize_text(payload.text, payload.style)
        return summary
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - real API failure handling
        raise HTTPException(status_code=503, detail="The summary service is currently unavailable.") from exc
