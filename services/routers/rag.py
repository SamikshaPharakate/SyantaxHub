from fastapi import APIRouter, HTTPException
from models.schemas import RAGQueryRequest, CodeIndexRequest, CodeAnalysisRequest, AIResponse
from core.rag_engine import rag_engine

router = APIRouter(prefix="/api/v1/rag", tags=["RAG & Analysis Services"])

@router.post("/query", response_model=AIResponse)
async def query_rag(payload: RAGQueryRequest):
    try:
        result = rag_engine.query(
            user_query=payload.query,
            collection_name=payload.collection_name or "official_docs",
            top_k=payload.top_k or 3
        )
        return AIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-code", response_model=AIResponse)
async def analyze_code(payload: CodeAnalysisRequest):
    try:
        result = rag_engine.analyze_code(
            code=payload.code,
            language=payload.language,
            technology=payload.technology or "",
            version=payload.version or ""
        )
        return AIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed-docs", response_model=AIResponse)
async def seed_official_documentation():
    try:
        result = rag_engine.seed_official_docs()
        return AIResponse(success=True, data=result, message="Official documentation (Java, React, JS, Python) successfully seeded and indexed in ChromaDB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index-code", response_model=AIResponse)
async def index_code(payload: CodeIndexRequest):
    try:
        result = rag_engine.index_code_snippet(
            snippet_id=payload.id,
            title=payload.title,
            language=payload.language,
            code=payload.code,
            description=payload.description or ""
        )
        return AIResponse(success=True, data=result, message="Code snippet successfully indexed into vector database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
