import os
import json
from typing import List, Dict, Any
from backend.config import DATA_DIR, SAMPLE_MATERIALS_DIR, UPLOADS_DIR
from backend.document_processor import DocumentProcessor, DocumentChunk
from backend.rag_engine import rag_engine

class StorageManager:
    """
    Manages document storage, chunk persistence, and preloaded curriculum materials.
    """

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[DocumentChunk] = []
        self.metadata_file = os.path.join(DATA_DIR, "documents_metadata.json")

    def initialize_system(self):
        """
        Preloads sample materials on first run and builds RAG vector index.
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
        # Remove any previous chunks for this doc
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
        return list(self.documents.values())

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.chunks if c.doc_id == doc_id]

    def get_library_summary(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "supported_types": ["PDF", "PPTX", "DOCX", "TXT", "MD"],
            "documents": list(self.documents.values())
        }

storage_manager = StorageManager()
