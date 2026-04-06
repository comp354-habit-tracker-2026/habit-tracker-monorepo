import { type FormEvent, useState } from 'react';

import { useCreateHabit } from '../api/create-habit';
import { type CreateHabitInput } from '../types/habit';

type CreateHabitFormProps = {
  onSuccess?: () => void;
};

/**
 * Controlled form for creating a new habit.
 *
 * Validation is intentionally kept simple here. For complex forms,
 * integrate React Hook Form + Zod (see createHabitSchema in types/habit.ts).
 */
export function CreateHabitForm({ onSuccess }: CreateHabitFormProps) {
  const createHabit = useCreateHabit();

  const [values, setValues] = useState<CreateHabitInput>({
    name: '',
    description: '',
    frequency: 'daily',
  });

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    createHabit.mutate(values, { onSuccess });
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={values.name}
          onChange={(e) => setValues((v) => ({ ...v, name: e.target.value }))}
          required
        />
      </div>

      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={values.description}
          onChange={(e) =>
            setValues((v) => ({ ...v, description: e.target.value }))
          }
        />
      </div>

      <div>
        <label htmlFor="frequency">Frequency</label>
        <select
          id="frequency"
          value={values.frequency}
          onChange={(e) =>
            setValues((v) => ({
              ...v,
              frequency: e.target.value as 'daily' | 'weekly',
            }))
          }
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
        </select>
      </div>

      <button type="submit" disabled={createHabit.isPending}>
        {createHabit.isPending ? 'Saving…' : 'Create Habit'}
      </button>

      {createHabit.isError && <p role="alert">{createHabit.error.message}</p>}
    </form>
  );
}
