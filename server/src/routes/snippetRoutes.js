const express = require('express');
const {
  getSnippets,
  getUserSnippets,
  getSnippetById,
  createSnippet,
  updateSnippet,
  deleteSnippet,
} = require('../controllers/snippetController');
const { optionalAuth, protect } = require('../middlewares/authMiddleware');

const router = express.Router();

router.route('/')
  .get(optionalAuth, getSnippets)
  .post(optionalAuth, createSnippet);

router.get('/user/me', protect, getUserSnippets);

router.route('/:id')
  .get(getSnippetById)
  .put(protect, updateSnippet)
  .delete(protect, deleteSnippet);

module.exports = router;
