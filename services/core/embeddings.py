import logging
from typing import List

logger = logging.getLogger("embeddings")

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
            except Exception as e:
                logger.warning(f"SentenceTransformer not available: {e}. Falling back to default vectorizer.")
                self._model = "fallback"

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        if self._model != "fallback" and hasattr(self._model, "encode"):
            return self._model.encode(text).tolist()
        
        # Simple deterministic hashing fallback vector for testing without torch overhead
        import hashlib
        hash_digest = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255.0 for b in hash_digest[:384]]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in documents]

embedding_service = EmbeddingService()
