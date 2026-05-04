from fastapi import APIRouter, Depends, Request
from core.security import verify_firebase_token
from services.history_service import sync_user_profile

router = APIRouter()


@router.post("/auth")
async def sync_user(request: Request, user_info: dict = Depends(verify_firebase_token)):
    db = request.app.state.db
    return sync_user_profile(db, user_info)
