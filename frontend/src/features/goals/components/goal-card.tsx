import { useState } from 'react';
import type { Goal } from '../types/goal';
import { useDeleteGoal } from '../api/delete-goal';
import { useUpdateGoal } from '../api/update-goal';

type Props = {
  goal: Goal;
};

export const GoalCard = ({ goal }: Props) => {
  const { mutate: deleteGoal } = useDeleteGoal();
  const { mutate: updateGoal } = useUpdateGoal();

  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(goal.title);

  const handleDelete = () => {
    deleteGoal(goal.id);
  };

  const handleUpdate = () => {
    updateGoal({ id: goal.id, title });
    setIsEditing(false);
  };

  return (
    <div className="p-4 border rounded-xl shadow-sm bg-white">
      {isEditing ? (
        <div className="flex gap-2 mb-2">
          <input
            className="border p-1 rounded w-full"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <button
            onClick={handleUpdate}
            className="bg-green-500 text-white px-2 rounded"
          >
            Save
          </button>
        </div>
      ) : (
        <h3 className="font-semibold text-lg">{goal.title}</h3>
      )}

      <p className="text-sm text-gray-500">
        {goal.current_value} / {goal.target_value}
      </p>

      <div className="w-full bg-gray-200 h-2 rounded mt-2">
        <div
          className="bg-blue-500 h-2 rounded"
          style={{ width: `${goal.progress_percentage}%` }}
        />
      </div>

      <p className="text-xs mt-1 text-gray-600">
        {goal.progress_percentage}% complete
      </p>

      <div className="flex gap-2 mt-3">
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="text-sm px-2 py-1 bg-gray-200 rounded"
        >
          Edit
        </button>

        <button
          onClick={handleDelete}
          className="text-sm px-2 py-1 bg-red-500 text-white rounded"
        >
          Delete
        </button>
      </div>
    </div>
  );
};
