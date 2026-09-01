import logging
from typing import Dict, Any, List
from core.vector_db import vector_db
from core.llm_provider import llm_provider
from core.doc_chunker import doc_chunker
from core.seed_docs import OFFICIAL_DOCS

logger = logging.getLogger("rag_engine")

class RAGEngine:
    def __init__(self):
        pass

    def seed_official_docs(self) -> Dict[str, Any]:
        """
        Chunks and indexes official documentation for Java, React, JavaScript, and Python into ChromaDB.
        """
        indexed_count = 0
        total_chunks = 0

        for doc in OFFICIAL_DOCS:
            chunks = doc_chunker.chunk_markdown(
                content=doc["content"],
                doc_title=doc["title"],
                tech=doc["technology"],
                version=doc["version"]
            )
            total_chunks += len(chunks)

            for chunk in chunks:
                vector_db.add_document(
                    doc_id=chunk["chunk_id"],
                    document_text=f"Technology: {chunk['technology']} (v{chunk['version']})\nDocument: {chunk['title']} -> {chunk['section']}\n\n{chunk['text']}",
                    metadata={
                        "title": chunk["title"],
                        "section": chunk["section"],
                        "technology": chunk["technology"],
                        "version": chunk["version"]
                    },
                    collection_name="official_docs"
                )
                indexed_count += 1

        logger.info(f"Seeded {indexed_count} chunks across {len(OFFICIAL_DOCS)} official document suites into ChromaDB.")
        return {
            "status": "success",
            "docs_processed": len(OFFICIAL_DOCS),
            "chunks_indexed": indexed_count,
            "collection": "official_docs"
        }

    def analyze_code(self, code: str, language: str, technology: str = "", version: str = "") -> Dict[str, Any]:
        """
        Retrieves relevant official docs context from ChromaDB and performs deep code analysis using OpenRouter LLM.
        """
        # 1. Search vector store for relevant documentation standards
        search_query = f"{technology} {language} best practices deprecated patterns migration"
        retrieved_docs = vector_db.query(query_text=search_query, n_results=3, collection_name="official_docs")
        
        # Fallback search in code_snippets collection if official_docs has no match yet
        if not retrieved_docs:
            retrieved_docs = vector_db.query(query_text=code[:200], n_results=3, collection_name="code_snippets")

        context_str = "\n\n".join([f"Source ({item['metadata'].get('technology', 'Doc')}): {item['document']}" for item in retrieved_docs]) if retrieved_docs else "Standard documentation guidelines."

        # 2. Build OpenRouter Prompt
        prompt = f"""Analyze the following {language} code snippet against modern official documentation standards for {technology or language} (v{version or 'latest'}).

CODE TO ANALYZE:
```{language}
{code}
```

OFFICIAL DOCUMENTATION CONTEXT (CHROMA DB RAG):
{context_str}

INSTRUCTIONS:
Provide a detailed structured analysis containing:
1. Executive summary of code health and compliance.
2. List of detected issues (outdated patterns, deprecated APIs, performance bottlenecks, security risks).
3. Recommended replacement code with modern syntax.
4. Step-by-step refactoring advice.
"""

        system_instruction = "You are SyntaxHub AI, a world-class code architect and static analysis expert."
        analysis_res = llm_provider.generate_response(prompt=prompt, system_instruction=system_instruction)

        return {
            "language": language,
            "technology": technology,
            "version": version,
            "analysis": analysis_res,
            "docs_context": retrieved_docs
        }

    def query(self, user_query: str, collection_name: str = "official_docs", top_k: int = 3) -> Dict[str, Any]:
        retrieved_docs = vector_db.query(query_text=user_query, n_results=top_k, collection_name=collection_name)
        
        context_blocks = []
        for i, item in enumerate(retrieved_docs, 1):
            context_blocks.append(f"--- Document Source #{i} --- [{item.get('metadata', {}).get('title', 'Doc')}]\n{item.get('document')}")

        context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant official docs retrieved."

        prompt = f"""USER QUESTION:
{user_query}

OFFICIAL DOCUMENTATION CONTEXT:
{context_str}

INSTRUCTIONS:
Answer the question accurately using the official documentation context. Cite specific versions and methods when relevant.
"""
        answer = llm_provider.generate_response(prompt=prompt, system_instruction="You are SyntaxHub Documentation Assistant.")

        return {
            "query": user_query,
            "answer": answer,
            "sources": retrieved_docs
        }

rag_engine = RAGEngine()
