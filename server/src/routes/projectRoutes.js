const express = require('express');
const {
  getProjects,
  getProjectById,
  createProject,
  updateProject,
  deleteProject,
} = require('../controllers/projectController');
const { protect, optionalAuth } = require('../middlewares/authMiddleware');

const router = express.Router();

router
  .route('/')
  .get(optionalAuth, getProjects)
  .post(optionalAuth, createProject);

router
  .route('/:id')
  .get(getProjectById)
  .put(protect, updateProject)
  .delete(protect, deleteProject);

module.exports = router;
