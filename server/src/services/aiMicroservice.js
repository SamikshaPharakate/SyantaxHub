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
    const response = await aiMicroserviceClient.post('/rag/analyze-code', analysisData);
    return response.data;
  },

  async seedDocs() {
    const response = await aiMicroserviceClient.post('/rag/seed-docs');
    return response.data;
  },

  async queryRAG(queryData) {
    const response = await aiMicroserviceClient.post('/rag/query', queryData);
    return response.data;
  },

  async indexSnippet(snippetData) {
    const response = await aiMicroserviceClient.post('/rag/index-code', snippetData);
    return response.data;
  },

  async explainCode(codeData) {
    const response = await aiMicroserviceClient.post('/llm/explain', codeData);
    return response.data;
  },

  async checkHealth() {
    const response = await aiMicroserviceClient.get('/health');
    return response.data;
  },
};
