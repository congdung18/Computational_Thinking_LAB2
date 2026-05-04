from fastapi import APIRouter, Request
from services.rag_service import RagService

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    rag_service: RagService = request.app.state.rag_service
    retriever_ready = rag_service.retriever_ready() if rag_service else False
    llm_ready = rag_service.llm_ready() if rag_service else False
    return {"status": "healthy", "db_loaded": retriever_ready, "llm_loaded": llm_ready}
