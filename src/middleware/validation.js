// Validation middleware

const validateId = (req, res, next) => {
  const { id } = req.params;

  if (!id) {
    return res.status(400).json({ error: 'ID parameter is required' });
  }

  // Validate UUID-like or string ID format
  if (typeof id !== 'string' || id.trim() === '') {
    return res.status(400).json({ error: 'ID must be a non-empty string' });
  }

  next();
};

module.exports = {
  validateId
};
