import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

//updated this part so it matches the backend goals model
type CreateGoalInput = {
  title: string;
  description?: string;
  target_value: number;
  goal_type: 'distance' | 'duration' | 'frequency' | 'calories' | 'custom';
  start_date: string;
  end_date: string;
};

const createGoal = async (data: CreateGoalInput) => {
  const res = await apiClient.post('/goals/', data);
  return res;
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
