import { useMutation, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type CreateHabitInput, type Habit } from '../types/habit';
import { getHabitsQueryOptions } from './get-habits';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function createHabit(data: CreateHabitInput): Promise<Habit> {
  const response = await apiClient.post<Habit>('/goals', data);
  return response as unknown as Habit;
}

// ---------------------------------------------------------------------------
// Mutation hook
// ---------------------------------------------------------------------------
export function useCreateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      // Invalidate the habits list so it refetches after creation
      queryClient.invalidateQueries({
        queryKey: getHabitsQueryOptions().queryKey,
      });
    },
  });
}
