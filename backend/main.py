import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load environment variables
load_dotenv()

# Verify GEMINI_API_KEY
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_api_key_here":
    print("WARNING: GEMINI_API_KEY is not set or is using the default value.")

app = FastAPI(
    title="Transportation Suggestion RAG API",
    description="API that suggests transportation based on weather and user preferences using RAG.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Firebase Admin
cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
if cred_path and os.path.exists(cred_path):
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase Admin and Firestore initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin: {e}")
        db = None
else:
    print("WARNING: FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set or file not found. Auth will fail.")
    db = None

security = HTTPBearer()

def verify_firebase_token(creds: HTTPAuthorizationCredentials = Security(security)):
    try:
        decoded_token = auth.verify_id_token(creds.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Initialize models and DB at startup
print("Initializing embeddings and Vector DB connection...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

try:
    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    print(f"Failed to load Chroma DB: {e}. Make sure to run ingest.py first.")
    retriever = None

# Initialize LLM
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
except Exception as e:
    print(f"Failed to initialize Gemini: {e}")
    llm = None

# Create Prompt Template
template = """
You are a helpful transportation assistant. Use the following context rules to recommend the best transportation method (walk, bike, motorbike, car, public transportation, etc.) based on the user's weather conditions and preferences. 

Context (Rules):
{context}

User's Input:
- Weather conditions: {weather}
- User preferences/Distance: {preferences}

Based on the rules and input, recommend the best transportation method and provide a brief explanation why. If the rules don't cover the exact scenario, make a logical recommendation.

Recommendation:
"""
prompt = ChatPromptTemplate.from_template(template)

# Request Model
class SuggestionRequest(BaseModel):
    weather: str
    preferences: str

class SuggestionResponse(BaseModel):
    suggestion: str

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@app.post("/auth")
async def sync_user(user_info: dict = Depends(verify_firebase_token)):
    if not db:
        return {"status": "Firestore not initialized"}
        
    user_id = user_info.get("uid")
    email = user_info.get("email")
    
    try:
        user_ref = db.collection("users").document(user_id)
        doc = user_ref.get()
        
        if not doc.exists:
            user_ref.set({
                "email": email,
                "created_at": firestore.SERVER_TIMESTAMP
            })
            return {"status": "New user created"}
        return {"status": "User synced"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(user_info: dict = Depends(verify_firebase_token)):
    if not db:
        return {"history": []}
        
    user_id = user_info.get("uid")
    
    try:
        docs = db.collection("users").document(user_id).collection("history")\
                 .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
                 
        history = []
        for doc in docs:
            data = doc.to_dict()
            if "timestamp" in data and data["timestamp"]:
                data["timestamp"] = data["timestamp"].isoformat()
            history.append(data)
            
        return {"history": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"history": []}

@app.post("/suggest", response_model=SuggestionResponse)
async def suggest_transportation(
    request: SuggestionRequest, 
    user_info: dict = Depends(verify_firebase_token)
):
    if not retriever or not llm:
        raise HTTPException(status_code=500, detail="RAG system is not properly initialized. Check API keys and ensure ingest.py was run.")

    try:
        # Create the RAG chain
        rag_chain = (
            {"context": retriever | format_docs, "weather": lambda x: request.weather, "preferences": lambda x: request.preferences}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Execute chain
        combined_query = f"Weather: {request.weather}. Preferences: {request.preferences}"
        response = rag_chain.invoke(combined_query)

        # Save to Firestore
        if db:
            user_id = user_info.get("uid")
            history_ref = db.collection("users").document(user_id).collection("history")
            history_ref.add({
                "weather": request.weather,
                "preferences": request.preferences,
                "suggestion": response,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

        return SuggestionResponse(suggestion=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "db_loaded": retriever is not None, "llm_loaded": llm is not None}