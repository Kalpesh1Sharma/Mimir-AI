# api/schemas.py

from typing import List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    persona: Optional[str] = "default"
    mode: Optional[str] = "factual"


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    metadata: Optional[dict] = None


class UploadResponse(BaseModel):
    message: str
    files_loaded: int


class ClearResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
