import { useMemo, useState } from 'react';

import { ActivityListSkeleton } from './activity-list-skeleton';
import { ActivityCard } from './activity-card';
import { SortControl, type SortOption } from './sort-control';
import { SearchBar } from './search-bar';
import { FilterBar } from './filter-bar';

import { useActivities } from '../api/get-activities';
import type { Activity } from '../types/activity';
import type { ActivityFilters } from '../types/filters';

type ActivitiesListProps = {
  onActivityClick?: (activity: Activity) => void;
};

export function ActivitiesList({ onActivityClick }: ActivitiesListProps) {
  const activitiesQuery = useActivities();

  const [sortOption, setSortOption] = useState<SortOption>('date-newest');
  const [searchQuery, setSearchQuery] = useState('');

  const [filters, setFilters] = useState<ActivityFilters>({
    selectedTypes: [],
    startDate: '',
    endDate: '',
  });

  // Combined filtering + search + sorting
  const processedActivities = useMemo(() => {
    const all = activitiesQuery.data ?? [];
    let result = [...all];

    // Search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter((activity) =>
        activity.activity_type.toLowerCase().includes(query) ||
        (activity.provider ?? '').toLowerCase().includes(query) ||
        activity.date.includes(query)
      );
    }

    // Filter (your feature)
    result = filterActivities(result, filters);

    // Sort
    result.sort((a, b) => {
      switch (sortOption) {
        case 'date-newest': {
          const dateB = new Date(b.date).getTime();
          const dateA = new Date(a.date).getTime();
          return dateB - dateA;
        }
        case 'date-oldest': {
          const dateA = new Date(a.date).getTime();
          const dateB = new Date(b.date).getTime();
          return dateA - dateB;
        }
        case 'duration': {
          return b.duration - a.duration;
        }
        case 'distance': {
          const distanceB = b.distance ?? 0;
          const distanceA = a.distance ?? 0;
          return distanceB - distanceA;
        }
        default:
          return 0;
      }
    });

    return result;
  }, [activitiesQuery.data, searchQuery, sortOption, filters]);

  if (activitiesQuery.isLoading) return <ActivityListSkeleton />;

  if (activitiesQuery.isError) {
    return <p>Failed to load activities.</p>;
  }

  const allActivities = activitiesQuery.data ?? [];

  const availableTypes = Array.from(
    new Set(allActivities.map((a) => a.activity_type))
  ).sort();

  if (allActivities.length === 0) {
    return <p>No activities yet.</p>;
  }

  return (
    <div>
      {/* Controls */}
      <div className="activities-list__controls">
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
        <SortControl value={sortOption} onChange={setSortOption} />
      </div>

      <FilterBar
        availableTypes={availableTypes}
        selectedTypes={filters.selectedTypes}
        startDate={filters.startDate}
        endDate={filters.endDate}
        onTypeToggle={(type) => {
          setFilters((prev) => ({
            ...prev,
            selectedTypes: prev.selectedTypes.includes(type)
              ? prev.selectedTypes.filter((t) => t !== type)
              : [...prev.selectedTypes, type],
          }));
        }}
        onStartDateChange={(value: string) =>
          setFilters((prev) => ({ ...prev, startDate: value }))
        }
        onEndDateChange={(value: string) =>
          setFilters((prev) => ({ ...prev, endDate: value }))
        }
        onClearFilters={() =>
          setFilters({ selectedTypes: [], startDate: '', endDate: '' })
        }
      />

      <p>
        Showing {processedActivities.length} of {allActivities.length} activities
      </p>

      <ul>
        {processedActivities.map((activity) => (
          <li key={activity.id}>
            <ActivityCard activity={activity} onClick={onActivityClick} />
          </li>
        ))}
      </ul>
    </div>
  );
}

function filterActivities(
  activities: Activity[],
  filters: ActivityFilters
): Activity[] {
  return activities.filter((activity) => {
    const matchesType =
      filters.selectedTypes.length === 0 ||
      filters.selectedTypes.includes(activity.activity_type);

    const activityDate = new Date(activity.date);

    const matchesStartDate =
      !filters.startDate ||
      activityDate >= new Date(`${filters.startDate}T00:00:00`);

    const matchesEndDate =
      !filters.endDate ||
      activityDate <= new Date(`${filters.endDate}T23:59:59.999`);

    return matchesType && matchesStartDate && matchesEndDate;
  });
}

