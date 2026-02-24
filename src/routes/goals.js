const express = require('express');
const router = express.Router();
const { goals, templates } = require('../models/data');
const { validateId } = require('../middleware/validation');

// GET /goals/templates - Get all goal templates
// Must come before /:id to avoid matching as an id parameter
router.get('/templates', (req, res) => {
  res.status(200).json({
    count: templates.length,
    templates: templates
  });
});

// GET /goals/:id - Get a specific goal by ID
router.get('/:id', validateId, (req, res) => {
  const { id } = req.params;

  const goal = goals.find(g => g.id === id);

  if (!goal) {
    return res.status(404).json({
      error: 'Goal not found',
      message: `No goal exists with id: ${id}`
    });
  }

  res.status(200).json(goal);
});

module.exports = router;
