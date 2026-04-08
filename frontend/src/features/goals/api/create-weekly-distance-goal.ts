import { useMutation, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import {
  type CreateWeeklyDistanceGoalInput,
  type Goal,
} from '../types/goal';
import { getGoalsQueryOptions } from './get-goals';

type GoalPayload = {
  title: string;
  description: string;
  target_value: number;
  goal_type: 'distance';
  start_date: string;
  end_date: string;
};

function toLocalDateString(value: Date): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function buildWeeklyGoalPayload(input: CreateWeeklyDistanceGoalInput): GoalPayload {
  const startDate = new Date();
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 6);

  return {
    title: `Weekly Distance Goal (${input.targetDistance} km)`,
    description: 'Auto-generated weekly distance target.',
    target_value: Number(input.targetDistance.toFixed(2)),
    goal_type: 'distance',
    start_date: toLocalDateString(startDate),
    end_date: toLocalDateString(endDate),
  };
}

async function createWeeklyDistanceGoal(
  input: CreateWeeklyDistanceGoalInput,
): Promise<Goal> {
  const payload = buildWeeklyGoalPayload(input);
  const response = await apiClient.post<Goal>('/goals/', payload);
  return response as unknown as Goal;
}

export function useCreateWeeklyDistanceGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createWeeklyDistanceGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: getGoalsQueryOptions().queryKey,
      });
    },
  });
}
