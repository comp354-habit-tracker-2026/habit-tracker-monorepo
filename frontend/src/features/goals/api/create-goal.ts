import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

type CreateGoalInput = {
  title: string;
  target_value: number;
  goal_type: string;
};

const createGoal = async (data: CreateGoalInput) => {
  const res = await apiClient.post('/goals/', data);
  return res.data;
};

export const useCreateGoal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    },
  });
};
