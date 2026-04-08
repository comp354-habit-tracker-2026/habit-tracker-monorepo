import { type BadgeProgress, type UserBadge } from '../types/gamification';

type BadgeGridProps = {
  badgeProgress: BadgeProgress[];
  earnedBadges: UserBadge[];
};

const BADGE_TYPE_LABELS: Record<string, string> = {
  single: 'Single Activity',
  cumulative: 'Cumulative',
  streak: 'Streak',
  frequency: 'Weekly',
};

export function BadgeGrid({ badgeProgress, earnedBadges }: BadgeGridProps) {
  const earnedIds = new Set(earnedBadges.map((ub) => ub.badge.id));

  // Show earned badges first, then in-progress sorted by highest progress
  const sorted = [...badgeProgress].sort((a, b) => {
    const aEarned = earnedIds.has(a.badge.id) ? 1 : 0;
    const bEarned = earnedIds.has(b.badge.id) ? 1 : 0;
    if (aEarned !== bEarned) return bEarned - aEarned;
    return b.progress_percent - a.progress_percent;
  });

  return (
    <div className="gamification__badges">
      <h2 className="gamification__section-title">
        Badges ({earnedBadges.length} / {badgeProgress.length})
      </h2>
      <div className="gamification__badge-grid">
        {sorted.map((bp) => {
          const earned = bp.earned || earnedIds.has(bp.badge.id);
          return (
            <div
              key={bp.badge.id}
              className={`gamification__badge-card ${earned ? 'gamification__badge-card--earned' : ''}`}
            >
              <div className="gamification__badge-icon">
                {earned ? badgeIcon(bp.badge.badge_type) : lockedIcon()}
              </div>
              <div className="gamification__badge-info">
                <span className="gamification__badge-name">{bp.badge.name}</span>
                <span className="gamification__badge-type">
                  {BADGE_TYPE_LABELS[bp.badge.badge_type] ?? bp.badge.badge_type}
                </span>
                <span className="gamification__badge-desc">{bp.badge.description}</span>
              </div>
              <div className="gamification__badge-progress">
                <div className="gamification__progress-bar">
                  <div
                    className="gamification__progress-fill"
                    style={{ width: `${Math.min(bp.progress_percent, 100)}%` }}
                  />
                </div>
                <span className="gamification__progress-text">
                  {earned ? `+${bp.badge.points} pts` : `${Math.round(bp.progress_percent)}%`}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function badgeIcon(type: string) {
  const icons: Record<string, string> = {
    single: '\u2B50',    // star
    cumulative: '\uD83C\uDFC6', // trophy
    streak: '\uD83D\uDD25',    // fire
    frequency: '\uD83D\uDD01', // repeat
  };
  return <span className="gamification__icon">{icons[type] ?? '\uD83C\uDFC5'}</span>;
}

function lockedIcon() {
  return <span className="gamification__icon gamification__icon--locked">{'\uD83D\uDD12'}</span>;
}
