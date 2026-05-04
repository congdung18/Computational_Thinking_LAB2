from fastapi import APIRouter, Depends, Request
from core.security import verify_firebase_token
from services.history_service import get_user_history

router = APIRouter()


@router.get("/history")
async def get_history(request: Request, user_info: dict = Depends(verify_firebase_token)):
    db = request.app.state.db
    history = get_user_history(db, user_info)
    return {"history": history}
