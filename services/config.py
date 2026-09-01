import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SyntaxHub AI Service"
    version: str = "1.0.0"
    port: int = 8000
    host: str = "0.0.0.0"
    
    # OpenRouter API & LLM Settings
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
    site_url: str = os.getenv("SITE_URL", "https://syntaxhub.dev")
    site_name: str = os.getenv("SITE_NAME", "SyntaxHub")

    # Fallback LLM Settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    default_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openrouter")
    
    # Vector DB & Embeddings Settings
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
