import { Link } from 'react-router';

import { paths } from '@/config/paths';

import { useHabits } from '../api/get-habits';

/**
 * Renders the full list of the user's habits.
 * Data fetching lives in the API layer (useHabits), not here.
 */
export function HabitsList() {
  const habitsQuery = useHabits();

  if (habitsQuery.isLoading) return <p>Loading habits…</p>;
  if (habitsQuery.isError) return <p>Failed to load habits.</p>;

  const habits = habitsQuery.data ?? [];

  if (habits.length === 0) {
    return <p>No habits yet. Create your first one!</p>;
  }

  return (
    <ul>
      {habits.map((habit) => (
        <li key={habit.id}>
          <Link to={paths.app.habit.getHref(habit.id)}>{habit.name}</Link>
          {habit.description && <span> – {habit.description}</span>}
        </li>
      ))}
    </ul>
  );
}
