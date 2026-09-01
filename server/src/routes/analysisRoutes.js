const express = require('express');
const { createAnalysis, getAnalyses, toggleSaveAnalysis, deleteAnalysis } = require('../controllers/analysisController');
const { optionalAuth } = require('../middlewares/authMiddleware');

const router = express.Router();

router.route('/')
  .get(optionalAuth, getAnalyses)
  .post(optionalAuth, createAnalysis);

router.route('/:id/save')
  .patch(optionalAuth, toggleSaveAnalysis);

router.route('/:id')
  .delete(optionalAuth, deleteAnalysis);

module.exports = router;
