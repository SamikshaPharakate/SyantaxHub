const mongoose = require('mongoose');

const SnippetSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: [true, 'Snippet title is required'],
      trim: true,
    },
    language: {
      type: String,
      required: [true, 'Programming language is required'],
      lowercase: true,
      trim: true,
    },
    code: {
      type: String,
      required: [true, 'Code content is required'],
    },
    description: {
      type: String,
      default: '',
    },
    tags: [
      {
        type: String,
        trim: true,
      },
    ],
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: false,
    },
    isPublic: {
      type: Boolean,
      default: true,
    },
    vectorIndexed: {
      type: Boolean,
      default: false,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Snippet', SnippetSchema);
