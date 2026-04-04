import { useState } from 'react';
import { useCreateGoal } from '../api/create-goal';

export const CreateGoalForm = () => {
  const { mutate, isPending } = useCreateGoal();

  const [title, setTitle] = useState('');
  const [target, setTarget] = useState(10);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    mutate({
      title,
      target_value: target,
      goal_type: 'total',
    });

    setTitle('');
    setTarget(10);
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="flex gap-2">
        <input
          className="border p-2 rounded w-full"
          placeholder="Goal name"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <input
          type="number"
          className="border p-2 rounded w-24"
          value={target}
          onChange={(e) => setTarget(Number(e.target.value))}
        />

        <button
          type="submit"
          className="bg-blue-500 text-white px-3 rounded"
          disabled={isPending}
        >
          Add
        </button>
      </div>
    </form>
  );
};
