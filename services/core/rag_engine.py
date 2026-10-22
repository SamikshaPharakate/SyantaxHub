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

        # Determine status accurately from the analysis content and ground-truth code verification
        status = self._determine_status(
            analysis_text=analysis_res,
            code=code,
            language=language,
            technology=technology,
            version=version
        )

        return {
            "language": language,
            "technology": technology,
            "version": version,
            "analysis": analysis_res,
            "status": status,
            "docs_context": retrieved_docs
        }

    def _determine_status(self, analysis_text: str, code: str = "", language: str = "", technology: str = "", version: str = "") -> str:
        """
        Infer code health status accurately from LLM analysis response and ground-truth code verification.
        Returns 'current', 'warning', 'outdated', or 'uncertain'.
        """
        if not analysis_text or not isinstance(analysis_text, str):
            return "uncertain" if not code else "current"

        import re

        clean_analysis = analysis_text.strip()

        # 1. Check for explicit STATUS tag (exclude prompt instruction echo: [CURRENT | WARNING | OUTDATED])
        status_line_match = re.search(r'^\s*STATUS:\s*(CURRENT|WARNING|OUTDATED|DEPRECATED|UNCERTAIN)\b', clean_analysis, re.MULTILINE | re.IGNORECASE)
        if not status_line_match:
            status_line_match = re.search(r'\bSTATUS:\s*(CURRENT|WARNING|OUTDATED|DEPRECATED|UNCERTAIN)(?![\s|\]])\b', clean_analysis, re.IGNORECASE)

        explicit_status = None
        if status_line_match:
            tag = status_line_match.group(1).lower()
            explicit_status = "outdated" if tag == "deprecated" else tag

        # 2. Check for explicit positive declarations in Executive Summary / Compliance sections
        has_current_declaration = bool(re.search(
            r'(no\s+deprecated|no\s+outdated|all\s+checks\s+passed|current\s+&\s+compliant|adheres\s+to\s+modern|zero\s+issues|0\s+issues|no\s+issues\s+detected|no\s+issues\s+found)',
            clean_analysis,
            re.IGNORECASE
        ))

        # Check for explicit issues list
        has_explicit_issues = False
        issues_section_match = re.search(r'###\s*Detected Issues\s*\n([\s\S]*?)(?=\n###|\Z)', clean_analysis, re.IGNORECASE)
        if issues_section_match:
            issues_content = issues_section_match.group(1).strip()
            if re.search(r'(no\s+(deprecated|outdated|issues)|none|0\s+issues)', issues_content, re.IGNORECASE):
                has_explicit_issues = False
            elif re.search(r'-\s+\*\*', issues_content):
                has_explicit_issues = True

        # Check for explicit warnings / optimization suggestions
        has_explicit_warnings = False
        warn_section_match = re.search(r'###\s*Optimization Suggestions\s*\n([\s\S]*?)(?=\n###|\Z)', clean_analysis, re.IGNORECASE)
        if warn_section_match:
            warn_content = warn_section_match.group(1).strip()
            if re.search(r'-\s+\*\*', warn_content):
                has_explicit_warnings = True

        # 3. Ground truth verification on submitted code directly:
        code_has_deprecated = False
        code_has_warnings = False
        code_has_valid_modern = False

        if code:
            code_lower = code.lower()
            tech_lower = (technology or language or "").lower()

            # JS checks
            if any(k in tech_lower for k in ["javascript", "js", "node", "ecmascript"]):
                if re.search(r'\.substr\s*\(', code):
                    code_has_deprecated = True
                if re.search(r'\bvar\s+[a-zA-Z0-9_$]+', code) or re.search(r'\beval\s*\(', code):
                    code_has_deprecated = True
                if re.search(r'\.slice\s*\(', code) or re.search(r'\bconst\s+', code) or re.search(r'\blet\s+', code):
                    code_has_valid_modern = True
                if re.search(r'\.reduce\s*\(', code) and any(k in code_lower for k in ["category", "group", "type"]):
                    code_has_warnings = True

            # React checks
            if any(k in tech_lower for k in ["react", "next", "jsx", "tsx"]) or "react" in code_lower:
                if re.search(r'\bcomponent(didmount|willmount|didupdate|willreceiveprops)\b', code_lower):
                    code_has_deprecated = True
                if "class " in code_lower and "extends " in code_lower and ("component" in code_lower or "react.component" in code_lower):
                    code_has_deprecated = True
                if "createref(" in code_lower:
                    code_has_deprecated = True
                if "forwardref(" in code_lower and ("19" in (version or "") or not version or "latest" in (version or "")):
                    code_has_warnings = True
                if "useeffect" in code_lower and any(kw in code_lower for kw in ["fetch(", "axios", ".then("]):
                    code_has_warnings = True
                if any(hook in code_lower for hook in ["usestate", "useeffect", "usememo", "usecallback", "useref", "use("]):
                    code_has_valid_modern = True
                if re.search(r'\b(export\s+)?(default\s+)?(async\s+)?function\b', code) or "const " in code:
                    code_has_valid_modern = True

            # Java checks
            if "java" in tech_lower:
                if re.search(r'new\s+(Integer|Double|Long|Float|Boolean|Byte|Short|Character)\s*\(', code):
                    code_has_deprecated = True
                if "newfixedthreadpool" in code_lower or "newcachedthreadpool" in code_lower or re.search(r'\b(Vector|Hashtable)\b', code):
                    code_has_deprecated = True
                if re.search(r'new\s+ArrayList<[A-Za-z0-9_]+>\s*\(', code) or "synchronized" in code_lower:
                    code_has_warnings = True
                if "virtualthread" in code_lower or re.search(r'\b(var|record)\s+', code) or "list.of(" in code_lower:
                    code_has_valid_modern = True

            # Python checks
            if "python" in tech_lower or "py" in tech_lower:
                if re.search(r'^\s*print\s+[^(]', code, re.MULTILINE) or re.search(r'except\s*:', code):
                    code_has_deprecated = True
                if "typevar(" in code_lower:
                    code_has_warnings = True
                if re.search(r'(def|class)\s+[a-zA-Z0-9_]+\[', code) or re.search(r'\bf["\']', code):
                    code_has_valid_modern = True

        # 4. Resolve final status accurately:
        # Rule: Mark OUTDATED ONLY when there is reliable evidence that the submitted code uses deprecated/obsolete API.
        if code_has_deprecated:
            return "outdated"

        # If explicit status is given:
        if explicit_status == "outdated":
            # Guard against false positives: if the code has NO deprecated syntax, do not mark outdated!
            if (has_current_declaration or not has_explicit_issues) and not code_has_deprecated:
                return "warning" if (code_has_warnings or has_explicit_warnings) else "current"
            return "outdated"

        if explicit_status == "warning":
            return "warning"

        if explicit_status == "current":
            return "current"

        if explicit_status == "uncertain":
            return "uncertain"

        # If no explicit status tag, check sections and code features:
        if has_explicit_issues:
            return "outdated"
        if has_explicit_warnings or code_has_warnings:
            return "warning"
        if has_current_declaration or code_has_valid_modern:
            return "current"

        # If code is blank or contains insufficient evidence:
        if not code or not code.strip() or len(code.strip()) < 5:
            return "uncertain"

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
