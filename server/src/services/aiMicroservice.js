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
      console.warn('[AI Microservice Warning] analyzeCode call failed:', err.message);
      return {
        success: false,
        data: {
          language: analysisData.language,
          technology: analysisData.technology,
          version: analysisData.version,
          analysis: `[AI Service Unavailable] Could not reach Python FastAPI AI microservice at ${AI_SERVICE_BASE}. Ensure service is running via 'npm run dev:services'.\n\nOriginal Code:\n\`\`\`${analysisData.language}\n${analysisData.code}\n\`\`\``,
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
      console.warn('[AI Microservice Warning] queryRAG call failed:', err.message);
      return {
        success: false,
        data: {
          query: queryData.query,
          answer: `[AI Service Unavailable] Could not query vector database at ${AI_SERVICE_BASE}: ${err.message}`,
          sources: [],
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
