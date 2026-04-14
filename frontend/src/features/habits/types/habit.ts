import { z } from 'zod';

// ---------------------------------------------------------------------------
// Domain type
// ---------------------------------------------------------------------------
export type Habit = {
  id: string;
  name: string;
  description: string;
  frequency: 'daily' | 'weekly';
  createdAt: string;
  updatedAt: string;
};

// ---------------------------------------------------------------------------
// Zod schemas – used for form validation and API response parsing
// ---------------------------------------------------------------------------
export const createHabitSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  frequency: z.enum(['daily', 'weekly']),
});

export type CreateHabitInput = z.infer<typeof createHabitSchema>;

export const updateHabitSchema = createHabitSchema.partial();
export type UpdateHabitInput = z.infer<typeof updateHabitSchema>;
