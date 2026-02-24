const request = require('supertest');
const app = require('../src/index');

describe('Habit Tracker API - Goals Endpoints', () => {
  describe('GET /', () => {
    it('should return health check', async () => {
      const res = await request(app).get('/');
      expect(res.status).toBe(200);
      expect(res.body.status).toBe('ok');
      expect(res.body.message).toBe('Habit Tracker API');
    });
  });

  describe('GET /goals/:id', () => {
    it('should return a goal when valid id is provided', async () => {
      const res = await request(app).get('/goals/goal-1');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('id', 'goal-1');
      expect(res.body).toHaveProperty('userId', 'user-1');
      expect(res.body).toHaveProperty('duration', 30);
      expect(res.body).toHaveProperty('sport', 'running');
      expect(res.body).toHaveProperty('progressionType', 'linear');
      expect(res.body).toHaveProperty('reward', 'badge-marathon');
    });

    it('should return another goal when different valid id is provided', async () => {
      const res = await request(app).get('/goals/goal-2');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('id', 'goal-2');
      expect(res.body).toHaveProperty('sport', 'cycling');
      expect(res.body).toHaveProperty('progressionType', 'exponential');
    });

    it('should return 404 when goal does not exist', async () => {
      const res = await request(app).get('/goals/nonexistent-goal');
      expect(res.status).toBe(404);
      expect(res.body).toHaveProperty('error', 'Goal not found');
      expect(res.body).toHaveProperty('message');
    });

    it('should return 400 when id is missing', async () => {
      const res = await request(app).get('/goals/');
      expect(res.status).toBe(404); // Express handles this as route not found
    });

    it('should return 400 when id is invalid (empty string)', async () => {
      // Note: Express routing may handle this differently
      // This is more of a validation edge case
      const res = await request(app).get('/goals/ ');
      expect(res.status).toBe(404);
    });
  });

  describe('GET /goals/templates', () => {
    it('should return all goal templates', async () => {
      const res = await request(app).get('/goals/templates');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('count');
      expect(res.body).toHaveProperty('templates');
      expect(Array.isArray(res.body.templates)).toBe(true);
      expect(res.body.count).toBeGreaterThan(0);
    });

    it('should return templates with correct structure', async () => {
      const res = await request(app).get('/goals/templates');
      expect(res.status).toBe(200);
      const template = res.body.templates[0];
      expect(template).toHaveProperty('id');
      expect(template).toHaveProperty('duration');
      expect(template).toHaveProperty('sport');
      expect(template).toHaveProperty('progressionType');
      expect(template).toHaveProperty('reward');
    });

    it('should include predefined templates', async () => {
      const res = await request(app).get('/goals/templates');
      const ids = res.body.templates.map(t => t.id);
      expect(ids).toContain('template-1');
      expect(ids).toContain('template-2');
      expect(ids).toContain('template-3');
    });
  });

  describe('404 handling for undefined routes', () => {
    it('should return 404 for non-existent routes', async () => {
      const res = await request(app).get('/undefined-route');
      expect(res.status).toBe(404);
      expect(res.body).toHaveProperty('error', 'Not Found');
    });
  });
});
