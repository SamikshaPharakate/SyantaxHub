import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import rag, llm, vector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="SyntaxHub AI Microservice powering Code Analysis, RAG, LLM Integration, and ChromaDB Vector Search"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(rag.router)
app.include_router(llm.router)
app.include_router(vector.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.app_name,
        "version": settings.version,
        "status": "online"
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "vector_store": "chromadb",
        "llm_provider": settings.default_provider
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
