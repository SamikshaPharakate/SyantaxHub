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

    AIQueryLog.create({
      queryType: 'explain',
      prompt: `[${language || 'code'}] ${code.substring(0, 150)}...`,
      response: typeof aiResult === 'string' ? aiResult : JSON.stringify(aiResult),
      user: req.user ? req.user.id : undefined,
    }).catch(err => console.warn('[Log Warning]', err.message));

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

    AIQueryLog.create({
      queryType: 'rag',
      prompt: query,
      response: typeof aiResult === 'string' ? aiResult : JSON.stringify(aiResult),
      user: req.user ? req.user.id : undefined,
    }).catch(err => console.warn('[Log Warning]', err.message));

    res.status(200).json({ success: true, data: aiResult.data || aiResult });
  } catch (err) {
    next(err);
  }
};

exports.searchVector = async (req, res, next) => {
  try {
    const { query, collection_name, n_results } = req.body;
    if (!query) {
      return res.status(400).json({ success: false, error: 'Query parameter is required' });
    }

    const searchResult = await aiMicroservice.vectorSearch({ query, collection_name, n_results });

    AIQueryLog.create({
      queryType: 'vector_search',
      prompt: query,
      response: JSON.stringify(searchResult),
      user: req.user ? req.user.id : undefined,
    }).catch(err => console.warn('[Log Warning]', err.message));

    res.status(200).json({ success: true, data: searchResult.data || searchResult });
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

exports.checkHealth = async (req, res, next) => {
  try {
    const healthStatus = await aiMicroservice.checkHealth();
    res.status(200).json({ success: true, data: healthStatus });
  } catch (err) {
    next(err);
  }
};

exports.getStats = async (req, res, next) => {
  try {
    const stats = await aiMicroservice.getStats();
    res.status(200).json({ success: true, data: stats });
  } catch (err) {
    next(err);
  }
};

exports.getLogs = async (req, res, next) => {
  try {
    const filter = {};
    if (req.user) filter.user = req.user.id;
    const logs = await AIQueryLog.find(filter).sort({ createdAt: -1 }).limit(50);
    res.status(200).json({ success: true, count: logs.length, data: logs });
  } catch (err) {
    next(err);
  }
};

