const Snippet = require('../models/Snippet');
const aiMicroservice = require('../services/aiMicroservice');

exports.getSnippets = async (req, res, next) => {
  try {
    const snippets = await Snippet.find({ isPublic: true }).sort({ createdAt: -1 });
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
    const { title, language, code, description, tags } = req.body;

    const snippet = await Snippet.create({
      title,
      language,
      code,
      description,
      tags: tags || [],
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

exports.deleteSnippet = async (req, res, next) => {
  try {
    const snippet = await Snippet.findById(req.params.id);
    if (!snippet) {
      return res.status(404).json({ success: false, error: 'Snippet not found' });
    }

    await snippet.deleteOne();
    res.status(200).json({ success: true, message: 'Snippet removed' });
  } catch (err) {
    next(err);
  }
};
