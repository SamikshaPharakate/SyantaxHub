const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const errorHandler = require('./middlewares/errorMiddleware');

const cookieParser = require('cookie-parser');

const authRoutes = require('./routes/authRoutes');
const snippetRoutes = require('./routes/snippetRoutes');
const aiRoutes = require('./routes/aiRoutes');
const analysisRoutes = require('./routes/analysisRoutes');
const projectRoutes = require('./routes/projectRoutes');

const app = express();

// Allowed Origins for CORS credentials
const allowedOrigins = [
  'http://localhost:3000',
  'http://127.0.0.1:3000',
  'https://syntax-hub.vercel.app',
  process.env.CLIENT_URL,
].filter(Boolean);

// Global Security & Utility Middlewares
app.use(helmet());
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin) || process.env.NODE_ENV !== 'production') {
      callback(null, origin || true);
    } else {
      callback(new Error('CORS policy: Not allowed by Access-Control-Allow-Origin'));
    }
  },
  credentials: true,
}));
app.use(cookieParser());
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
app.use('/api/v1/projects', projectRoutes);

// Error Handling Middleware
app.use(errorHandler);

module.exports = app;
