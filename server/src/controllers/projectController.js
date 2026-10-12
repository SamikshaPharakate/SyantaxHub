const Project = require('../models/Project');

exports.getProjects = async (req, res, next) => {
  try {
    const filter = {};
    if (req.user) filter.user = req.user.id;

    const projects = await Project.find(filter).sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: projects.length, data: projects });
  } catch (err) {
    next(err);
  }
};

exports.getProjectById = async (req, res, next) => {
  try {
    const project = await Project.findById(req.params.id);
    if (!project) {
      return res.status(404).json({ success: false, error: 'Project not found' });
    }
    res.status(200).json({ success: true, data: project });
  } catch (err) {
    next(err);
  }
};

exports.createProject = async (req, res, next) => {
  try {
    const { name, description, technology } = req.body;
    if (!name) {
      return res.status(400).json({ success: false, error: 'Project name is required' });
    }

    const project = await Project.create({
      name,
      description: description || '',
      technology: technology || 'General',
      user: req.user ? req.user.id : undefined,
    });

    res.status(201).json({ success: true, data: project });
  } catch (err) {
    next(err);
  }
};

exports.updateProject = async (req, res, next) => {
  try {
    let project = await Project.findById(req.params.id);
    if (!project) {
      return res.status(404).json({ success: false, error: 'Project not found' });
    }

    if (project.user && req.user && project.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, error: 'Not authorized to update project' });
    }

    const { name, description, technology } = req.body;
    project = await Project.findByIdAndUpdate(
      req.params.id,
      {
        ...(name && { name }),
        ...(description !== undefined && { description }),
        ...(technology && { technology }),
      },
      { new: true, runValidators: true }
    );

    res.status(200).json({ success: true, data: project });
  } catch (err) {
    next(err);
  }
};

exports.deleteProject = async (req, res, next) => {
  try {
    const project = await Project.findById(req.params.id);
    if (!project) {
      return res.status(404).json({ success: false, error: 'Project not found' });
    }

    if (project.user && req.user && project.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, error: 'Not authorized to delete project' });
    }

    await project.deleteOne();
    res.status(200).json({ success: true, message: 'Project deleted' });
  } catch (err) {
    next(err);
  }
};
