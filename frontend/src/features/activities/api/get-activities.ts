import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Activity } from '../types/activity';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getActivities(): Promise<Activity[]> {
  const response = await apiClient.get<{ results: Activity[] }>('/api/v1/activities/');
  return (response as unknown as { results: Activity[] }).results;
}

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated
// ---------------------------------------------------------------------------
export function getActivitiesQueryOptions() {
  return queryOptions({
    queryKey: ['activities'],
    queryFn: getActivities,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useActivities() {
  return useQuery(getActivitiesQueryOptions());
}
