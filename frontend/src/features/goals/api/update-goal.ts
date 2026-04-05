import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

//instead of just sending back id and string aslo added target value that actually got updated
type UpdateGoalInput = {
  id: number;
  title?: string;
  target_value?: number;
};

const updateGoal = async ({ id, title }: UpdateGoalInput) => {
  const res = await apiClient.patch(`/goals/${id}/`, { title });
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
