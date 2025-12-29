# api/main.py

from fastapi import FastAPI, UploadFile, File, Depends
from typing import List
import shutil
import os
import uuid

from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    QueryRequest,
    QueryResponse,
    UploadResponse,
    ClearResponse,
    HealthResponse,
)
from api.deps import get_assistant
from backend.assistant import MimirAssistant

# --------------------------------------------------
# APP INIT (MUST BE FIRST)
# --------------------------------------------------

app = FastAPI(
    title="Mimir API",
    description="Multimodal, Persona-Adaptive RAG Assistant",
    version="1.0.0",
)

# --------------------------------------------------
# CORS (AFTER app exists)
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# FILE STORAGE
# --------------------------------------------------

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

@app.post("/files/upload", response_model=UploadResponse)
def upload_files(
    files: List[UploadFile] = File(...),
    assistant: MimirAssistant = Depends(get_assistant),
):
    saved_paths = []

    for file in files:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_paths.append(file_path)

    assistant.ingest_files(saved_paths)

    return {
        "message": "Files uploaded and indexed successfully.",
        "files_loaded": len(saved_paths),
    }

# --------------------------------------------------
# CLEAR FILES
# --------------------------------------------------

@app.post("/files/clear", response_model=ClearResponse)
def clear_files(
    assistant: MimirAssistant = Depends(get_assistant),
):
    assistant.clear_files()
    return {"message": "Uploaded files cleared for this session."}

# --------------------------------------------------
# QUERY
# --------------------------------------------------

@app.post("/query", response_model=QueryResponse)
def query_mimir(
    payload: QueryRequest,
    assistant: MimirAssistant = Depends(get_assistant),
):
    return assistant.query(
        text=payload.query,
        persona=payload.persona,
        mode=payload.mode,
    )
