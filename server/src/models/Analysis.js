const mongoose = require('mongoose');

const AnalysisSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: true,
      default: 'Code Analysis',
    },
    technology: {
      type: String,
      required: true,
      trim: true,
    },
    language: {
      type: String,
      required: true,
      trim: true,
    },
    version: {
      type: String,
      default: 'latest',
    },
    code: {
      type: String,
      required: true,
    },
    result: {
      type: mongoose.Schema.Types.Mixed,
      required: true,
    },
    status: {
      type: String,
      enum: ['current', 'outdated', 'deprecated'],
      default: 'outdated',
    },
    isSaved: {
      type: Boolean,
      default: false,
    },
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: false,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Analysis', AnalysisSchema);
