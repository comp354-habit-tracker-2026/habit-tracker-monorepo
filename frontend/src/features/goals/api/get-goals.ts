import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Goal } from '../types/goal';

const getGoals = async (): Promise<Goal[]> => {
  const res = await apiClient.get('/goals/');
  return res.data;
};

export const useGoals = () => {
  return useQuery({
    queryKey: ['goals'],
    queryFn: getGoals,
  });
};
