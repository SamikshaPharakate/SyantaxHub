import os
import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from config import settings
from core.embeddings import embedding_service

logger = logging.getLogger("vector_db")

class VectorDBClient:
    def __init__(self):
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        logger.info(f"Initialized ChromaDB persistent client at: {settings.chroma_persist_dir}")

    def get_or_create_collection(self, name: str = "code_snippets"):
        return self.client.get_or_create_collection(name=name)

    def add_document(self, doc_id: str, document_text: str, metadata: Dict[str, Any], collection_name: str = "code_snippets"):
        collection = self.get_or_create_collection(collection_name)
        embedding = embedding_service.embed_text(document_text)
        collection.upsert(
            ids=[doc_id],
            documents=[document_text],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        return {"id": doc_id, "status": "indexed", "collection": collection_name}

    def query(self, query_text: str, n_results: int = 3, collection_name: str = "code_snippets") -> List[Dict[str, Any]]:
        collection = self.get_or_create_collection(collection_name)
        query_embedding = embedding_service.embed_text(query_text)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
                formatted_results.append({
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return formatted_results

vector_db = VectorDBClient()
