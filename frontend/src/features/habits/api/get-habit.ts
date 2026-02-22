import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import { type ApiResponse } from '@/types/api';

import { type Habit } from '../types/habit';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getHabit({ habitId }: { habitId: string }): Promise<Habit> {
  const response = await apiClient.get<ApiResponse<Habit>>(
    `/habits/${habitId}`,
  );
  return (response as unknown as ApiResponse<Habit>).data;
}

// ---------------------------------------------------------------------------
// Query options factory
// ---------------------------------------------------------------------------
export function getHabitQueryOptions(habitId: string) {
  return queryOptions({
    queryKey: ['habits', habitId],
    queryFn: () => getHabit({ habitId }),
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useHabit({ habitId }: { habitId: string }) {
  return useQuery(getHabitQueryOptions(habitId));
}
