const mongoose = require('mongoose');

const AIQueryLogSchema = new mongoose.Schema(
  {
    queryType: {
      type: String,
      enum: ['explain', 'refactor', 'rag', 'vector_search'],
      required: true,
    },
    prompt: {
      type: String,
      required: true,
    },
    response: {
      type: String,
      required: true,
    },
    tokensUsed: {
      type: Number,
      default: 0,
    },
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: false,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('AIQueryLog', AIQueryLogSchema);
