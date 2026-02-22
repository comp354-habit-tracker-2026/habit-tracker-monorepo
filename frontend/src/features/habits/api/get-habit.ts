import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Habit } from '../types/habit';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getHabit({ habitId }: { habitId: string }): Promise<Habit> {
  const response = await apiClient.get<Habit>(`/habits/${habitId}`);
  return response as unknown as Habit;
}

// ---------------------------------------------------------------------------
// Query options factory
// ---------------------------------------------------------------------------
export function getHabitQueryOptions(habitId: string | undefined) {
  return queryOptions({
    queryKey: ['habits', habitId],
    queryFn: () => getHabit({ habitId: habitId! }),
    enabled: !!habitId,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useHabit({ habitId }: { habitId: string | undefined }) {
  return useQuery(getHabitQueryOptions(habitId));
}
