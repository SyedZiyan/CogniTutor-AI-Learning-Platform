import os
import shutil
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import settings, UPLOADS_DIR, FRONTEND_DIR
from backend.storage import storage_manager
from backend.rag_engine import rag_engine
from backend.tutor_engine import tutor_engine
from backend.quiz_engine import quiz_engine
from backend.competency_engine import competency_engine
from backend.roadmap_engine import roadmap_engine
from backend.gamification import gamification_engine
from backend.knowledge_graph import knowledge_graph_engine
from backend.viva_engine import socratic_viva_engine

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Intelligent AI Learning Platform with RAG Tutor, Competency Engine, Adaptive Quizzes & Dynamic Roadmap"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class TutorQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4

class DoubtSolverRequest(BaseModel):
    topic_or_question: str

class EvaluateMCQRequest(BaseModel):
    question_id: str
    selected_option_index: int
    current_streak: Optional[int] = 0
    current_difficulty: Optional[str] = "medium"

class EvaluateShortAnswerRequest(BaseModel):
    question_id: str
    student_answer: str

class VivaStartRequest(BaseModel):
    topic: str
    student_name: Optional[str] = "Scholar"

class VivaRespondRequest(BaseModel):
    session_id: str
    student_transcript: str

class SettingsUpdateRequest(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    llm_provider: Optional[str] = "local"
    ollama_endpoint: Optional[str] = None

# Initialize documents & vector engine on module load and startup
storage_manager.initialize_system()

@app.on_event("startup")
async def startup_event():
    storage_manager.initialize_system()
    print(f"CogniTutor initialized. Indexed {len(storage_manager.chunks)} chunks across {len(storage_manager.documents)} documents.")

# 1. Platform Status & Library
@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "app_name": settings.app_name,
        "version": settings.version,
        "total_documents": len(storage_manager.documents),
        "total_chunks": len(storage_manager.chunks),
        "active_llm": settings.llm_provider
    }

@app.get("/api/documents")
async def get_documents():
    return storage_manager.get_library_summary()

@app.get("/api/documents/{doc_id}/chunks")
async def get_document_chunks(doc_id: str):
    chunks = storage_manager.get_document_chunks(doc_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document chunks not found")
    return {"doc_id": doc_id, "total_chunks": len(chunks), "chunks": chunks}

# 2. Document Upload Endpoint (PDF, PPTX, DOCX, TXT)
@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    allowed_exts = [".pdf", ".pptx", ".ppt", ".docx", ".doc", ".txt", ".md"]

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Supported: {', '.join(allowed_exts)}")

    dest_path = os.path.join(UPLOADS_DIR, filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process and index file
    doc_meta = storage_manager.index_file(dest_path, is_sample=False)
    gamification_engine.add_xp(50, f"Uploaded document: {filename}")
    gamification_engine.unlock_badge("b_first_upload")

    return {
        "message": f"Successfully processed and indexed '{filename}'",
        "document": doc_meta,
        "xp_awarded": 50
    }

# 3. RAG AI Tutor Query
@app.post("/api/tutor/chat")
async def tutor_chat(req: TutorQueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    response = tutor_engine.answer_query(req.query, top_k=req.top_k)
    gamification_engine.add_xp(15, "Consulted AI Tutor")
    return response

# 4. Adaptive 3-Level Doubt Solver
@app.post("/api/tutor/doubt-solver")
async def solve_doubt(req: DoubtSolverRequest):
    if not req.topic_or_question.strip():
        raise HTTPException(status_code=400, detail="Please provide a concept or topic.")

    result = tutor_engine.solve_doubt_multilevel(req.topic_or_question)
    gamification_engine.add_xp(25, "Explored Multi-Level Doubt Solver")
    gamification_engine.unlock_badge("b_deep_thinker")
    return result

# 5. Quiz Generator & Evaluators
@app.get("/api/quiz/generate")
async def generate_quiz(topic: Optional[str] = None, difficulty: Optional[str] = "adaptive"):
    return quiz_engine.generate_quiz(topic_filter=topic, difficulty=difficulty)

@app.post("/api/quiz/evaluate-mcq")
async def evaluate_mcq(req: EvaluateMCQRequest):
    result = quiz_engine.evaluate_mcq(
        question_id=req.question_id,
        selected_option_index=req.selected_option_index,
        current_streak=req.current_streak,
        current_difficulty=req.current_difficulty
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Update Competency Engine score for this topic
    competency_engine.update_score_from_assessment(
        topic=result["topic"],
        is_correct=result["is_correct"],
        difficulty=req.current_difficulty or "medium"
    )

    # Award XP
    gamification_engine.add_xp(result["xp_earned"], "Completed Quiz Question")
    gamification_engine.quizzes_completed += 1

    return result

@app.post("/api/quiz/evaluate-short")
async def evaluate_short(req: EvaluateShortAnswerRequest):
    result = quiz_engine.evaluate_short_answer(
        question_id=req.question_id,
        student_answer=req.student_answer
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    competency_engine.update_score_from_assessment(
        topic=result["topic"],
        is_correct=result["passed"],
        difficulty="medium"
    )

    gamification_engine.add_xp(result["xp_earned"], "Completed Short Answer Assessment")
    return result

# 6. Competency & Skill Gap Analysis
@app.get("/api/competency/analysis")
async def get_competency():
    return competency_engine.get_competency_analysis()

# 7. Personalized Roadmap
@app.get("/api/roadmap")
async def get_roadmap():
    return roadmap_engine.get_roadmap()

@app.post("/api/roadmap/milestone/{milestone_id}/toggle")
async def toggle_milestone(milestone_id: str):
    res = roadmap_engine.toggle_milestone(milestone_id)
    if res["completed"]:
        gamification_engine.add_xp(35, f"Completed Roadmap Milestone: {milestone_id}")
    return res

# 8. Gamification & Leaderboard
@app.get("/api/gamification")
async def get_gamification():
    return gamification_engine.get_gamification_overview()

@app.post("/api/gamification/badge/{badge_id}/unlock")
async def unlock_badge(badge_id: str):
    badge = gamification_engine.unlock_badge(badge_id)
    if not badge:
        return {"message": "Badge already unlocked or invalid"}
    return {"message": f"Badge '{badge['name']}' unlocked!", "badge": badge}

# 9. Settings
@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    if req.openai_api_key is not None:
        settings.openai_api_key = req.openai_api_key
    if req.gemini_api_key is not None:
        settings.gemini_api_key = req.gemini_api_key
    if req.llm_provider:
        settings.llm_provider = req.llm_provider
    if req.ollama_endpoint:
        settings.ollama_endpoint = req.ollama_endpoint
    return {"message": "Settings updated successfully", "provider": settings.llm_provider}

# 10. Concept Knowledge Graph (Visual Ontology)
@app.get("/api/graph")
async def get_concept_graph():
    return knowledge_graph_engine.get_graph_data()

# 11. Socratic Viva Interview Mode
@app.post("/api/viva/start")
async def start_viva_session(req: VivaStartRequest):
    return socratic_viva_engine.start_session(req.topic, req.student_name)

@app.post("/api/viva/respond")
async def respond_viva_session(req: VivaRespondRequest):
    result = socratic_viva_engine.process_response(req.session_id, req.student_transcript)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Mount static frontend directory
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "CogniTutor API is running. Frontend index.html not yet installed."}
