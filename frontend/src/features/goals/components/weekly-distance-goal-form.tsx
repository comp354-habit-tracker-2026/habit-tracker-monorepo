import { type FormEvent, useState } from 'react';

import { useCreateWeeklyDistanceGoal } from '../api/create-weekly-distance-goal';
import { createWeeklyDistanceGoalSchema } from '../types/goal';

type WeeklyDistanceGoalFormProps = {
  onSuccess?: () => void;
};

export function WeeklyDistanceGoalForm({
  onSuccess,
}: WeeklyDistanceGoalFormProps) {
  const createWeeklyGoal = useCreateWeeklyDistanceGoal();
  const [targetDistance, setTargetDistance] = useState('');
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const parsedValue = Number(targetDistance);
    const result = createWeeklyDistanceGoalSchema.safeParse({
      targetDistance: parsedValue,
    });

    if (!result.success) {
      setValidationMessage(result.error.issues[0]?.message ?? 'Invalid target value.');
      return;
    }

    setValidationMessage(null);
    createWeeklyGoal.mutate(result.data, {
      onSuccess: () => {
        setTargetDistance('');
        onSuccess?.();
      },
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="targetDistance">Weekly target distance (km)</label>
        <input
          id="targetDistance"
          type="number"
          min="0"
          step="0.1"
          value={targetDistance}
          onChange={(event) => setTargetDistance(event.target.value)}
          placeholder="e.g. 25"
          required
        />
      </div>

      <button type="submit" disabled={createWeeklyGoal.isPending}>
        {createWeeklyGoal.isPending ? 'Saving…' : 'Save Weekly Goal'}
      </button>

      {validationMessage && <p role="alert">{validationMessage}</p>}
      {createWeeklyGoal.isError && (
        <p role="alert">{createWeeklyGoal.error.message}</p>
      )}
    </form>
  );
}
