const aiMicroservice = require('../services/aiMicroservice');
const AIQueryLog = require('../models/AIQueryLog');

exports.analyzeCode = async (req, res, next) => {
  try {
    const { code, language, technology, version } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: 'Code parameter is required' });
    }

    const aiResult = await aiMicroservice.analyzeCode({ code, language, technology, version });

    // Log query asynchronously
    AIQueryLog.create({
      queryType: 'refactor',
      prompt: `[${language}/${technology}] ${code.substring(0, 150)}...`,
      response: typeof aiResult === 'string' ? aiResult : JSON.stringify(aiResult),
      user: req.user ? req.user.id : undefined,
    }).catch(err => console.warn('[Log Warning]', err.message));

    res.status(200).json({ success: true, data: aiResult.data || aiResult });
  } catch (err) {
    next(err);
  }
};

exports.seedDocs = async (req, res, next) => {
  try {
    const result = await aiMicroservice.seedDocs();
    res.status(200).json({ success: true, data: result });
  } catch (err) {
    next(err);
  }
};

exports.explainCode = async (req, res, next) => {
  try {
    const { code, language, context } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: 'Code parameter is required' });
    }

    const aiResult = await aiMicroservice.explainCode({ code, language, context });
    res.status(200).json({ success: true, data: aiResult.data || aiResult });
  } catch (err) {
    next(err);
  }
};

exports.queryRAG = async (req, res, next) => {
  try {
    const { query, collection_name, top_k } = req.body;
    if (!query) {
      return res.status(400).json({ success: false, error: 'Query parameter is required' });
    }

    const aiResult = await aiMicroservice.queryRAG({ query, collection_name, top_k });
    res.status(200).json({ success: true, data: aiResult.data || aiResult });
  } catch (err) {
    next(err);
  }
};

exports.indexCode = async (req, res, next) => {
  try {
    const { id, title, language, code, description } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: 'Code parameter is required' });
    }

    const indexResult = await aiMicroservice.indexSnippet({ id, title, language, code, description });
    res.status(200).json({ success: true, data: indexResult });
  } catch (err) {
    next(err);
  }
};
