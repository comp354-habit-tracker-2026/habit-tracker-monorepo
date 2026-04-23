import { useGoals } from '../api/get-goals';

function toNumeric(value: string | number): number {
  if (typeof value === 'number') return value;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

export function GoalsList() {
  const goalsQuery = useGoals();

  if (goalsQuery.isLoading) return <p>Loading goals…</p>;
  if (goalsQuery.isError) return <p>Failed to load goals.</p>;

  const goals = (goalsQuery.data ?? []).filter((goal) => goal.goal_type === 'distance');

  if (goals.length === 0) {
    return <p>No distance goals yet. Set your first weekly target.</p>;
  }

  return (
    <ul>
      {goals.map((goal) => {
        const progress = toNumeric(goal.progress_percentage);

        return (
          <li key={goal.id}>
            <strong>{goal.title}</strong>
            <p>
              Target: {goal.target_value} km | Current: {goal.current_value} km | Progress:{' '}
              {progress.toFixed(1)}%
            </p>
          </li>
        );
      })}
    </ul>
  );
}
