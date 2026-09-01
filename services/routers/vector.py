from fastapi import APIRouter, HTTPException
from models.schemas import VectorSearchRequest, AIResponse
from core.vector_db import vector_db

router = APIRouter(prefix="/api/v1/vector", tags=["Vector Store"])

@router.post("/search", response_model=AIResponse)
async def vector_search(payload: VectorSearchRequest):
    try:
        results = vector_db.query(
            query_text=payload.query,
            n_results=payload.n_results or 5,
            collection_name=payload.collection_name or "code_snippets"
        )
        return AIResponse(success=True, data={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
