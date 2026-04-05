//changed the entire form
import { useState } from 'react';
import { useCreateGoal } from '../api/create-goal';

export const CreateGoalForm = () => {
  const { mutate, isPending } = useCreateGoal();

  const [title, setTitle] = useState('');
  const [target, setTarget] = useState(10);
  type GoalType = 'distance' | 'duration' | 'frequency' | 'calories' | 'custom';
  const [type, setType] = useState<GoalType>('custom');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title || !startDate || !endDate) {
      alert('Fill all fields');
      return;
    }

    mutate({
      title,
      target_value: target,
      goal_type: type,
      start_date: startDate,
      end_date: endDate,
    });

    setTitle('');
    setTarget(10);
    setStartDate('');
    setEndDate('');
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 space-y-2">
      <input
        className="border p-2 rounded w-full"
        placeholder="Goal name"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <input
        type="number"
        className="border p-2 rounded w-full"
        value={target}
        onChange={(e) => setTarget(Number(e.target.value))}
      />

      <select
        className="border p-2 rounded w-full"
        value={type}
        onChange={(e) => setType(e.target.value as GoalType)}
      >
        <option value="custom">Custom</option>
        <option value="distance">Distance</option>
        <option value="duration">Duration</option>
        <option value="frequency">Frequency</option>
        <option value="calories">Calories</option>
      </select>

      <input
        type="date"
        className="border p-2 rounded w-full"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
      />

      <input
        type="date"
        className="border p-2 rounded w-full"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
      />

      <button
        type="submit"
        className="bg-blue-500 text-white px-3 py-2 rounded"
        disabled={isPending}
      >
        Add Goal
      </button>
    </form>
  );
};
