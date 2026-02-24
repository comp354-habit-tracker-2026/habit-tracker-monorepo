// Goal model with fields: id, userId, duration, sport, progressionType, reward

class Goal {
  constructor(data) {
    this.id = data.id;
    this.userId = data.userId;
    this.duration = data.duration;
    this.sport = data.sport;
    this.progressionType = data.progressionType;
    this.reward = data.reward;
  }

  validate() {
    const errors = [];

    if (!this.id) errors.push('id is required');
    if (!this.userId) errors.push('userId is required');
    if (!this.duration) errors.push('duration is required');
    if (!this.sport) errors.push('sport is required');
    if (!this.progressionType) errors.push('progressionType is required');
    if (!this.reward) errors.push('reward is required');

    // Validate progressionType enum
    const validProgressionTypes = ['linear', 'exponential', 'step', 'custom'];
    if (this.progressionType && !validProgressionTypes.includes(this.progressionType)) {
      errors.push(`progressionType must be one of: ${validProgressionTypes.join(', ')}`);
    }

    return errors.length === 0 ? null : errors;
  }

  toJSON() {
    return {
      id: this.id,
      userId: this.userId,
      duration: this.duration,
      sport: this.sport,
      progressionType: this.progressionType,
      reward: this.reward
    };
  }
}

module.exports = Goal;
