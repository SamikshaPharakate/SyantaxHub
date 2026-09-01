const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/syntaxhub', {
      dbName: 'syntaxhub'
    });
    console.log(`[MongoDB] Database connected successfully: ${conn.connection.host} / ${conn.connection.name}`);
  } catch (error) {
    console.error(`[MongoDB Error] Connection failed: ${error.message}`);
    // Non-fatal warning if network is restricted during local test build
  }
};

module.exports = connectDB;
