import { type MilestoneProgress, type UserMilestone } from '../types/gamification';

type MilestoneListProps = {
  milestoneProgress: MilestoneProgress[];
  reachedMilestones: UserMilestone[];
};

const METRIC_LABELS: Record<string, string> = {
  total_distance: 'Distance',
  total_duration: 'Duration',
  total_calories: 'Calories',
  total_activities: 'Activities',
};

export function MilestoneList({ milestoneProgress, reachedMilestones }: MilestoneListProps) {
  const reachedIds = new Set(reachedMilestones.map((um) => um.milestone.id));

  const sorted = [...milestoneProgress].sort((a, b) => {
    const aReached = reachedIds.has(a.milestone.id) ? 1 : 0;
    const bReached = reachedIds.has(b.milestone.id) ? 1 : 0;
    if (aReached !== bReached) return bReached - aReached;
    return b.progress_percent - a.progress_percent;
  });

  return (
    <div className="gamification__milestones">
      <h2 className="gamification__section-title">
        Milestones ({reachedMilestones.length} / {milestoneProgress.length})
      </h2>
      <div className="gamification__milestone-list">
        {sorted.map((mp) => {
          const reached = mp.reached || reachedIds.has(mp.milestone.id);
          return (
            <div
              key={mp.milestone.id}
              className={`gamification__milestone-card ${reached ? 'gamification__milestone-card--reached' : ''}`}
            >
              <div className="gamification__milestone-header">
                <span className="gamification__milestone-name">
                  {reached ? '\u2705' : '\u26AA'} {mp.milestone.name}
                </span>
                <span className="gamification__milestone-points">
                  {reached ? `+${mp.milestone.points} pts` : `${mp.milestone.points} pts`}
                </span>
              </div>
              <span className="gamification__milestone-desc">{mp.milestone.description}</span>
              <span className="gamification__milestone-metric">
                {METRIC_LABELS[mp.milestone.metric] ?? mp.milestone.metric}
              </span>
              <div className="gamification__progress-bar">
                <div
                  className="gamification__progress-fill"
                  style={{ width: `${Math.min(mp.progress_percent, 100)}%` }}
                />
              </div>
              <span className="gamification__progress-text">
                {Math.round(mp.progress_percent)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
