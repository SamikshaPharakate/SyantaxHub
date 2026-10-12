const express = require('express');
const { analyzeCode, seedDocs, explainCode, queryRAG, indexCode, searchVector, checkHealth, getStats, getLogs } = require('../controllers/aiController');
const { optionalAuth } = require('../middlewares/authMiddleware');

const router = express.Router();

router.get('/health', checkHealth);
router.get('/stats', getStats);
router.get('/logs', optionalAuth, getLogs);
router.post('/analyze-code', optionalAuth, analyzeCode);
router.post('/seed-docs', seedDocs);
router.post('/explain', optionalAuth, explainCode);
router.post('/rag-query', optionalAuth, queryRAG);
router.post('/vector-search', optionalAuth, searchVector);
router.post('/index-code', optionalAuth, indexCode);

module.exports = router;
