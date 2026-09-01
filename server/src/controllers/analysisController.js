const Analysis = require('../models/Analysis');

exports.createAnalysis = async (req, res, next) => {
  try {
    const { title, technology, language, version, code, result, status, isSaved } = req.body;

    const analysis = await Analysis.create({
      title: title || `${technology || 'Code'} Analysis`,
      technology,
      language,
      version: version || 'latest',
      code,
      result,
      status: status || 'outdated',
      isSaved: isSaved || false,
      user: req.user ? req.user.id : undefined,
    });

    res.status(201).json({ success: true, data: analysis });
  } catch (err) {
    next(err);
  }
};

exports.getAnalyses = async (req, res, next) => {
  try {
    const filter = {};
    if (req.query.saved === 'true') filter.isSaved = true;
    if (req.user) filter.user = req.user.id;

    const analyses = await Analysis.find(filter).sort({ createdAt: -1 });
    res.status(200).json({ success: true, count: analyses.length, data: analyses });
  } catch (err) {
    next(err);
  }
};

exports.toggleSaveAnalysis = async (req, res, next) => {
  try {
    const analysis = await Analysis.findById(req.params.id);
    if (!analysis) {
      return res.status(404).json({ success: false, error: 'Analysis not found' });
    }

    analysis.isSaved = !analysis.isSaved;
    await analysis.save();

    res.status(200).json({ success: true, data: analysis });
  } catch (err) {
    next(err);
  }
};

exports.deleteAnalysis = async (req, res, next) => {
  try {
    const analysis = await Analysis.findById(req.params.id);
    if (!analysis) {
      return res.status(404).json({ success: false, error: 'Analysis not found' });
    }

    await analysis.deleteOne();
    res.status(200).json({ success: true, message: 'Analysis deleted' });
  } catch (err) {
    next(err);
  }
};
