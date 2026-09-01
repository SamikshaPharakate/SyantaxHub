/**
 * SyntaxHub Client API Gateway
 * Wraps HTTP calls to Express Backend Server and FastAPI AI Microservice
 */

const BACKEND_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
const AI_SERVICE_BASE = process.env.NEXT_PUBLIC_AI_SERVICE_URL || 'http://localhost:8000/api';

export interface Snippet {
  _id?: string;
  title: string;
  language: string;
  code: string;
  description?: string;
  tags?: string[];
}

export interface CodeAnalysisPayload {
  code: string;
  language: string;
  technology?: string;
  version?: string;
}

export interface RAGQueryRequest {
  query: string;
  collection_name?: string;
  top_k?: number;
}

export interface CodeExplainRequest {
  code: string;
  language: string;
  context?: string;
}

/**
 * Backend API Client (Node.js Express)
 */
export const backendApi = {
  // Auth
  async register(userData: Record<string, any>) {
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return res.json();
  },

  async login(credentials: Record<string, any>) {
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return res.json();
  },

  async demoLogin() {
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/demo-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return res.json();
  },

  // AI & Analysis Gateway Proxies
  async analyzeCode(payload: CodeAnalysisPayload) {
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/analyze-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async saveAnalysis(analysisData: Record<string, any>, token?: string) {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${BACKEND_API_BASE}/v1/analyses`, {
      method: 'POST',
      headers,
      body: JSON.stringify(analysisData),
    });
    return res.json();
  },

  async fetchAnalyses(savedOnly?: boolean, token?: string) {
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const url = `${BACKEND_API_BASE}/v1/analyses${savedOnly ? '?saved=true' : ''}`;
    const res = await fetch(url, { headers });
    return res.json();
  },

  async seedOfficialDocs() {
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/seed-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return res.json();
  },

  // Snippets
  async fetchSnippets(token?: string) {
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${BACKEND_API_BASE}/v1/snippets`, { headers });
    return res.json();
  },

  async createSnippet(snippet: Snippet, token?: string) {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${BACKEND_API_BASE}/v1/snippets`, {
      method: 'POST',
      headers,
      body: JSON.stringify(snippet),
    });
    return res.json();
  },
};

/**
 * Direct AI Microservice Client (Python FastAPI)
 */
export const aiServiceApi = {
  async queryRAG(payload: RAGQueryRequest) {
    const res = await fetch(`${AI_SERVICE_BASE}/v1/rag/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async analyzeCodeDirect(payload: CodeAnalysisPayload) {
    const res = await fetch(`${AI_SERVICE_BASE}/v1/rag/analyze-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async seedDocsDirect() {
    const res = await fetch(`${AI_SERVICE_BASE}/v1/rag/seed-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return res.json();
  },

  async explainCode(payload: CodeExplainRequest) {
    const res = await fetch(`${AI_SERVICE_BASE}/v1/llm/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return res.json();
  },

  async checkHealth() {
    const res = await fetch(`${AI_SERVICE_BASE}/v1/health`);
    return res.json();
  },
};
