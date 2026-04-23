import { useState } from 'react';
import { useCreateGoal } from '../api/create-goal';
import type { Goal, GoalType } from '../types/goal';
import '../goals-ui.css';

type CreateGoalFormProps = {
  mode: 'api' | 'mock';
  onCreateMock?: (goal: Goal) => void;
};

export const CreateGoalForm = ({ mode, onCreateMock }: CreateGoalFormProps) => {
  const { mutate, isPending } = useCreateGoal();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [target, setTarget] = useState(10);
  const [type, setType] = useState<GoalType>('custom');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setTarget(10);
    setType('custom');
    setStartDate('');
    setEndDate('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title || !startDate || !endDate) {
      alert('Fill all required fields');
      return;
    }

    if (mode === 'mock') {
      const nowIso = new Date().toISOString();

      const newGoal: Goal = {
        id: Date.now(),
        title,
        description: description.trim(),
        target_value: target,
        current_value: 0,
        progress_percentage: 0,
        goal_type: type,
        status: 'active',
        start_date: startDate,
        end_date: endDate,
        created_at: nowIso,
        updated_at: nowIso,
      };

      onCreateMock?.(newGoal);
      resetForm();
      return;
    }

    mutate(
      {
        title,
        description: description.trim() || undefined,
        target_value: target,
        goal_type: type,
        start_date: startDate,
        end_date: endDate,
      },
      {
        onSuccess: () => {
          resetForm();
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="goals-form-grid">
        <input
          className="goals-input"
          placeholder="Goal name"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <input
          type="number"
          className="goals-input"
          value={target}
          onChange={(e) => setTarget(Number(e.target.value))}
          placeholder="Target value"
          min="0"
        />

        <select
          className="goals-select"
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
          className="goals-input"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <input
          type="date"
          className="goals-input"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />
      </div>

      <textarea
        className="goals-textarea"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <button
        type="submit"
        className="goals-submit-btn"
        disabled={mode === 'api' ? isPending : false}
      >
        + Set New Goal
      </button>
    </form>
  );
};