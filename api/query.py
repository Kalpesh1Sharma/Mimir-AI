from fastapi import APIRouter
from api.schemas import QueryRequest, QueryResponse
from backend.assistant import MimirAssistant

router = APIRouter()
mimir = MimirAssistant()

@router.post("/query", response_model=QueryResponse)
def query_mimir(payload: QueryRequest):
    return mimir.query(
        text=payload.query,      # ✅ mapping here
        persona=payload.persona,
        mode=payload.mode,
    )
