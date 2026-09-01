const express = require('express');
const { getSnippets, getSnippetById, createSnippet, deleteSnippet } = require('../controllers/snippetController');
const { optionalAuth, protect } = require('../middlewares/authMiddleware');

const router = express.Router();

router.route('/')
  .get(getSnippets)
  .post(optionalAuth, createSnippet);

router.route('/:id')
  .get(getSnippetById)
  .delete(protect, deleteSnippet);

module.exports = router;
