import os
import json
from typing import List, Dict, Any, Optional
from backend.config import DATA_DIR, SAMPLE_MATERIALS_DIR, UPLOADS_DIR
from backend.document_processor import DocumentProcessor, DocumentChunk
from backend.rag_engine import rag_engine
from backend.database import db

class StorageManager:
    """
    Manages document storage, chunk persistence, SQLite database synchronization,
    and preloaded curriculum materials.
    """

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[DocumentChunk] = []
        self.metadata_file = os.path.join(DATA_DIR, "documents_metadata.json")

    def initialize_system(self):
        """
        Preloads sample materials on first run, synchronizes SQLite database,
        and builds RAG vector index.
        """
        # Load sample materials
        if os.path.exists(SAMPLE_MATERIALS_DIR):
            for file_name in os.listdir(SAMPLE_MATERIALS_DIR):
                file_path = os.path.join(SAMPLE_MATERIALS_DIR, file_name)
                if os.path.isfile(file_path):
                    self.index_file(file_path, is_sample=True)

        # Also load any previously uploaded files
        if os.path.exists(UPLOADS_DIR):
            for file_name in os.listdir(UPLOADS_DIR):
                file_path = os.path.join(UPLOADS_DIR, file_name)
                if os.path.isfile(file_path):
                    self.index_file(file_path, is_sample=False)

        # Refresh RAG vector index
        rag_engine.set_chunks(self.chunks)

    def index_file(self, file_path: str, is_sample: bool = False) -> Dict[str, Any]:
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(file_path)

        # Process and chunk
        new_chunks = DocumentProcessor.process_file(file_path, doc_name=file_name)
        if not new_chunks:
            return {"error": "Could not extract readable text from document"}

        doc_id = new_chunks[0].doc_id
        # Remove any previous chunks for this doc in memory
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id] + new_chunks

        # Record document metadata
        topics_covered = list(set(c.topic for c in new_chunks))
        doc_meta = {
            "doc_id": doc_id,
            "file_name": file_name,
            "file_path": file_path,
            "file_type": ext.replace(".", "").upper(),
            "file_size_kb": round(file_size / 1024, 1),
            "chunk_count": len(new_chunks),
            "topics": topics_covered,
            "is_sample": is_sample
        }
        self.documents[doc_id] = doc_meta

        # Persist to SQLite relational database
        try:
            db.save_document(doc_meta, new_chunks)
        except Exception as e:
            print(f"Warning: SQLite persistence error for {file_name}: {e}")

        # Update RAG vector index
        rag_engine.set_chunks(self.chunks)
        self.save_metadata()

        return doc_meta

    def save_metadata(self):
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Warning: could not save metadata: {e}")

    def get_all_documents(self) -> List[Dict[str, Any]]:
        # Prefer SQLite records if available
        try:
            db_docs = db.get_all_documents()
            if db_docs:
                return db_docs
        except Exception:
            pass
        return list(self.documents.values())

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        try:
            db_chunks = db.get_document_chunks(doc_id)
            if db_chunks:
                return db_chunks
        except Exception:
            pass
        return [c.to_dict() for c in self.chunks if c.doc_id == doc_id]

    def refresh_for_active_course(self, course_id: str, sample_files: List[str]):
        """
        Refreshes chunks and ensures all sample materials for the course are indexed.
        """
        for file_name in sample_files:
            file_path = os.path.join(SAMPLE_MATERIALS_DIR, file_name)
            if os.path.isfile(file_path):
                # Ensure it's indexed
                matching = [d for d in self.documents.values() if d.get("file_name") == file_name]
                if not matching:
                    self.index_file(file_path, is_sample=True)

        rag_engine.set_chunks(self.chunks)

    def get_library_summary(self, course_id: Optional[str] = None) -> Dict[str, Any]:
        doc_list = self.get_all_documents()

        return {
            "total_documents": len(doc_list),
            "total_chunks": len(self.chunks),
            "supported_types": ["PDF", "PPTX", "DOCX", "TXT", "MD"],
            "documents": doc_list
        }

storage_manager = StorageManager()
