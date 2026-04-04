import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

type UpdateGoalInput = {
  id: number;
  title: string;
};

const updateGoal = async ({ id, title }: UpdateGoalInput) => {
  const res = await apiClient.patch(`/goals/${id}/`, { title });
  return res.data;
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
