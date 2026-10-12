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
Provide a detailed structured analysis.
Start your response with an exact status tag line:
STATUS: [CURRENT | WARNING | OUTDATED]
- Use STATUS: CURRENT if the code uses modern, up-to-date conventions and has no obsolete/deprecated patterns.
- Use STATUS: WARNING if the code is functional and largely modern, but has minor optimization, performance, or styling suggestions.
- Use STATUS: OUTDATED only if the code contains deprecated APIs, obsolete lifecycle methods, or patterns marked as legacy in modern versions.

Followed by:
1. Executive summary of code health and compliance.
2. List of detected issues (or state clearly "No deprecated or outdated patterns detected").
3. Recommended replacement code with modern syntax (if applicable).
4. Step-by-step refactoring advice.
"""

        system_instruction = "You are SyntaxHub AI, a world-class code architect and static analysis expert."
        analysis_res = llm_provider.generate_response(prompt=prompt, system_instruction=system_instruction)

        # Determine status dynamically from the analysis content
        status = self._determine_status(analysis_res)

        return {
            "language": language,
            "technology": technology,
            "version": version,
            "analysis": analysis_res,
            "status": status,
            "docs_context": retrieved_docs
        }

    def _determine_status(self, analysis_text: str) -> str:
        """
        Infer code health status from the LLM analysis response.
        Returns 'outdated', 'warning', or 'current'.
        """
        if not analysis_text or not isinstance(analysis_text, str):
            return "current"

        import re

        # 1. Check for explicit STATUS tag first
        status_match = re.search(r'\bSTATUS:\s*(CURRENT|WARNING|OUTDATED|DEPRECATED)\b', analysis_text, re.IGNORECASE)
        if status_match:
            tag = status_match.group(1).lower()
            if tag == "deprecated":
                return "outdated"
            return tag

        text_lower = analysis_text.lower()

        # 2. Check for strong healthy/current declarations
        strong_current_phrases = [
            "no issues detected",
            "no issues found",
            "no deprecated",
            "no outdated",
            "not deprecated",
            "not outdated",
            "code is up to date",
            "up to date with current standards",
            "follows modern patterns",
            "follows best practices",
            "all checks passed",
            "0 issues",
            "clean code",
            "well-structured and compliant"
        ]
        has_strong_current = any(phrase in text_lower for phrase in strong_current_phrases)

        # 3. Strip negated and informational phrases so "no deprecated" does not trigger "deprecated"
        sanitized_text = text_lower
        negation_patterns = [
            r"no\s+(deprecated|outdated|issues|anti-patterns|warnings|legacy|problems)",
            r"not\s+(deprecated|outdated|legacy)",
            r"without\s+(deprecated|outdated|issues)",
            r"free\s+of\s+(deprecated|outdated)",
            r"scanned\s+against\s+(known\s+)?(deprecated|outdated)",
            r"against\s+(known\s+)?(deprecated|outdated)",
            r"zero\s+(deprecated|outdated|issues)",
            r"0\s+(deprecated|outdated|issues)"
        ]
        for pattern in negation_patterns:
            sanitized_text = re.sub(pattern, " ", sanitized_text)

        # Strong outdated signals (only when not negated)
        outdated_keywords = [
            "deprecated", "outdated", "obsolete", "end-of-life",
            "no longer supported", "removed in", "removed from",
            "security risk", "security vulnerabilit", "critical issue",
            "breaking change", "must migrate", "must upgrade",
            "severely outdated", "not recommended"
        ]
        # Moderate warning signals
        warning_keywords = [
            "consider updating", "consider upgrading", "should migrate",
            "recommendation", "performance bottleneck", "could be improved",
            "minor issue", "best practice", "anti-pattern", "code smell",
            "refactor", "improvement suggested", "warning"
        ]
        # Positive signals indicating current/healthy code
        current_keywords = [
            "up to date", "up-to-date", "follows best practices",
            "well-structured", "modern pattern", "current standard",
            "compliant", "clean code", "healthy", "efficient"
        ]

        outdated_score = sum(1 for kw in outdated_keywords if kw in sanitized_text)
        warning_score = sum(1 for kw in warning_keywords if kw in sanitized_text)
        current_score = sum(1 for kw in current_keywords if kw in sanitized_text)
        if has_strong_current:
            current_score += 4

        if outdated_score >= 2 and outdated_score > current_score:
            return "outdated"
        elif current_score >= outdated_score and (current_score > warning_score or outdated_score == 0):
            return "current"
        elif warning_score >= 1 or outdated_score >= 1:
            return "warning"
        else:
            return "current"

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

    def index_code_snippet(self, snippet_id: str, title: str, language: str, code: str, description: str = "") -> Dict[str, Any]:
        document_text = f"Title: {title}\nLanguage: {language}\nDescription: {description}\n\nCode:\n```{language}\n{code}\n```"
        metadata = {
            "title": title,
            "language": language,
            "description": description
        }
        return vector_db.add_document(
            doc_id=snippet_id,
            document_text=document_text,
            metadata=metadata,
            collection_name="code_snippets"
        )

    def get_stats(self) -> Dict[str, Any]:
        return vector_db.get_stats()

rag_engine = RAGEngine()
