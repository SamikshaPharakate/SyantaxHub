const express = require('express');
const { analyzeCode, seedDocs, explainCode, queryRAG, indexCode } = require('../controllers/aiController');
const { optionalAuth } = require('../middlewares/authMiddleware');

const router = express.Router();

router.post('/analyze-code', optionalAuth, analyzeCode);
router.post('/seed-docs', seedDocs);
router.post('/explain', optionalAuth, explainCode);
router.post('/rag-query', optionalAuth, queryRAG);
router.post('/index-code', optionalAuth, indexCode);

module.exports = router;
