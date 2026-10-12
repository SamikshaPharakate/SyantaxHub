const express = require('express');
const { createAnalysis, getAnalyses, getAnalysisById, toggleSaveAnalysis, deleteAnalysis } = require('../controllers/analysisController');
const { optionalAuth } = require('../middlewares/authMiddleware');

const router = express.Router();

router.route('/')
  .get(optionalAuth, getAnalyses)
  .post(optionalAuth, createAnalysis);

router.patch('/:id/toggle-save', optionalAuth, toggleSaveAnalysis);
router.patch('/:id/save', optionalAuth, toggleSaveAnalysis);

router.route('/:id')
  .get(optionalAuth, getAnalysisById)
  .delete(optionalAuth, deleteAnalysis);

module.exports = router;
