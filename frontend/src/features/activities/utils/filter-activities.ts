import type { Activity } from '../types/activity';
import type { ActivityFilters } from '../types/filters';

export function filterActivities(
  activities: Activity[],
  filters: ActivityFilters
): Activity[] {
  return activities.filter((activity) => {
    const matchesType =
      filters.selectedTypes.length === 0 ||
      filters.selectedTypes.includes(activity.activity_type);

    const activityDate = new Date(activity.date);

    const matchesStartDate =
      !filters.startDate || activityDate >= new Date(filters.startDate);

    const matchesEndDate =
      !filters.endDate || activityDate <= new Date(filters.endDate);

    return matchesType && matchesStartDate && matchesEndDate;
  });
}//code developed from chatGPT