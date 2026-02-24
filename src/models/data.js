// In-memory data store for goals and templates

const goals = [
  {
    id: 'goal-1',
    userId: 'user-1',
    duration: 30,
    sport: 'running',
    progressionType: 'linear',
    reward: 'badge-marathon'
  },
  {
    id: 'goal-2',
    userId: 'user-1',
    duration: 45,
    sport: 'cycling',
    progressionType: 'exponential',
    reward: 'badge-cyclist'
  },
  {
    id: 'goal-3',
    userId: 'user-2',
    duration: 60,
    sport: 'swimming',
    progressionType: 'step',
    reward: 'badge-swimmer'
  }
];

const templates = [
  {
    id: 'template-1',
    duration: 30,
    sport: 'running',
    progressionType: 'linear',
    reward: 'badge-marathon'
  },
  {
    id: 'template-2',
    duration: 45,
    sport: 'cycling',
    progressionType: 'exponential',
    reward: 'badge-cyclist'
  },
  {
    id: 'template-3',
    duration: 60,
    sport: 'swimming',
    progressionType: 'step',
    reward: 'badge-swimmer'
  },
  {
    id: 'template-4',
    duration: 90,
    sport: 'yoga',
    progressionType: 'custom',
    reward: 'badge-yogi'
  }
];

module.exports = {
  goals,
  templates
};
