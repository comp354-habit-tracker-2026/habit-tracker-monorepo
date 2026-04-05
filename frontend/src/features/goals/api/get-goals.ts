import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Goal } from '../types/goal';

type GoalsResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Goal[];
};

const getGoals = async (): Promise<Goal[]> => {
  const data = (await apiClient.get('/goals/')) as GoalsResponse;

  console.log('API RESPONSE:', data);

  return data.results ?? [];
};

export const useGoals = () => {
  return useQuery({
    queryKey: ['goals'],
    queryFn: getGoals,
  });
};
