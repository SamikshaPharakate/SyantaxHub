const jwt = require('jsonwebtoken');
const User = require('../models/User');

const getTokenFromRequest = (req) => {
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    return req.headers.authorization.split(' ')[1];
  }
  if (req.cookies && req.cookies.token) {
    return req.cookies.token;
  }
  if (req.headers.cookie) {
    const cookies = req.headers.cookie.split(';');
    for (let cookie of cookies) {
      const [name, val] = cookie.trim().split('=');
      if (name === 'token' && val) {
        return decodeURIComponent(val);
      }
    }
  }
  return null;
};

exports.protect = async (req, res, next) => {
  const token = getTokenFromRequest(req);

  if (!token || token === 'none') {
    return res.status(401).json({ success: false, error: 'Not authorized to access this route' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'syntaxhub_jwt_super_secret_key_2026');
    req.user = await User.findById(decoded.id);
    if (!req.user) {
      return res.status(401).json({ success: false, error: 'User no longer exists' });
    }
    next();
  } catch (err) {
    return res.status(401).json({ success: false, error: 'Token invalid or expired' });
  }
};

exports.optionalAuth = async (req, res, next) => {
  const token = getTokenFromRequest(req);

  if (token && token !== 'none') {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'syntaxhub_jwt_super_secret_key_2026');
      req.user = await User.findById(decoded.id);
    } catch (err) {
      // Ignore token failure for optional auth
    }
  }
  next();
};
