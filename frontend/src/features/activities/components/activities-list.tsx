import { ActivityListSkeleton } from './activity-list-skeleton';
import { ActivityCard } from './activity-card';
import { useActivities } from '../api/get-activities';
import type { Activity } from '../types/activity';

type ActivitiesListProps = {
  onActivityClick?: (activity: Activity) => void;
};

/**
 * Renders the full list of user's activities.
 * Handles loading, error, and empty states.
 * Data fetching lives in the API layer (useActivities).
 * 
 * Adds refresh/sync functionality to re-trigger API calls
 */
export function ActivitiesList({ onActivityClick }: ActivitiesListProps) {
  const activitiesQuery = useActivities();

  // Loading state
  if (activitiesQuery.isLoading) {
    return <ActivityListSkeleton />;
  }

  // Error state
  if (activitiesQuery.isError) {
    return (
      <div className="activities-list__error" role="alert">
        <p className="activities-list__error-message">
          Failed to load activities. Please try again.
        </p>
        <button
          className="activities-list__retry-button"
          onClick={() => activitiesQuery.refetch()}
          disabled={activitiesQuery.isRefetching}
        >
          {activitiesQuery.isRefetching ? 'Retrying...' : 'Retry'}
        </button>
      </div>
    );
  }

  const activities = activitiesQuery.data ?? [];

  // Empty state
  if (activities.length === 0) {
    return (
      <div className="activities-list__empty" role="status">
        <p className="activities-list__empty-message">
          No activities yet. Start tracking your first activity!
        </p>
        {/*Refresh button for empty state */}
        <button
          className="activities-list__refresh-button"
          onClick={() => activitiesQuery.refetch()}
          disabled={activitiesQuery.isRefetching}
        >
          {activitiesQuery.isRefetching ? '⟳ Syncing...' : '⟳ Sync Activities'}
        </button>
      </div>
    );
  }

  // Success state - render list with refresh button
  return (
    <div>
      {/* AI-WRITTEN: Refresh/Sync button at top of list with loading indicator */}
      <div className="activities-list__header">
        <button
          className="activities-refresh-button"
          onClick={() => activitiesQuery.refetch()}
          disabled={activitiesQuery.isRefetching}
          aria-label="Refresh activities from Insights API"
        >
          <span className={activitiesQuery.isRefetching ? 'spin' : ''}>⟳</span>
          <span className="activities-refresh-button__text">
            {activitiesQuery.isRefetching ? 'Syncing...' : 'Sync'}
          </span>
        </button>
      </div>
      <ul className="activities-list" role="list">
        {activities.map((activity) => (
          <li key={activity.id} className="activities-list__item">
            <ActivityCard
              activity={activity}
              onClick={onActivityClick}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
