from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language prompt or query")
    collection_name: Optional[str] = Field("official_docs", description="ChromaDB collection to search")
    top_k: Optional[int] = Field(3, description="Number of context snippets to retrieve")

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: str = Field("javascript", description="Programming language (javascript, python, java, react)")
    technology: Optional[str] = Field("", description="Framework or runtime (React, Spring, Next.js)")
    version: Optional[str] = Field("", description="Target version (e.g. 19, 21, 3.13)")

class CodeIndexRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the snippet")
    title: str = Field(..., description="Snippet title")
    language: str = Field(..., description="Programming language")
    code: str = Field(..., description="Code contents")
    description: Optional[str] = ""

class CodeExplainRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: Optional[str] = Field("javascript", description="Programming language")
    context: Optional[str] = Field("", description="Optional developer context")

class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    collection_name: Optional[str] = Field("official_docs", description="Chroma collection name")
    n_results: Optional[int] = Field(5, description="Number of results")

class AIResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None
