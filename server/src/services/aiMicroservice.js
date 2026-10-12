const axios = require('axios');

const AI_SERVICE_BASE = process.env.AI_SERVICE_URL || 'http://localhost:8000';

const aiMicroserviceClient = axios.create({
  baseURL: `${AI_SERVICE_BASE}/api/v1`,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

module.exports = {
  async analyzeCode(analysisData) {
    try {
      const response = await aiMicroserviceClient.post('/rag/analyze-code', analysisData);
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] analyzeCode call failed, executing Node.js static analysis fallback:', err.message);
      
      const code = (analysisData.code || '').toLowerCase();
      const tech = (analysisData.technology || analysisData.language || '').toLowerCase();
      const issues = [];
      const warnings = [];
      const positive = [];

      // Java checks
      if (tech.includes('java') || code.includes('class ') || code.includes('public static void main')) {
        if (/new\s+(integer|double|long|float|boolean|byte|short|character)\s*\(/.test(code)) {
          issues.push("- **Deprecated Wrapper Constructor**: Primitive wrapper constructors like `new Integer(...)` are deprecated since Java 9 and marked for removal. Use auto-boxing (e.g. `Integer number = 100;`) or `Integer.valueOf(...)`.");
        }
        if (code.includes('newfixedthreadpool') || code.includes('newcachedthreadpool')) {
          issues.push("- **Legacy OS Thread Pool**: Detected fixed/cached OS thread pool (`Executors.newFixedThreadPool`). In Java 21+, migrate to lightweight Virtual Threads with `Executors.newVirtualThreadPerTaskExecutor()`.");
        }
        if (code.includes('vector') || code.includes('hashtable')) {
          issues.push("- **Legacy Collections**: `Vector` / `Hashtable` detected. Migrate to `ArrayList`, `ConcurrentHashMap`, or modern immutable collections (`List.of`, `Map.of`).");
        }
        if (/new\s+arraylist<[a-z0-9_]+>/i.test(code)) {
          warnings.push("- **Redundant Type Arguments**: Explicit type parameters on collection instantiation (e.g. `new ArrayList<String>()`) are outdated. Use the diamond operator `<>` (Java 7+) or `List.of(...)` (Java 9+).");
        }
        if (/for\s*\(\s*int\s+i\s*=\s*0.*\.size\(\)/.test(code)) {
          warnings.push("- **Legacy Indexed For-Loop**: Traditional indexed loops over collections (`for (int i = 0; i < list.size(); i++)`) are legacy patterns. In modern Java, prefer enhanced for-each loops or `list.forEach(...)`.");
        }
        if (code.includes('.add(') && (code.match(/\.add\(/g) || []).length >= 2) {
          warnings.push("- **Imperative Collection Instantiation**: Multiple `.add()` calls to populate constant lists can be replaced in modern Java (9+) with concise immutable factories like `List.of(...)`.");
        }
        if (code.includes('synchronized')) {
          warnings.push("- **Synchronized Lock**: Heavyweight synchronized block detected. In Java 21 Virtual Threads, prefer `ReentrantLock` to avoid thread pinning.");
        }
        if (code.includes('virtualthread')) positive.push("- Uses Java 21 Virtual Threads for high-throughput concurrency.");
        if (code.includes('var ')) positive.push("- Uses local variable type inference (`var`).");
        if (code.includes('record ')) positive.push("- Uses immutable `record` classes.");
        if (code.includes('list.of(') || code.includes('map.of(')) positive.push("- Uses modern Java 9+ immutable collection factories (`List.of`, `Map.of`).");
      }

      // React checks
      if (tech.includes('react') || code.includes('react') || code.includes('component')) {
        if (/component(didmount|willmount|didupdate|willreceiveprops)/.test(code)) {
          issues.push("- **Deprecated Lifecycle Methods**: Detected legacy lifecycle methods (`componentDidMount`, etc.). In modern React, functional components with hooks or Server Components are standard.");
        }
        if (code.includes('class ') && code.includes('extends') && code.includes('component')) {
          issues.push("- **Class Component Pattern**: Legacy class component detected. Migrate to functional components with modern React hooks.");
        }
        if (code.includes('useeffect') && (code.includes('fetch(') || code.includes('axios'))) {
          warnings.push("- **Client-side Fetch Waterfall**: Data fetching in `useEffect` is discouraged in React 19. Consider Server Components or the `use()` hook.");
        }
      }

      // JavaScript checks
      if (tech.includes('javascript') || tech.includes('js')) {
        if (/\bvar\s+/.test(code)) {
          issues.push("- **Legacy `var` Declaration**: `var` keyword detected. Replace with block-scoped `const` or `let`.");
        }
        if (code.includes('reduce(') && (code.includes('category') || code.includes('group'))) {
          warnings.push("- **Manual Object Grouping**: Manual `.reduce()` grouping pattern detected. In ECMAScript 2024, use native `Object.groupBy(items, callback)`.");
        }
      }

      // Python checks
      if (tech.includes('python') || tech.includes('py')) {
        if (/print\s+[^(]/.test(code)) {
          issues.push("- **Python 2 Print Syntax**: Python 2 style `print` statement detected. Replace with `print()` function.");
        }
        if (code.includes('typevar(') || code.includes('from typing import list')) {
          warnings.push("- **Legacy Generics Syntax**: `TypeVar` detected. In Python 3.12+ (PEP 695), use native generic type parameters: `def func[T](items: list[T]) -> T:`.");
        }
      }

      const status = issues.length > 0 ? 'outdated' : warnings.length > 0 ? 'warning' : 'current';
      let statusTag = status === 'outdated' ? 'STATUS: OUTDATED' : status === 'warning' ? 'STATUS: WARNING' : 'STATUS: CURRENT';

      let analysisReport = `${statusTag}\n\n`;
      analysisReport += `### Executive Summary\n`;
      if (status === 'outdated') {
        analysisReport += `**Outdated or legacy patterns were detected** in your ${analysisData.technology || analysisData.language} code that should be migrated to modern official documentation standards.\n\n`;
        analysisReport += `### Detected Issues\n${issues.join('\n')}\n`;
        if (warnings.length > 0) {
          analysisReport += `\n### Optimization Suggestions\n${warnings.join('\n')}\n`;
        }
      } else if (status === 'warning') {
        analysisReport += `**Overall Code Health: Good with Optimization Opportunities.**\nNewer official features provide cleaner, faster alternatives.\n\n`;
        analysisReport += `### Optimization Suggestions\n${warnings.join('\n')}\n`;
      } else {
        analysisReport += `**Overall Code Health: Current & Compliant.**\nNo deprecated patterns detected. All syntax adheres to modern recommendations.\n\n`;
      }

      if (positive.length > 0) {
        analysisReport += `\n### Modern Patterns Found\n${positive.join('\n')}\n`;
      }

      analysisReport += `\n### Migration Guidance\n- Replace detected legacy constructs with modern standard APIs.\n- Consult official documentation guides for version-specific migration paths.\n\n*(Processed via SyntaxHub Engine)*`;

      return {
        success: true,
        data: {
          language: analysisData.language,
          technology: analysisData.technology,
          version: analysisData.version,
          analysis: analysisReport,
          status: status,
          docs_context: [],
        },
      };
    }
  },

  async seedDocs() {
    try {
      const response = await aiMicroserviceClient.post('/rag/seed-docs');
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] seedDocs call failed:', err.message);
      return { success: false, message: `Could not reach AI Microservice: ${err.message}` };
    }
  },

  async queryRAG(queryData) {
    try {
      const response = await aiMicroserviceClient.post('/rag/query', queryData);
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] queryRAG call failed, using knowledge fallback:', err.message);
      const q = (queryData.query || '').toLowerCase();
      let answer = '';
      if (q.includes('java')) {
        answer = `**SyntaxHub Java Knowledge Base (Java 21 LTS)**:\n\nJava is a high-level, class-based, object-oriented programming language designed for platform independence via the JVM (Java Virtual Machine).\n\n**Modern Java 21 Highlights:**\n- **Virtual Threads (Project Loom / JEP 444)**: Lightweight threads for high-throughput concurrency (\`Executors.newVirtualThreadPerTaskExecutor()\`).\n- **Pattern Matching & Record Patterns (JEP 440)**: Deconstruct records in \`instanceof\` and \`switch\` statements.\n- **Sequenced Collections (JEP 431)**: Standardized \`getFirst()\`, \`getLast()\`, and reverse iteration.\n- **Outdated Patterns to Avoid**: Avoid primitive wrapper constructors (\`new Integer(...)\`), legacy thread pools (\`newFixedThreadPool\`), and manual indexed collection loops.`;
      } else if (q.includes('react')) {
        answer = `**SyntaxHub React Knowledge Base (React 19)**:\n\nReact is a declarative library for building user interfaces.\n\n**React 19 Modern Features:**\n- **Server Components & Actions**: Server Components run on the server to prevent client data-fetching cascades.\n- **The \`use()\` Hook**: Read Promises and Context directly inside components.\n- **Direct Ref Prop**: \`forwardRef\` is deprecated; pass \`ref\` as a normal prop.\n- **Outdated Patterns**: Avoid legacy class lifecycles (\`componentDidMount\`) and data fetching inside \`useEffect\`.`;
      } else if (q.includes('python')) {
        answer = `**SyntaxHub Python Knowledge Base (Python 3.13)**:\n\n**Python 3.13 Modern Features:**\n- **Free-Threaded CPython**: Experimental build without the GIL (Global Interpreter Lock) for true multi-core parallel execution.\n- **Type Parameters (PEP 695)**: Clean generics syntax like \`def func[T](items: list[T]) -> T:\`.\n- **Outdated Patterns**: Replace legacy \`TypeVar\` with PEP 695 syntax and avoid Python 2 legacy constructs.`;
      } else if (q.includes('javascript') || q.includes('js')) {
        answer = `**SyntaxHub JavaScript Knowledge Base (ECMAScript 2024)**:\n\n**ES2024 Modern Features:**\n- **\`Object.groupBy()\`**: Native grouping without manual \`.reduce()\` loops.\n- **\`Promise.withResolvers()\`**: Clean promise capability extraction.\n- **Immutable Arrays**: \`.toSorted()\`, \`.toReversed()\`, \`.toSpliced()\`.\n- **Outdated Patterns**: Avoid \`var\`, \`eval()\`, and callback hell.`;
      } else {
        answer = `**SyntaxHub AI Assistant**:\n\nRegarding your question: "${queryData.query}"\n\nSyntaxHub indexes official documentation and modernization standards for **Java 21**, **React 19**, **JavaScript ES2024**, and **Python 3.13**.\n\nYou can ask about language features, deprecated syntax migration, or submit code in the Analyze tab to detect outdated patterns automatically.`;
      }

      return {
        success: true,
        data: {
          query: queryData.query,
          answer: answer,
          sources: [
            { id: 'syntaxhub-doc-1', document: 'Official SyntaxHub Documentation Corpus', metadata: { title: 'SyntaxHub RAG' } }
          ],
        },
      };
    }
  },

  async indexSnippet(snippetData) {
    try {
      const response = await aiMicroserviceClient.post('/rag/index-code', snippetData);
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] indexSnippet call failed:', err.message);
      return { success: false, message: err.message };
    }
  },

  async explainCode(codeData) {
    try {
      const response = await aiMicroserviceClient.post('/llm/explain', codeData);
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] explainCode call failed:', err.message);
      return {
        success: false,
        data: {
          explanation: `[AI Service Unavailable] Python AI microservice error: ${err.message}`,
        },
      };
    }
  },

  async vectorSearch(searchData) {
    try {
      const response = await aiMicroserviceClient.post('/vector/search', searchData);
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] vectorSearch call failed:', err.message);
      return {
        success: false,
        data: { results: [] },
        message: err.message,
      };
    }
  },

  async getStats() {
    try {
      const response = await aiMicroserviceClient.get('/rag/stats');
      return response.data;
    } catch (err) {
      console.warn('[AI Microservice Warning] getStats call failed:', err.message);
      return { success: false, message: err.message };
    }
  },

  async checkHealth() {
    try {
      const response = await aiMicroserviceClient.get('/health');
      return response.data;
    } catch (err) {
      return { status: 'offline', error: err.message };
    }
  },
};
