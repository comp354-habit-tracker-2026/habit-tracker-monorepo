import { useMutation, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import { type ApiResponse } from '@/types/api';

import { type CreateHabitInput, type Habit } from '../types/habit';
import { getHabitsQueryOptions } from './get-habits';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function createHabit(data: CreateHabitInput): Promise<Habit> {
  const response = await apiClient.post<ApiResponse<Habit>>('/habits', data);
  return (response as unknown as ApiResponse<Habit>).data;
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
