import { z } from 'zod';

// ---------------------------------------------------------------------------
// Domain type
// ---------------------------------------------------------------------------
export type Habit = {
  id: string;
  title: string;
  description: string;
  target_value: number;
  current_value: number;
  goal_type: 'distance' | 'duration' | 'frequency' | 'calories' | 'custom';
  status: 'active' | 'completed' | 'paused' | 'failed';
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
};

// ---------------------------------------------------------------------------
// Zod schemas – used for form validation and API response parsing
// ---------------------------------------------------------------------------
export const createHabitSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().max(500).optional(),
  target_value: z.number().min(0.01, 'Target value is required'),
  goal_type: z.enum(['distance', 'duration', 'frequency', 'calories', 'custom']),
  status: z.enum(['active', 'completed', 'paused', 'failed']).default('active'),
  start_date: z.string(),
  end_date: z.string(),
});

export type CreateHabitInput = z.infer<typeof createHabitSchema>;

export const updateHabitSchema = createHabitSchema.partial();
export type UpdateHabitInput = z.infer<typeof updateHabitSchema>;
