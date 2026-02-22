import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import { type ApiResponse } from '@/types/api';

import { type Habit } from '../types/habit';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getHabits(): Promise<Habit[]> {
  const response = await apiClient.get<ApiResponse<Habit[]>>('/habits');
  return (response as unknown as ApiResponse<Habit[]>).data;
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
