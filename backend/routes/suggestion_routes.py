from fastapi import APIRouter, Depends, HTTPException, Request
from core.security import verify_firebase_token
from schemas.suggestion import SuggestionRequest, SuggestionResponse
from services.history_service import save_user_history
from services.rag_service import RagService

router = APIRouter()


@router.post("/suggest", response_model=SuggestionResponse)
async def suggest_transportation(
    request: Request,
    payload: SuggestionRequest,
    user_info: dict = Depends(verify_firebase_token),
):
    rag_service: RagService = request.app.state.rag_service
    if not rag_service or not rag_service.is_ready():
        raise HTTPException(
            status_code=500,
            detail="RAG system is not properly initialized. Check API keys and ensure ingestion was run.",
        )

    try:
        suggestion = rag_service.suggest(payload.weather, payload.preferences)
        save_user_history(
            request.app.state.db,
            user_info,
            payload.weather,
            payload.preferences,
            suggestion,
        )
        return SuggestionResponse(suggestion=suggestion)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
