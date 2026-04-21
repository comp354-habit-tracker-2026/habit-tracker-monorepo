import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

type UpdateGoalInput = {
  id: number;
  title?: string;
  target_value?: number;
  status?: 'active' | 'completed' | 'paused' | 'failed';
};

const updateGoal = async ({ id, ...updates }: UpdateGoalInput) => {
  const res = await apiClient.patch(`/goals/${id}/`, updates);
  return res;
};

export const useUpdateGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    },
  });
};