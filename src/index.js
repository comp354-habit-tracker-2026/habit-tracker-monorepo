const express = require('express');
const goalsRouter = require('./routes/goals');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Habit Tracker API',
    version: '1.0.0'
  });
});

// Mount routes
app.use('/goals', goalsRouter);

// 404 handler for undefined routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`
  });
});

// Error handling middleware
app.use((err, req, res) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message
  });
});

// Start server if not in test mode
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Habit Tracker API running on port ${PORT}`);
  });
}

module.exports = app;
