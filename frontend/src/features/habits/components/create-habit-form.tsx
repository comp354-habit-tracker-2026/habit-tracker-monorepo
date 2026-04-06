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
    title: '',
    description: '',
    target_value: 1,
    goal_type: 'custom',
    status: 'active',
    start_date: '',
    end_date: '',
  });

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    createHabit.mutate(values, { onSuccess });
  }

  return (
    <form onSubmit={handleSubmit}>

      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={values.title}
          onChange={(e) => setValues((v) => ({ ...v, title: e.target.value }))}
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
        <label htmlFor="target_value">Target Value</label>
        <input
          id="target_value"
          type="number"
          value={values.target_value}
          onChange={(e) => setValues((v) => ({ ...v, target_value: Number(e.target.value) }))}
          required
        />
      </div>

      <div>
        <label htmlFor="goal_type">Goal Type</label>
        <select
          id="goal_type"
          value={values.goal_type}
          onChange={(e) => setValues((v) => ({ ...v, goal_type: e.target.value as CreateHabitInput['goal_type'] }))}
        >
          <option value="distance">Distance</option>
          <option value="duration">Duration</option>
          <option value="frequency">Frequency</option>
          <option value="calories">Calories</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <div>
        <label htmlFor="status">Status</label>
        <select
          id="status"
          value={values.status}
          onChange={(e) => setValues((v) => ({ ...v, status: e.target.value as CreateHabitInput['status'] }))}
        >
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="paused">Paused</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div>
        <label htmlFor="start_date">Start Date</label>
        <input
          id="start_date"
          type="date"
          value={values.start_date}
          onChange={(e) => setValues((v) => ({ ...v, start_date: e.target.value }))}
          required
        />
      </div>

      <div>
        <label htmlFor="end_date">End Date</label>
        <input
          id="end_date"
          type="date"
          value={values.end_date}
          onChange={(e) => setValues((v) => ({ ...v, end_date: e.target.value }))}
          required
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
