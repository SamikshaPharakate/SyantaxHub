const Snippet = require('../models/Snippet');
const aiMicroservice = require('../services/aiMicroservice');

exports.getSnippets = async (req, res, next) => {
  try {
    const { search, language, tag, userOnly } = req.query;
    const filter = { isPublic: true };

    if (userOnly === 'true' && req.user) {
      delete filter.isPublic;
      filter.user = req.user.id;
    }

    if (language) {
      filter.language = language.toLowerCase();
    }

    if (tag) {
      filter.tags = tag.toLowerCase();
    }

    if (search) {
      filter.$or = [
        { title: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { code: { $regex: search, $options: 'i' } },
      ];
    }

    const snippets = await Snippet.find(filter).sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: snippets.length, data: snippets });
  } catch (err) {
    next(err);
  }
};

exports.getUserSnippets = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({ success: false, error: 'Not authorized' });
    }
    const snippets = await Snippet.find({ user: req.user.id }).sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: snippets.length, data: snippets });
  } catch (err) {
    next(err);
  }
};

exports.getSnippetById = async (req, res, next) => {
  try {
    const snippet = await Snippet.findById(req.params.id);
    if (!snippet) {
      return res.status(404).json({ success: false, error: 'Snippet not found' });
    }
    res.status(200).json({ success: true, data: snippet });
  } catch (err) {
    next(err);
  }
};

exports.createSnippet = async (req, res, next) => {
  try {
    const { title, language, code, description, tags, isPublic } = req.body;

    const snippet = await Snippet.create({
      title,
      language: language ? language.toLowerCase() : 'javascript',
      code,
      description: description || '',
      tags: tags || [],
      isPublic: isPublic !== undefined ? isPublic : true,
      user: req.user ? req.user.id : undefined,
    });

    // Auto-index to ChromaDB via AI microservice in background (non-blocking)
    aiMicroservice.indexSnippet({
      id: snippet._id.toString(),
      title: snippet.title,
      language: snippet.language,
      code: snippet.code,
      description: snippet.description,
    }).then(() => {
      Snippet.findByIdAndUpdate(snippet._id, { vectorIndexed: true }).exec();
    }).catch(err => {
      console.warn('[AI Service Warning] Auto vector indexing failed:', err.message);
    });

    res.status(201).json({ success: true, data: snippet });
  } catch (err) {
    next(err);
  }
};

exports.updateSnippet = async (req, res, next) => {
  try {
    let snippet = await Snippet.findById(req.params.id);
    if (!snippet) {
      return res.status(404).json({ success: false, error: 'Snippet not found' });
    }

    if (snippet.user && req.user && snippet.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, error: 'Not authorized to update this snippet' });
    }

    const { title, language, code, description, tags, isPublic } = req.body;

    snippet = await Snippet.findByIdAndUpdate(
      req.params.id,
      {
        ...(title && { title }),
        ...(language && { language: language.toLowerCase() }),
        ...(code && { code }),
        ...(description !== undefined && { description }),
        ...(tags && { tags }),
        ...(isPublic !== undefined && { isPublic }),
      },
      { new: true, runValidators: true }
    );

    // Re-index in ChromaDB asynchronously
    aiMicroservice.indexSnippet({
      id: snippet._id.toString(),
      title: snippet.title,
      language: snippet.language,
      code: snippet.code,
      description: snippet.description,
    }).then(() => {
      Snippet.findByIdAndUpdate(snippet._id, { vectorIndexed: true }).exec();
    }).catch(err => {
      console.warn('[AI Service Warning] Re-indexing failed:', err.message);
    });

    res.status(200).json({ success: true, data: snippet });
  } catch (err) {
    next(err);
  }
};

exports.deleteSnippet = async (req, res, next) => {
  try {
    const snippet = await Snippet.findById(req.params.id);
    if (!snippet) {
      return res.status(404).json({ success: false, error: 'Snippet not found' });
    }

    if (snippet.user && req.user && snippet.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, error: 'Not authorized to delete this snippet' });
    }

    await snippet.deleteOne();
    res.status(200).json({ success: true, message: 'Snippet removed' });
  } catch (err) {
    next(err);
  }
};
