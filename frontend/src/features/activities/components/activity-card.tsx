import type { Activity } from '../types/activity';
import { getActivityConfig } from '../types/activity';

type ActivityCardProps = {
  activity: Activity;
  onClick?: (activity: Activity) => void;
};

/**
 * AI-WRITTEN: Displays a single activity as a card with:
 * - Activity type icon and color coding
 * - Date, duration, distance
 * - Click handler for navigation to detail page
 */
export function ActivityCard({ activity, onClick }: ActivityCardProps) {
  const config = getActivityConfig(activity.activity_type);
  const formattedDate = new Date(activity.date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  const durationLabel = formatDuration(activity.duration);
  const distanceLabel =
    activity.distance !== null ? `${activity.distance} km` : null;

  return (
    <article
      className="activity-card"
      onClick={() => onClick?.(activity)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.(activity);
        }
      }}
      aria-label={`${activity.activity_type} on ${formattedDate}`}
    >
      <div className={`activity-card__icon ${config.color}`}>
        <span className="activity-card__emoji">{config.icon}</span>
      </div>
      <div className="activity-card__body">
        <header className="activity-card__header">
          <h3 className="activity-card__title">{activity.activity_type}</h3>
          <time className="activity-card__date" dateTime={activity.date}>
            {formattedDate}
          </time>
        </header>
        <dl className="activity-card__metrics">
          <div className="activity-card__metric">
            <dt className="activity-card__metric-label">Duration</dt>
            <dd className="activity-card__metric-value">{durationLabel}</dd>
          </div>
          {distanceLabel && (
            <div className="activity-card__metric">
              <dt className="activity-card__metric-label">Distance</dt>
              <dd className="activity-card__metric-value">{distanceLabel}</dd>
            </div>
          )}
          {activity.calories !== null && (
            <div className="activity-card__metric">
              <dt className="activity-card__metric-label">Calories</dt>
              <dd className="activity-card__metric-value">
                {activity.calories}
              </dd>
            </div>
          )}
        </dl>
      </div>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (remainingMinutes === 0) {
    return `${hours}h`;
  }
  return `${hours}h ${remainingMinutes}m`;
}
