const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const errorHandler = require('./middlewares/errorMiddleware');

const authRoutes = require('./routes/authRoutes');
const snippetRoutes = require('./routes/snippetRoutes');
const aiRoutes = require('./routes/aiRoutes');
const analysisRoutes = require('./routes/analysisRoutes');

const app = express();

// Global Security & Utility Middlewares
app.use(helmet());
app.use(cors());
app.use(express.json());

if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

// Root Route & Health Check
app.get('/', (req, res) => {
  res.json({ message: 'SyntaxHub Backend Express API is running', version: '1.0.0' });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'UP', timestamp: new Date().toISOString() });
});

// API Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/snippets', snippetRoutes);
app.use('/api/v1/ai', aiRoutes);
app.use('/api/v1/analyses', analysisRoutes);

// Error Handling Middleware
app.use(errorHandler);

module.exports = app;
