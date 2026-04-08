import { type Streak } from '../types/gamification';

type StreakCardProps = {
  streak: Streak;
};

export function StreakCard({ streak }: StreakCardProps) {
  return (
    <div className="gamification__streak">
      <h2 className="gamification__section-title">Streak</h2>
      <div className="gamification__streak-grid">
        <div className="gamification__streak-item">
          <span className="gamification__streak-number">{streak.current_count}</span>
          <span className="gamification__streak-label">Current days</span>
        </div>
        <div className="gamification__streak-item">
          <span className="gamification__streak-number">{streak.longest_count}</span>
          <span className="gamification__streak-label">Longest streak</span>
        </div>
      </div>
      {streak.last_activity_date && (
        <p className="gamification__streak-date">
          Last active: {new Date(streak.last_activity_date).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
