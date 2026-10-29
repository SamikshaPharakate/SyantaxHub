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

export interface ProjectItem {
  _id?: string;
  name: string;
  description?: string;
  technology?: string;
}

function getAuthHeaders(explicitToken?: string, extraHeaders?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = { ...extraHeaders };
  const token = explicitToken || (typeof window !== 'undefined' ? localStorage.getItem('syntaxhub_token') : null);
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
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
      credentials: 'include',
    });
    return res.json();
  },

  async login(credentials: Record<string, any>) {
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
      credentials: 'include',
    });
    return res.json();
  },

  async demoLogin() {
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/demo-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    });
    return res.json();
  },

  async logout() {
    try {
      const res = await fetch(`${BACKEND_API_BASE}/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      return await res.json();
    } catch (e) {
      return { success: true };
    }
  },

  async getMe(token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/auth/me`, {
      headers,
      credentials: 'include',
    });
    return res.json();
  },

  // AI & Analysis Gateway Proxies
  async analyzeCode(payload: CodeAnalysisPayload) {
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/analyze-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include',
    });
    return res.json();
  },

  async saveAnalysis(analysisData: Record<string, any>, token?: string) {
    const headers = getAuthHeaders(token, { 'Content-Type': 'application/json' });
    const res = await fetch(`${BACKEND_API_BASE}/v1/analyses`, {
      method: 'POST',
      headers,
      body: JSON.stringify(analysisData),
      credentials: 'include',
    });
    return res.json();
  },

  async fetchAnalyses(savedOnly?: boolean, token?: string) {
    const headers = getAuthHeaders(token);
    const url = `${BACKEND_API_BASE}/v1/analyses${savedOnly ? '?saved=true' : ''}`;
    const res = await fetch(url, { headers, credentials: 'include' });
    return res.json();
  },

  async toggleSaveAnalysis(id: string, token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/analyses/${id}/toggle-save`, {
      method: 'PATCH',
      headers,
      credentials: 'include',
    });
    return res.json();
  },

  async deleteAnalysis(id: string, token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/analyses/${id}`, {
      method: 'DELETE',
      headers,
      credentials: 'include',
    });
    return res.json();
  },

  async seedOfficialDocs() {
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/seed-docs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    });
    return res.json();
  },

  async queryRAG(payload: RAGQueryRequest, token?: string) {
    const headers = getAuthHeaders(token, { 'Content-Type': 'application/json' });
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/rag-query`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      credentials: 'include',
    });
    return res.json();
  },

  // Projects
  async fetchProjects(token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/projects`, { headers, credentials: 'include' });
    return res.json();
  },

  async createProject(project: ProjectItem, token?: string) {
    const headers = getAuthHeaders(token, { 'Content-Type': 'application/json' });
    const res = await fetch(`${BACKEND_API_BASE}/v1/projects`, {
      method: 'POST',
      headers,
      body: JSON.stringify(project),
      credentials: 'include',
    });
    return res.json();
  },

  async deleteProject(id: string, token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/projects/${id}`, {
      method: 'DELETE',
      headers,
      credentials: 'include',
    });
    return res.json();
  },

  // AI Query Logs
  async fetchAILogs(token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/ai/logs`, { headers, credentials: 'include' });
    return res.json();
  },

  // Snippets
  async fetchSnippets(token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/snippets`, { headers, credentials: 'include' });
    return res.json();
  },

  async createSnippet(snippet: Snippet, token?: string) {
    const headers = getAuthHeaders(token, { 'Content-Type': 'application/json' });
    const res = await fetch(`${BACKEND_API_BASE}/v1/snippets`, {
      method: 'POST',
      headers,
      body: JSON.stringify(snippet),
      credentials: 'include',
    });
    return res.json();
  },

  async deleteSnippet(id: string, token?: string) {
    const headers = getAuthHeaders(token);
    const res = await fetch(`${BACKEND_API_BASE}/v1/snippets/${id}`, {
      method: 'DELETE',
      headers,
      credentials: 'include',
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
