import { z } from 'zod';

export type Goal = {
  id: number;
  title: string;
  description: string;
  target_value: string;
  current_value: string;
  goal_type: 'distance' | 'duration' | 'frequency' | 'calories' | 'custom';
  status: 'active' | 'completed' | 'paused' | 'failed';
  start_date: string;
  end_date: string;
  progress_percentage: string | number;
  created_at: string;
  updated_at: string;
};

export const createWeeklyDistanceGoalSchema = z.object({
  targetDistance: z
    .number({ message: 'Target distance is required.' })
    .positive('Target distance must be greater than 0.')
    .max(1000, 'Distance goals must be realistic. Please use a value up to 1000.'),
});

export type CreateWeeklyDistanceGoalInput = z.infer<
  typeof createWeeklyDistanceGoalSchema
>;
