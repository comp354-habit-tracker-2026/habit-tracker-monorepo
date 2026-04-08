import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Goal } from '../types/goal';

type PaginatedResponse<T> = {
  count: number;
  results: T[];
};

async function getGoals(): Promise<Goal[]> {
  const response = await apiClient.get<PaginatedResponse<Goal>>('/goals/');
  const payload = response as unknown as PaginatedResponse<Goal>;
  return payload.results ?? [];
}

export function getGoalsQueryOptions() {
  return queryOptions({
    queryKey: ['goals'],
    queryFn: getGoals,
  });
}

export function useGoals() {
  return useQuery(getGoalsQueryOptions());
}
