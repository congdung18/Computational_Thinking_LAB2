# Transportation Suggestion RAG System

A complete Retrieval-Augmented Generation (RAG) web application that intelligently recommends the best transportation method (e.g., walking, biking, driving, or public transit) based on the user's weather conditions and travel preferences.

## 🌟 Project Architecture

The project is split into two main services, containerized using Docker:

### 1. Backend (FastAPI + LangChain + Chroma)
- **API Framework:** FastAPI
- **LLM:** Google Gemini (`gemini-2.5-flash`) via LangChain.
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`).
- **Vector Database:** ChromaDB to store and retrieve transportation context rules.
- **Database:** Firebase Firestore (for saving user profiles and chat history).
- **Authentication:** Firebase Admin SDK (token verification).
- **Port:** `8000`

### 2. Frontend (React + Vite)
- **Framework:** React powered by Vite for fast, modern web development.
- **Authentication:** Firebase JS SDK (Google & Email/Password login).
- **Styling:** Vanilla CSS for a clean, responsive user interface.
- **Web Server:** Nginx (used within the Docker container to serve the built static files).
- **Port:** `3000`

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed.
- A valid Google Gemini API Key.

### 1. Setup Environment Variables

#### Backend
Navigate to the `backend` directory and ensure your `.env` file is properly configured with your Google API Key and Firebase Service Account key:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-service-account.json
```
*(You must download `firebase-service-account.json` from your Firebase Console -> Project Settings -> Service Accounts and place it in the `backend` folder).*

#### Frontend
Navigate to the `frontend` directory and create a `.env` file with your Firebase web configuration:

```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```
*(You must also enable "Firestore Database" in your Firebase Console).*

### 2. Data Ingestion
Before querying the system, the RAG knowledge base needs to be populated with transportation rules. 

If it's your first time or if you update the rules in `backend/data/transport_rules.txt`, you need to run the ingestion script to generate the vector database (`chroma_db`). If you have Python installed locally:

```bash
cd backend
python ingest.py
cd ..
```
*(This will read `transport_rules.txt`, split the content, compute embeddings, and save the Vector DB to the `chroma_db` folder.)*

### 3. Run the Application with Docker Compose
From the root directory of the project, build and spin up the containers:

```bash
docker compose up -d --build
```

### 4. Access the Application
Once the containers are successfully running:
- **Frontend UI:** Open your browser and navigate to [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) to test the backend API interactively without Postman.

---

## 🛠️ API Reference

*Note: All core endpoints (except `/health`) now require a valid Firebase ID Token passed in the `Authorization: Bearer <token>` header.*

### Sync User Profile
- **Endpoint:** `POST http://localhost:8000/auth`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Verifies the user's Firebase token and creates a profile in Firestore if they are new. Returns `{"status": "User synced"}`.

### Get a Transportation Suggestion
- **Endpoint:** `POST http://localhost:8000/suggest`
- **Headers:** `Authorization: Bearer <token>`
- **Body (JSON):**
  ```json
  {
    "weather": "Heavy rain",
    "preferences": "I need to travel 10km and don't want to get wet."
  }
  ```
- **Response:**
  ```json
  {
    "suggestion": "Based on the heavy rain and distance, I recommend taking public transportation or a car..."
  }
  ```

### Get User Chat History
- **Endpoint:** `GET http://localhost:8000/history`
- **Headers:** `Authorization: Bearer <token>`
- **Description:** Retrieves the user's 10 most recent queries and suggestions from Firestore.

### Health Check
- **Endpoint:** `GET http://localhost:8000/health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "db_loaded": true,
    "llm_loaded": true
  }
  ```

---

## 🛑 Useful Docker Commands

- **Stop the containers:**
  ```bash
  docker compose down
  ```
- **Rebuild and start a specific service (e.g., backend):**
  ```bash
  docker compose up -d --build backend
  ```
- **View logs for a service:**
  ```bash
  docker compose logs -f backend
  ```
