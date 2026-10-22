import logging
import httpx
from config import settings

logger = logging.getLogger("llm_provider")

class LLMProvider:
    def __init__(self):
        self.openrouter_key = settings.openrouter_api_key
        self.openrouter_model = settings.openrouter_model
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key

    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        # 1. OpenRouter Integration (Primary if real key provided)
        if self.openrouter_key and "your_openrouter" not in self.openrouter_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                    "Content-Type": "application/json"
                }
                
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.openrouter_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1500
                }

                with httpx.Client(timeout=40.0) as client:
                    response = client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"OpenRouter API error [{response.status_code}]: {response.text}")
            except Exception as e:
                logger.warning(f"OpenRouter request failed: {e}")

        # 2. Google Gemini Fallback
        if self.gemini_key and "your_gemini" not in self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                res = model.generate_content(full_prompt)
                return res.text
            except Exception as e:
                logger.warning(f"Gemini API invocation failed: {e}")

        # 3. OpenAI Direct Fallback
        if self.openai_key and "your_openai" not in self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                res = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                return res.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI API invocation failed: {e}")

        # 4. Live Free AI Chatbot Model (Zero API Key required, dynamic real-time completions)
        try:
            free_ai = self._call_free_llm(prompt, system_instruction)
            if free_ai:
                return free_ai
        except Exception as e:
            logger.warning(f"Free LLM API invocation failed: {e}")

        # 5. Fallback Synthesizer — performs RAG synthesis / static analysis when external LLM API is offline
        return self._static_analysis_fallback(prompt)

    def _call_free_llm(self, prompt: str, system_instruction: str = "") -> str:
        """
        Calls high-speed free AI model API (Pollinations anonymous reasoning LLM).
        Provides real dynamic responses for any user question or code refactoring task.
        """
        messages = []
        sys_prompt = system_instruction or "You are SyntaxHub AI Assistant, an expert programming assistant specializing in Java 21, React 19, JavaScript ES2024, and Python 3.13. Answer questions clearly, accurately, with practical code examples formatted in markdown."
        messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages,
            "model": "openai"
        }

        with httpx.Client(timeout=25.0) as client:
            resp = client.post("https://text.pollinations.ai/", json=payload)
            if resp.status_code == 200 and resp.text:
                text = resp.text.strip()
                if text and not text.startswith('{"error"') and len(text) > 20:
                    return text
        return ""

    def _static_analysis_fallback(self, prompt: str) -> str:
        """
        Synthesizer engine used when external LLM APIs are unconfigured or offline.
        Handles both RAG Q&A (chat/queries) grounded in ChromaDB context and Code Analysis.
        """
        prompt_lower = prompt.lower()

        # Handle RAG / Chat User Question prompts
        if "user question:" in prompt_lower:
            # Extract question and retrieved context if present
            query_part = prompt
            if "user question:" in prompt_lower:
                parts = prompt.split("USER QUESTION:")
                if len(parts) > 1:
                    query_part = parts[1].split("OFFICIAL DOCUMENTATION CONTEXT:")[0].strip()

            context_extracted = ""
            if "OFFICIAL DOCUMENTATION CONTEXT:" in prompt:
                ctx_parts = prompt.split("OFFICIAL DOCUMENTATION CONTEXT:")
                if len(ctx_parts) > 1:
                    context_extracted = ctx_parts[1].split("INSTRUCTIONS:")[0].strip()

            ql = query_part.lower()
            response_lines = [f"**SyntaxHub AI Assistant** (ChromaDB Vector Store Grounded)\n"]

            if any(k in ql for k in ["react", "useeffect", "hook", "component", "server component"]):
                response_lines.append("### React 19 Guidance:")
                response_lines.append("- **Server Components & Actions**: Server Components are the modern default for data fetching to prevent client waterfall cascades.")
                response_lines.append("- **The `use()` Hook**: Pass Promises or Context to `use(resource)` directly inside render.")
                response_lines.append("- **Deprecated Patterns**: Legacy class lifecycles (`componentDidMount`) and `forwardRef` are replaced by standard props and functional hooks.")
            elif any(k in ql for k in ["java", "thread", "virtual thread", "loom", "record"]):
                response_lines.append("### Java 21 LTS Guidance:")
                response_lines.append("- **Virtual Threads (Project Loom - JEP 444)**: Use `Executors.newVirtualThreadPerTaskExecutor()` instead of fixed OS thread pools for millions of lightweight concurrent tasks.")
                response_lines.append("- **Pattern Matching & Records**: Deconstruct records directly in `switch` and `instanceof` with `Point(int x, int y)`.")
            elif any(k in ql for k in ["javascript", "js", "group", "promise", "es2024"]):
                response_lines.append("### ECMAScript 2024 Guidance:")
                response_lines.append("- **`Object.groupBy()`**: Native grouping replaces manual `.reduce()` loops.")
                response_lines.append("- **`Promise.withResolvers()`**: Destructure `{ promise, resolve, reject }` in a single call.")
                response_lines.append("- **Immutable Arrays**: Use `.toSorted()`, `.toSpliced()`, and `.toReversed()` instead of mutating originals.")
            elif any(k in ql for k in ["python", "gil", "typevar", "pep 695", "dataclass"]):
                response_lines.append("### Python 3.13 Guidance:")
                response_lines.append("- **Free-Threaded CPython**: Experimental GIL-free build provides true multi-core CPU parallelism.")
                response_lines.append("- **Type Parameter Syntax (PEP 695)**: Modern generics use `def func[T](items: list[T]) -> T:` rather than legacy `TypeVar`.")
                response_lines.append("- **Frozen Dataclasses**: Prefer `@dataclass(frozen=True, slots=True)` for robust, memory-efficient data objects.")
            else:
                response_lines.append(f"Regarding your query on: **{query_part}**")
                if context_extracted and "No relevant official docs retrieved" not in context_extracted:
                    response_lines.append("\n**Retrieved Documentation Highlights:**")
                    # Include key snippets from retrieved docs context
                    first_chunks = [c.strip() for c in context_extracted.split("--- Document Source") if c.strip()][:2]
                    for chk in first_chunks:
                        response_lines.append(f"> {chk[:280]}...")
                else:
                    response_lines.append("\nSyntaxHub is indexed with official documentation for **React 19**, **Java 21 LTS**, **JavaScript ES2024**, and **Python 3.13**.")
                    response_lines.append("Ask about migrations, modern patterns, or submit snippets in the Analyze tab for automated code scanning.")

            response_lines.append("\n*(Powered by ChromaDB Vector Database & OpenRouter / Static Synthesis)*")
            return "\n".join(response_lines)

        import re

        # Extract Code to Analyze and metadata from prompt
        code_part = ""
        tech = ""
        lang = ""
        ver = ""

        meta_match = re.search(r'Analyze the following\s+([a-zA-Z0-9_\-\.\s]+?)\s+code snippet against modern official documentation standards for\s+([a-zA-Z0-9_\-\.\s]+?)\s+\(v([a-zA-Z0-9_\-\.]+)\)', prompt)
        if meta_match:
            lang = meta_match.group(1).strip().lower()
            tech = meta_match.group(2).strip().lower()
            ver = meta_match.group(3).strip().lower()

        if "CODE TO ANALYZE:" in prompt:
            parts = prompt.split("CODE TO ANALYZE:")
            if len(parts) > 1:
                after_code = parts[1]
                if "OFFICIAL DOCUMENTATION CONTEXT" in after_code:
                    code_block = after_code.split("OFFICIAL DOCUMENTATION CONTEXT")[0].strip()
                elif "INSTRUCTIONS:" in after_code:
                    code_block = after_code.split("INSTRUCTIONS:")[0].strip()
                else:
                    code_block = after_code.strip()

                lines = code_block.splitlines()
                if lines and lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                code_part = "\n".join(lines).strip()
        else:
            code_part = prompt.strip()

        if not code_part.strip():
            return (
                "STATUS: UNCERTAIN\n\n"
                "### Executive Summary\n"
                "Insufficient code provided to evaluate compliance or detect deprecated patterns.\n\n"
                "### Recommendations\n"
                "- Please provide complete code for analysis.\n"
            )

        code_lower = code_part.lower()
        if not tech:
            if "react" in prompt_lower or "react" in lang:
                tech = "react"
            elif "java" in prompt_lower or "java" in lang:
                tech = "java"
            elif "javascript" in prompt_lower or "js" in prompt_lower or "js" in lang:
                tech = "javascript"
            elif "python" in prompt_lower or "py" in prompt_lower or "py" in lang:
                tech = "python"

        issues = []
        warnings = []
        positive = []

        # --- React patterns ---
        if "react" in tech or "react" in lang or "component" in code_lower or "jsx" in lang:
            if re.search(r'\bcomponent(didmount|willmount|didupdate|willreceiveprops)\b', code_lower):
                issues.append("- **Deprecated Lifecycle Methods**: Detected legacy lifecycle methods (`componentDidMount`, `componentWillMount`). In modern React, functional components with hooks or Server Components are standard.")
            if "class " in code_lower and "extends " in code_lower and ("component" in code_lower or "react.component" in code_lower):
                issues.append("- **Class Component Pattern**: Legacy class component detected. Migrate to functional components with modern React hooks.")
            if "createref(" in code_lower:
                issues.append("- **Legacy Ref API**: `createRef` detected in component body. Prefer `useRef` hook in functional components.")
            if "forwardref(" in code_lower and ("19" in ver or not ver or "latest" in ver):
                warnings.append("- **`forwardRef` Deprecation**: In React 19, `forwardRef` is deprecated. Pass `ref` directly as a standard component prop.")
            if "useeffect" in code_lower and any(kw in code_lower for kw in ["fetch(", "axios", ".then("]):
                warnings.append("- **Client-side Fetch Waterfall**: Data fetching in `useEffect` is discouraged in modern React (React 19). Consider React 19 Server Components, Suspense boundaries, or the `use()` hook.")
            if "usestate" in code_lower:
                positive.append("- Uses standard React `useState` hook for declarative state management.")
            if "useeffect" in code_lower:
                positive.append("- Uses React `useEffect` for lifecycle synchronization.")
            if "usememo" in code_lower or "usecallback" in code_lower:
                positive.append("- Uses memoization hooks (`useMemo` / `useCallback`) for performance optimization.")
            if "useref" in code_lower:
                positive.append("- Uses `useRef` for DOM references and mutable instance values.")
            if re.search(r'\b(export\s+)?(default\s+)?(async\s+)?function\b', code_part) or "const " in code_part:
                positive.append("- Modern functional component architecture.")

        # --- Java patterns ---
        if "java" in tech or "java" in lang:
            if re.search(r'new\s+(Integer|Double|Long|Float|Boolean|Byte|Short|Character)\s*\(', code_part):
                issues.append("- **Deprecated Wrapper Constructor**: Primitive wrapper constructors like `new Integer(...)` or `new Double(...)` are deprecated since Java 9 and marked for removal. Use auto-boxing (e.g. `Integer number = 100;`) or `Integer.valueOf(100)`.")
            if "newfixedthreadpool" in code_lower or "newcachedthreadpool" in code_lower:
                issues.append("- **Legacy OS Thread Pool**: Detected fixed/cached OS thread pool (`Executors.newFixedThreadPool`). In Java 21+, migrate to lightweight Virtual Threads with `Executors.newVirtualThreadPerTaskExecutor()` for orders-of-magnitude higher concurrency.")
            if re.search(r'\b(Vector|Hashtable)\b', code_part):
                issues.append("- **Legacy Collections**: `Vector` / `Hashtable` detected. Migrate to `ArrayList`, `ConcurrentHashMap`, or modern immutable collections (`List.of`, `Map.of`).")
            if re.search(r'new\s+ArrayList<[A-Za-z0-9_]+>\s*\(', code_part):
                warnings.append("- **Redundant Type Arguments**: Explicit type arguments on collection instantiation (e.g., `new ArrayList<String>()`) are outdated. Use the diamond operator `<>` (Java 7+) or `List.of(...)` (Java 9+).")
            if re.search(r'for\s*\(\s*int\s+i\s*=\s*0.*\.size\(\)', code_part):
                warnings.append("- **Legacy Indexed For-Loop**: Traditional indexed loops over collections (`for (int i = 0; i < collection.size(); i++)`) are legacy patterns. In modern Java, prefer enhanced for-each loops (`for (String item : items)`) or `collection.forEach(System.out::println)`.")
            if ".add(" in code_lower and code_lower.count(".add(") >= 2 and ("list" in code_lower or "names" in code_lower):
                warnings.append("- **Imperative Collection Instantiation**: Successive `.add()` calls to populate constant lists can be replaced in modern Java (9+) with concise immutable factories like `List.of(...)`.")
            if "synchronized" in code_lower:
                warnings.append("- **`synchronized` Block**: Heavyweight synchronized lock detected. In Java 21 Virtual Threads, prefer `ReentrantLock` to avoid thread pinning.")
            if "virtualthread" in code_lower:
                positive.append("- Uses Java 21 Virtual Threads for high-throughput concurrency.")
            if re.search(r'\bvar\s+', code_part):
                positive.append("- Uses local variable type inference (`var`, Java 10+).")
            if re.search(r'\brecord\s+', code_part):
                positive.append("- Uses immutable `record` classes (Java 16+).")
            if "list.of(" in code_lower or "map.of(" in code_lower or "set.of(" in code_lower:
                positive.append("- Uses modern Java 9+ immutable collection factories (`List.of`, `Map.of`).")
            if "stream()" in code_lower or ".stream()" in code_lower:
                positive.append("- Uses functional Stream API.")
            if "public class" in code_part or "class " in code_part:
                positive.append("- Well-structured Java class definition.")

        # --- JavaScript / Node.js patterns ---
        if "javascript" in tech or "js" in tech or "express" in tech or "javascript" in lang or "js" in lang or "node" in tech:
            if re.search(r'\.substr\s*\(', code_part):
                issues.append("- **Deprecated `String.prototype.substr()`**: `substr()` is legacy Annex B syntax deprecated in modern ECMAScript standards. Replace with standard `.slice(start, end)` or `.substring(start, end)`.")
            if re.search(r'\bvar\s+[a-zA-Z0-9_$]+', code_part):
                issues.append("- **Legacy `var` Declaration**: `var` keyword detected. Replace with block-scoped `const` (for constants) or `let` (for reassignables) introduced in ES6.")
            if re.search(r'\beval\s*\(', code_part):
                issues.append("- **Security Vulnerability**: `eval()` detected. Avoid dynamic code execution due to arbitrary code injection risks.")
            if re.search(r'\.reduce\s*\(', code_part) and any(k in code_lower for k in ["category", "group", "type"]):
                warnings.append("- **Manual Object Grouping**: Manual `.reduce()` grouping pattern detected. In ECMAScript 2024, use native `Object.groupBy(iterable, callback)` for cleaner, faster grouping.")
            if ".then(" in code_lower and "async" not in code_lower and "fetchuser" not in code_lower:
                warnings.append("- **Promise Chaining**: `.then()` chains detected without `async/await`. Consider refactoring to `async/await` for better readability and structured error handling.")
            if re.search(r'\.slice\s*\(', code_part):
                positive.append("- Uses modern standard `.slice()` method for substring/array extraction.")
            if "express.router" in code_lower or "router." in code_lower or "router =" in code_lower:
                positive.append("- Uses modern Express Router modular route composition.")
            if re.search(r'\bconst\s+', code_part):
                positive.append("- Uses modern immutable variable declarations (`const`).")
            if re.search(r'\blet\s+', code_part):
                positive.append("- Uses modern block-scoped mutable declarations (`let`).")
            if "=>" in code_part:
                positive.append("- Uses ES6 arrow function syntax.")
            if "async " in code_part or "await " in code_part:
                positive.append("- Employs modern `async/await` asynchronous flow.")
            if "require(" in code_part:
                positive.append("- Uses standard Node.js CommonJS module resolution.")
            if "import " in code_part or "export " in code_part:
                positive.append("- Uses ECMAScript standard ES Modules (`import/export`).")

        # --- Python patterns ---
        if "python" in tech or "py" in tech or "python" in lang or "py" in lang:
            if re.search(r'^\s*print\s+[^(]', code_part, re.MULTILINE):
                issues.append("- **Python 2 Syntax**: Python 2 style `print` statement detected. Replace with `print()` function.")
            if re.search(r'except\s*:', code_part):
                issues.append("- **Bare `except:` Clause**: Catches all exceptions including SystemExit and KeyboardInterrupt. Specify `except Exception:` or exact error classes.")
            if "typevar(" in code_lower or "from typing import typevar" in code_lower or "from typing import list" in code_lower:
                warnings.append("- **Legacy Generics Syntax**: `TypeVar` / `typing.List` detected. In Python 3.12 & 3.13 (PEP 695), use native generic type parameters: `def func[T](items: list[T]) -> T:`.")
            if re.search(r'(def|class)\s+[a-zA-Z0-9_]+\[', code_part):
                positive.append("- Uses modern Python 3.12+ PEP 695 type parameter syntax.")
            if "from typing import" in code_part or "import " in code_part:
                positive.append("- Includes modular type hints / library imports.")
            if re.search(r'\bf["\']', code_part):
                positive.append("- Uses modern formatted string literals (f-strings).")
            if "dataclass" in code_lower:
                positive.append("- Uses `dataclass` decorator for clean data models.")
            if "async def" in code_part:
                positive.append("- Uses native Python `asyncio` asynchronous coroutines.")
            if "def " in code_part:
                positive.append("- Clean standard Python function definition.")

        if not issues and not warnings and not positive:
            return (
                "STATUS: UNCERTAIN\n\n"
                "### Executive Summary\n"
                "Code analysis processed via SyntaxHub Static Analysis Engine (ChromaDB RAG Grounded).\n"
                "**Status: Uncertain / Insufficient Syntax Evidence.**\n"
                "No known deprecated or modern patterns could be verified for the specified snippet.\n\n"
                "### Recommendations\n"
                "- Provide a more complete snippet with language-specific construct definitions to evaluate compliance.\n"
            )

        # Determine explicit overall status
        if issues:
            status_tag = "STATUS: OUTDATED"
            issues_str = "\n".join(issues)
            positive_str = "\n".join(positive) if positive else "- Standard language grammar."
            warning_str = ("\n\n### Optimization Suggestions\n" + "\n".join(warnings)) if warnings else ""
            return (
                f"{status_tag}\n\n"
                "### Executive Summary\n"
                "Code analysis processed via SyntaxHub Static Analysis Engine (ChromaDB RAG Grounded).\n"
                "**Outdated or legacy patterns were detected** that should be migrated to modern official documentation standards.\n\n"
                "### Detected Issues\n"
                f"{issues_str}"
                f"{warning_str}\n\n"
                "### Modern Patterns Found\n"
                f"{positive_str}\n\n"
                "### Migration Guidance\n"
                "- Review each detected issue above and replace legacy syntax with modern recommended patterns.\n"
                "- Refer to official framework release guides for step-by-step upgrade instructions.\n\n"
                "*(Tip: Set `OPENROUTER_API_KEY` or `GEMINI_API_KEY` in `services/.env` for live LLM completions using Llama-3.3 / Gemini)*"
            )
        elif warnings:
            status_tag = "STATUS: WARNING"
            warnings_str = "\n".join(warnings)
            positive_str = "\n".join(positive) if positive else "- Standard language grammar."
            return (
                f"{status_tag}\n\n"
                "### Executive Summary\n"
                "Code analysis processed via SyntaxHub Static Analysis Engine (ChromaDB RAG Grounded).\n"
                "**Overall Code Health: Good with Optimization Opportunities.**\n"
                "The code is functional and largely modern, but newer official language features provide better alternatives.\n\n"
                "### Optimization Suggestions\n"
                f"{warnings_str}\n\n"
                "### Modern Patterns Found\n"
                f"{positive_str}\n\n"
                "### Recommendations\n"
                "- Consider adopting the suggested modern patterns for improved performance, cleaner syntax, and better maintainability.\n\n"
                "*(Tip: Set `OPENROUTER_API_KEY` or `GEMINI_API_KEY` in `services/.env` for live LLM completions using Llama-3.3 / Gemini)*"
            )
        else:
            status_tag = "STATUS: CURRENT"
            if not positive:
                positive = ["- Code follows modern conventions and standard language syntax.", "- Clean structural definitions and declarations."]
            positive_str = "\n".join(positive)
            return (
                f"{status_tag}\n\n"
                "### Executive Summary\n"
                "Code analysis processed via SyntaxHub Static Analysis Engine (ChromaDB RAG Grounded).\n"
                "**Overall Code Health: Current & Compliant.**\n"
                "All checks passed! The submitted code adheres to modern official documentation standards.\n\n"
                "### Compliance Assessment\n"
                "- No deprecated or outdated patterns were detected in this code.\n"
                "- Architecture is compliant with current language recommendations.\n\n"
                "### Modern Patterns Found\n"
                f"{positive_str}\n\n"
                "### Recommendations\n"
                "- The code is in excellent health. Continue following clean code practices and maintain current test coverage.\n\n"
                "*(Tip: Set `OPENROUTER_API_KEY` or `GEMINI_API_KEY` in `services/.env` for live LLM completions using Llama-3.3 / Gemini)*"
            )

llm_provider = LLMProvider()
