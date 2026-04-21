export type GoalType =
  | 'distance'
  | 'duration'
  | 'frequency'
  | 'calories'
  | 'custom';

export type GoalStatus =
  | 'active'
  | 'completed'
  | 'paused'
  | 'failed';

export type Goal = {
  id: number;
  title: string;
  description: string;
  target_value: number | string;
  current_value: number | string;
  progress_percentage: number | string;
  goal_type: GoalType;
  status: GoalStatus;
  start_date: string;
  end_date: string;
  created_at?: string;
  updated_at?: string;
};