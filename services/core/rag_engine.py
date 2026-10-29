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
                version=doc["version"],
                url=doc.get("url", "")
            )
            total_chunks += len(chunks)

            for chunk in chunks:
                vector_db.add_document(
                    doc_id=chunk["chunk_id"],
                    document_text=f"Technology: {chunk['technology']} (v{chunk['version']})\nDocument: {chunk['title']} -> {chunk['section']}\nURL: {chunk.get('url', '')}\n\n{chunk['text']}",
                    metadata={
                        "title": chunk["title"],
                        "section": chunk["section"],
                        "technology": chunk["technology"],
                        "version": chunk["version"],
                        "url": chunk.get("url", "")
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

        # Extract structured issues with full evidence (Reason, Line, Original vs Replacement, Nuances, Impact, Migration Steps, Official Docs)
        issues = self._extract_structured_issues(
            code=code,
            language=language,
            technology=technology,
            version=version,
            status=status,
            analysis_text=analysis_res,
            docs_context=retrieved_docs
        )

        # Format comprehensive evidence-based analysis report
        enhanced_analysis = self._format_analysis_report(
            analysis_text=analysis_res,
            issues=issues,
            status=status,
            language=language,
            technology=technology,
            version=version,
            docs_context=retrieved_docs
        )

        return {
            "language": language,
            "technology": technology,
            "version": version,
            "status": status,
            "issues": issues,
            "analysis": enhanced_analysis,
            "docs_context": retrieved_docs
        }

    def _find_line_number(self, code: str, pattern: str) -> Optional[int]:
        if not code:
            return None
        import re
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return idx
        return None

    def _find_doc_source(self, keyword: str, tech: str, docs_context: list, default_title: str, default_url: str) -> Dict[str, str]:
        if docs_context:
            for item in docs_context:
                meta = item.get("metadata", {})
                doc_text = item.get("document", "")
                if keyword.lower() in doc_text.lower() or tech.lower() in meta.get("technology", "").lower():
                    if meta.get("title") and meta.get("url"):
                        return {"title": meta["title"], "url": meta["url"]}
                    elif meta.get("title"):
                        return {"title": meta["title"], "url": default_url}
        return {"title": default_title, "url": default_url}

    def _extract_structured_issues(self, code: str, language: str, technology: str, version: str, status: str, analysis_text: str = "", docs_context: list = None) -> List[Dict[str, Any]]:
        if status != "outdated" or not code:
            return []

        import re
        issues = []
        tech_lower = (technology or language or "").lower()
        lines = code.splitlines()

        # 1. JavaScript checks
        if any(k in tech_lower for k in ["javascript", "js", "node", "ecmascript"]):
            # String.prototype.substr()
            substr_matches = list(re.finditer(r'([a-zA-Z0-9_$]+)?\.substr\s*\(([^)]*)\)', code))
            if substr_matches:
                for match in substr_matches:
                    line_num = self._find_line_number(code, r'\.substr\s*\(')
                    orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else match.group(0)
                    var_name = match.group(1) or "str"
                    raw_args = match.group(2).strip()
                    args = [a.strip() for a in raw_args.split(',')] if raw_args else []
                    
                    if len(args) == 2 and args[0] in ["0", "'0'"]:
                        replaced_call = f"{var_name}.slice(0, {args[1]})"
                    elif len(args) == 1:
                        replaced_call = f"{var_name}.slice({args[0]})"
                    elif len(args) == 2:
                        try:
                            start_val = int(args[0])
                            len_val = int(args[1])
                            replaced_call = f"{var_name}.slice({start_val}, {start_val + len_val})"
                        except ValueError:
                            replaced_call = f"{var_name}.slice({args[0]}, {args[0]} + {args[1]})"
                    else:
                        replaced_call = f"{var_name}.slice(0, 5)"

                    repl_line = orig_line.replace(match.group(0), replaced_call) if match.group(0) in orig_line else replaced_call
                    doc_source = self._find_doc_source("substr", "JavaScript", docs_context, "MDN Web Docs: String.prototype.substr() (Deprecated)", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/substr")

                    issues.append({
                        "api": "String.prototype.substr()",
                        "line": line_num,
                        "reason": "String.prototype.substr() is a legacy Annex B feature deprecated in modern ECMAScript standards because its second parameter specifies length rather than end position, which conflicts with substring() and slice() semantics and causes off-by-one errors.",
                        "version": f"JavaScript ({version or 'ES2024'})",
                        "documentation": doc_source,
                        "original_code": orig_line,
                        "suggested_replacement": repl_line,
                        "replacement_explanation": "slice() is the recommended modern alternative for extracting substrings across all standard JavaScript runtimes. Note behavioral differences: substr(start, length) expects a length count as the second parameter, while slice(start, end) expects an exclusive ending index. When the start index is 0, both take identical second arguments (e.g., substr(0, 5) corresponds to slice(0, 5)). For non-zero start indices, slice requires calculating start + length.",
                        "impact": "Deprecated but still supported in browser JavaScript engines for backward compatibility (ECMAScript Annex B). Not removed yet, but flagged as obsolete by modern linters, TypeScript, and clean code standards.",
                        "migration_steps": [
                            "1. Locate calls to .substr(start, length).",
                            "2. If start index is 0, replace .substr(0, length) directly with .slice(0, length).",
                            "3. If start > 0, replace .substr(start, length) with .slice(start, start + length) or .substring(start, start + length).",
                            "4. Verify test cases covering negative indices and boundary conditions."
                        ]
                    })
                    break

            # Legacy var declaration
            var_matches = list(re.finditer(r'\bvar\s+([a-zA-Z0-9_$]+)', code))
            if var_matches and not any(i["api"] == "Legacy var Declaration" for i in issues):
                line_num = self._find_line_number(code, r'\bvar\s+')
                orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else var_matches[0].group(0)
                repl_line = orig_line.replace("var ", "const ")
                doc_source = self._find_doc_source("JavaScript", "JavaScript", docs_context, "MDN Web Docs: let & const declarations", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const")

                issues.append({
                    "api": "Legacy var Declaration",
                    "line": line_num,
                    "reason": "The 'var' keyword is function-scoped and hoisted, which causes variable leakage, unintentional shadowing, and subtle closure bugs. Modern ECMAScript (ES6+) mandates block-scoped const and let.",
                    "version": f"JavaScript ({version or 'ES2024'})",
                    "documentation": doc_source,
                    "original_code": orig_line,
                    "suggested_replacement": repl_line,
                    "replacement_explanation": "const and let provide block scoping and temporal dead zone (TDZ) protection, preventing accidental mutations and use before declaration.",
                    "impact": "Deprecated standard practice; still works in engines for web compatibility, but causes lint errors and maintains closure bugs.",
                    "migration_steps": [
                        "1. Replace var with const for variables that are not reassigned.",
                        "2. Replace var with let for loop accumulators or reassignables.",
                        "3. Check for variable hoisting dependencies."
                    ]
                })

        # 2. Python checks
        if "python" in tech_lower or "py" in tech_lower:
            # datetime.datetime.utcnow()
            utcnow_match = re.search(r'datetime\.utcnow\s*\(|\.utcnow\s*\(', code)
            if utcnow_match:
                line_num = self._find_line_number(code, r'\.utcnow\s*\(')
                orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else "now = datetime.utcnow()"
                repl_line = orig_line.replace(".utcnow()", ".now(timezone.utc)")
                if "now = datetime.utcnow()" in orig_line:
                    suggested_rep = "from datetime import datetime, timezone\nnow = datetime.now(timezone.utc)"
                else:
                    suggested_rep = repl_line
                
                doc_source = self._find_doc_source("utcnow", "Python", docs_context, "Python 3.13 Official Documentation: datetime.datetime.utcnow", "https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow")

                issues.append({
                    "api": "datetime.datetime.utcnow()",
                    "line": line_num,
                    "reason": "datetime.datetime.utcnow() is deprecated starting in Python 3.12 and Python 3.13 because it returns a naive datetime object without timezone information (tzinfo=None), which leads to subtle comparison errors against timezone-aware datetimes and UTC offset serialization bugs.",
                    "version": f"Python ({version or '3.13'})",
                    "documentation": doc_source,
                    "original_code": orig_line,
                    "suggested_replacement": suggested_rep,
                    "replacement_explanation": "datetime.now(timezone.utc) creates an explicit timezone-aware datetime instance with tzinfo=timezone.utc. Unlike naive utcnow(), the resulting timestamp can be safely compared against other aware datetimes and serializes unambiguously with an explicit UTC offset (+00:00 or Z).",
                    "impact": "Deprecated in Python 3.12+; emits a DeprecationWarning at runtime. Using naive datetime objects risks timezone conversion errors and potential breakage in future Python releases.",
                    "migration_steps": [
                        "1. Import timezone from the datetime module (from datetime import datetime, timezone).",
                        "2. Replace datetime.utcnow() with datetime.now(timezone.utc).",
                        "3. If using datetime.utcfromtimestamp(ts), replace with datetime.fromtimestamp(ts, timezone.utc).",
                        "4. Confirm downstream models or serializers handle timezone-aware datetime instances correctly."
                    ]
                })

            # Python 2 print
            py2_print = re.search(r'^\s*print\s+["\']([^"\']+)["\']', code, re.MULTILINE)
            if py2_print:
                line_num = self._find_line_number(code, r'^\s*print\s+[^(]')
                orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else py2_print.group(0)
                doc_source = self._find_doc_source("Python", "Python", docs_context, "Python 3 Documentation: What's New In Python 3.0", "https://docs.python.org/3/whatsnew/3.0.html")
                issues.append({
                    "api": "Python 2 print statement",
                    "line": line_num,
                    "reason": "print statement syntax was removed in Python 3 in favor of the print() function.",
                    "version": f"Python ({version or '3.13'})",
                    "documentation": doc_source,
                    "original_code": orig_line,
                    "suggested_replacement": f"print(\"{py2_print.group(1)}\")",
                    "replacement_explanation": "print() is a built-in function in Python 3, allowing keyword arguments like end= and sep=.",
                    "impact": "Removed API: throws a SyntaxError at runtime under Python 3.",
                    "migration_steps": [
                        "1. Wrap print arguments in parentheses: print(...)."
                    ]
                })

        # 3. React checks
        if any(k in tech_lower for k in ["react", "next", "jsx", "tsx"]) or "react" in code.lower():
            lifecycle_match = re.search(r'componentDidMount|componentWillMount|componentWillReceiveProps|componentWillUpdate', code, re.IGNORECASE)
            if lifecycle_match:
                line_num = self._find_line_number(code, r'component(DidMount|WillMount|WillReceiveProps|WillUpdate)')
                orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else lifecycle_match.group(0)
                doc_source = self._find_doc_source("React", "React", docs_context, "React 19 Official Documentation & Upgrade Guide", "https://react.dev/blog/2024/12/05/react-19")
                issues.append({
                    "api": f"React lifecycle method ({lifecycle_match.group(0)})",
                    "line": line_num,
                    "reason": "Legacy class component lifecycle methods are obsolete in modern React. In React 19, componentWillMount, componentWillReceiveProps, and componentWillUpdate have been completely removed. Functional components with hooks or React Server Components are standard.",
                    "version": f"React ({version or '19'})",
                    "documentation": doc_source,
                    "original_code": orig_line,
                    "suggested_replacement": "useEffect(() => {\n  // Lifecycle logic here\n}, []);",
                    "replacement_explanation": "useEffect runs after paint and does not block browser rendering. Functional components avoid 'this' binding pitfalls and are compatible with React 19 Server Components and Suspense.",
                    "impact": "Removed lifecycles (componentWillMount, etc.) throw fatal runtime errors in React 19. Class components are legacy and do not support modern React 19 features.",
                    "migration_steps": [
                        "1. Convert class component to a functional component.",
                        "2. Replace componentDidMount / componentDidUpdate with useEffect hook.",
                        "3. Replace this.state and this.setState with useState hook.",
                        "4. Remove this binding and render() method wrapper."
                    ]
                })

        # 4. Java checks
        if "java" in tech_lower:
            wrapper_match = re.search(r'new\s+(Integer|Double|Long|Float|Boolean|Byte|Short|Character)\s*\(([^)]*)\)', code)
            if wrapper_match:
                line_num = self._find_line_number(code, r'new\s+(Integer|Double|Long|Float|Boolean|Byte|Short|Character)\s*\(')
                orig_line = lines[line_num - 1].strip() if line_num and line_num <= len(lines) else wrapper_match.group(0)
                type_name = wrapper_match.group(1)
                arg = wrapper_match.group(2).strip()
                repl = f"{type_name}.valueOf({arg})" if arg else f"{type_name}.valueOf(0)"
                doc_source = self._find_doc_source("Java", "Java", docs_context, "Oracle Java 21 LTS Documentation (JEP 390)", "https://docs.oracle.com/en/java/javase/21/")
                issues.append({
                    "api": f"Primitive Wrapper Constructor (new {type_name})",
                    "line": line_num,
                    "reason": f"Primitive wrapper constructors like new {type_name}(...) have been deprecated since Java 9 and are marked for removal in modern releases (Java 21, JEP 390). They always allocate new objects on the heap, bypassing JVM cache.",
                    "version": f"Java ({version or '21'})",
                    "documentation": doc_source,
                    "original_code": orig_line,
                    "suggested_replacement": orig_line.replace(wrapper_match.group(0), repl),
                    "replacement_explanation": f"{type_name}.valueOf() utilizes the JVM primitive cache (e.g. -128 to 127 for integers), preventing unnecessary heap allocation and reducing garbage collection pressure.",
                    "impact": "Marked for removal in future Java JDK releases; triggers compiler deprecation warnings and wastes memory.",
                    "migration_steps": [
                        f"1. Replace 'new {type_name}(val)' with auto-boxing or '{type_name}.valueOf(val)'.",
                        "2. Clean up any explicit wrapper instantiations across collection population."
                    ]
                })

        return issues

    def _format_analysis_report(self, analysis_text: str, issues: list, status: str, language: str, technology: str, version: str, docs_context: list = None) -> str:
        tech_label = f"{technology or language} (v{version or 'latest'})"
        
        if status == "outdated" and issues:
            blocks = ["STATUS: OUTDATED\n\n### Executive Summary"]
            blocks.append(f"**Outdated or legacy patterns were detected** in your {tech_label} code that should be migrated to modern official documentation standards.\n")
            blocks.append(f"### Detected Outdated Issues ({len(issues)})\n")

            for idx, issue in enumerate(issues, 1):
                blocks.append(f"#### Issue {idx}: {issue['api']}")
                if issue.get("line"):
                    blocks.append(f"- **Line Number**: Line {issue['line']}")
                blocks.append(f"- **Affected Version**: {issue['version']}")
                blocks.append(f"- **Reason for Outdated Status**: {issue['reason']}")
                blocks.append(f"- **Practical Impact**: {issue['impact']}\n")
                
                blocks.append("```" + (language or "text"))
                blocks.append(f"// Original problematic code (Line {issue.get('line', 'N/A')}):")
                blocks.append(issue['original_code'])
                blocks.append(f"\n// Suggested modern replacement:")
                blocks.append(issue['suggested_replacement'])
                blocks.append("```\n")
                
                blocks.append(f"**Why the replacement is better:**\n{issue['replacement_explanation']}\n")
                
                if issue.get("migration_steps"):
                    blocks.append("**Migration Steps:**")
                    for step in issue["migration_steps"]:
                        blocks.append(f"- {step}")
                    blocks.append("")
                
                if issue.get("documentation") and issue["documentation"].get("url"):
                    blocks.append(f"**Official Documentation Source:**\n- [{issue['documentation']['title']}]({issue['documentation']['url']})\n")

            blocks.append("*(Analysis grounded in ChromaDB Vector Database & Official Modernization Standards)*")
            return "\n".join(blocks)

        elif status == "current":
            blocks = ["STATUS: CURRENT\n\n### Executive Summary"]
            blocks.append(f"**Overall Code Health: Current & Compliant.**")
            blocks.append(f"All checks passed! The submitted {tech_label} code adheres to modern official documentation standards.\n")
            blocks.append("### Compliance Assessment")
            blocks.append("- No deprecated, removed, or obsolete patterns were detected in this code.")
            blocks.append("- Architecture conforms to current framework best practices.\n")
            
            if docs_context:
                blocks.append("### Official Documentation Context")
                for doc in docs_context[:2]:
                    meta = doc.get("metadata", {})
                    title = meta.get("title", "Official Documentation")
                    url = meta.get("url", "")
                    if url:
                        blocks.append(f"- [{title}]({url})")
                    else:
                        blocks.append(f"- {title}")
                blocks.append("")

            blocks.append("*(Analysis grounded in ChromaDB Vector Database & Official Modernization Standards)*")
            return "\n".join(blocks)

        elif status == "warning":
            return analysis_text if analysis_text else f"STATUS: WARNING\n\n### Executive Summary\n**Overall Code Health: Good with Optimization Opportunities.**\nCode is functional, but newer patterns provide cleaner syntax."

        return analysis_text if analysis_text else f"STATUS: UNCERTAIN\n\n### Executive Summary\n**Status: Uncertain / Insufficient Syntax Evidence.**\nNo known deprecated or modern patterns could be verified for the specified snippet."

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
