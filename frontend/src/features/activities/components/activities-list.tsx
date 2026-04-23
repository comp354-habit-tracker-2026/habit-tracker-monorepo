import { useState, useMemo } from 'react';
import { ActivityListSkeleton } from './activity-list-skeleton';
import { ActivityCard } from './activity-card';
import { SortControl, type SortOption } from './sort-control';
import { SearchBar } from './search-bar';
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
 * Implements client-side sorting and searching
 */
export function ActivitiesList({ onActivityClick }: ActivitiesListProps) {
  const activitiesQuery = useActivities();
  const [sortOption, setSortOption] = useState<SortOption>('date-newest');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter and sort activities (client-side, no API re-fetch)
  // MUST be called unconditionally at top level (Rules of Hooks)
  const filteredAndSortedActivities = useMemo(() => {
    const allActivities = activitiesQuery.data ?? [];
    let result = [...allActivities];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter((activity) =>
        activity.activity_type.toLowerCase().includes(query) ||
        (activity.provider ?? '').toLowerCase().includes(query) ||
        activity.date.includes(query)
      );
    }

    // Apply sorting
    result.sort((a, b) => {
      switch (sortOption) {
        case 'date-newest':
          return new Date(b.date).getTime() - new Date(a.date).getTime();
        case 'date-oldest':
          return new Date(a.date).getTime() - new Date(b.date).getTime();
        case 'duration':
          return b.duration - a.duration;
        case 'distance':
          const aDistance = a.distance ?? 0;
          const bDistance = b.distance ?? 0;
          return bDistance - aDistance;
        default:
          return 0;
      }
    });

    return result;
  }, [activitiesQuery.data, searchQuery, sortOption]);

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

  const allActivities = activitiesQuery.data ?? [];

  // No results state (after filtering)
  if (filteredAndSortedActivities.length === 0 && allActivities.length > 0) {
    return (
      <div>
        <div className="activities-list__controls">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
          <SortControl value={sortOption} onChange={setSortOption} />
        </div>
        <div className="activities-list__no-results" role="status">
          <p className="activities-list__no-results-message">
            No activities match your search "{searchQuery}".
          </p>
          <button
            className="activities-list__clear-search"
            onClick={() => setSearchQuery('')}
          >
            Clear search
          </button>
        </div>
      </div>
    );
  }

  // Empty state (no activities at all)
  if (allActivities.length === 0) {
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

  // Success state - render list with controls
  return (
    <div>
      {/* Controls: Search and Sort */}
      <div className="activities-list__controls">
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
        <SortControl value={sortOption} onChange={setSortOption} />
      </div>
      
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
        {filteredAndSortedActivities.map((activity) => (
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
