from fastapi import APIRouter, HTTPException

from app.schemas import ChatAgentRequest, ChatAgentResponse
from app.services.agent_service import run_agent
from app.services.llm_service import LLMConfigurationError

router = APIRouter(prefix="/api")


@router.post("/chat/agent", response_model=ChatAgentResponse)
async def agent_chat(payload: ChatAgentRequest):
    try:
        result = await run_agent(payload.message)
        return ChatAgentResponse(answer=result["answer"], tool_used=result.get("tool_used", False))
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - safety guard for runtime issues
        raise HTTPException(status_code=503, detail="The AI agent encountered an error while running your request.") from exc
