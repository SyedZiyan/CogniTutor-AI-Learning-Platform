import os
from pydantic import BaseModel
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
SAMPLE_MATERIALS_DIR = os.path.join(BASE_DIR, "sample_materials")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

class AppSettings(BaseModel):
    app_name: str = "CogniTutor AI Learning Platform"
    version: str = "2.0.0"
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    llm_provider: str = "local" # "local", "openai", "gemini", "ollama"
    ollama_endpoint: str = "http://localhost:11434"
    llm_model: str = "gpt-4o-mini"
    chunk_size: int = 650
    chunk_overlap: int = 120
    top_k_retrieval: int = 4

settings = AppSettings()
