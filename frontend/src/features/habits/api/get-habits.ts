import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Habit } from '../types/habit';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getHabits(): Promise<Habit[]> {
  const response = await apiClient.get<Habit[]>('/goals');
  return response as unknown as Habit[];
}

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated so any
// component can prefetch or invalidate without importing the hook.
// ---------------------------------------------------------------------------
export function getHabitsQueryOptions() {
  return queryOptions({
    queryKey: ['habits'],
    queryFn: getHabits,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useHabits() {
  return useQuery(getHabitsQueryOptions());
}
