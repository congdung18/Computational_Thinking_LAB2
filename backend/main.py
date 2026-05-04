from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.firebase import init_firestore
from routes import auth_routes, health_routes, history_routes, suggestion_routes
from services.rag_service import RagService

app = FastAPI(
    title="Transportation Suggestion RAG API",
    description="API that suggests transportation based on weather and user preferences using RAG.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.db = init_firestore()
app.state.rag_service = RagService()

app.include_router(auth_routes.router)
app.include_router(history_routes.router)
app.include_router(suggestion_routes.router)
app.include_router(health_routes.router)