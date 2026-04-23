import { useState } from 'react';
import type { Goal } from '../types/goal';
import { useDeleteGoal } from '../api/delete-goal';
import { useUpdateGoal } from '../api/update-goal';
import '../goals-ui.css';
import { Circle, PauseCircle, AlertCircle, CheckCircle,PlayCircle } from 'lucide-react';

const formatNumber = (value: string | number) => {
  const num = Number(value);

  if (Number.isNaN(num)) return '0';

  return Number.isInteger(num) ? String(num) : String(parseFloat(num.toFixed(1)));
};

const getOverdueInfo = (status: Goal['status'], endDate: string) => {
  if (status !== 'active' || !endDate) {
    return { effectiveStatus: status, overdueDays: 0, isOverdue: false };
  }

  const today = new Date();
  const end = new Date(endDate);

  today.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);

  const diffMs = today.getTime() - end.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays > 0) {
    return {
      effectiveStatus: 'failed' as const,
      overdueDays: diffDays,
      isOverdue: true,
    };
  }

  return { effectiveStatus: status, overdueDays: 0, isOverdue: false };
};

type Props = {
  goal: Goal;
  mode: 'api' | 'mock';
  onDelete?: (id: number) => void;
  onUpdate?: (id: number, updates: Partial<Goal>) => void;
};



const goalUnits: Record<string, string> = {
  distance: 'km',
  frequency: 'workouts',
  duration: 'min',
  calories: 'kcal',
  custom: '',
};

export const GoalCard = ({ goal, mode, onDelete, onUpdate }: Props) => {
  const { mutate: deleteGoal } = useDeleteGoal();
  const { mutate: updateGoal } = useUpdateGoal();

  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(goal.title);

  const progress = Math.max(0, Math.min(100, Number(goal.progress_percentage) || 0));
  const remaining = Math.max(0, Number(goal.target_value) - Number(goal.current_value));
  const unit = goalUnits[goal.goal_type] ?? '';

  const { effectiveStatus, overdueDays, isOverdue } = getOverdueInfo(
    goal.status,
    goal.end_date
  );
const StatusIcon = isOverdue
  ? AlertCircle
  : effectiveStatus === 'completed'
  ? CheckCircle
  : effectiveStatus === 'paused'
  ? PauseCircle
  : PlayCircle;

  const isPaused = effectiveStatus === 'paused';
  const isComplete = progress >= 100 || effectiveStatus === 'completed';

const themeClass = isOverdue
  ? 'goal-theme-failed'
  : isPaused
  ? 'goal-theme-paused'
  : isComplete
  ? 'goal-theme-completed'
  : 'goal-theme-active';

  const handleDelete = () => {
    if (mode === 'mock') {
      onDelete?.(goal.id);
    } else {
      deleteGoal(goal.id);
    }
  };

  const handleUpdate = () => {
    if (mode === 'mock') {
      onUpdate?.(goal.id, { title });
    } else {
      updateGoal({ id: goal.id, title });
    }

    setIsEditing(false);
  };

  const handleTogglePause = () => {
    const newStatus = isPaused ? 'active' : 'paused';

    if (mode === 'mock') {
      onUpdate?.(goal.id, { status: newStatus });
    } else {
      updateGoal({ id: goal.id, status: newStatus });
    }
  };

  return (
    <div className={`goal-card ${themeClass}`}>
      <div className="goal-card-top">
        <div className="goal-card-left">
          <div className="goal-card-title-row">
<StatusIcon className="goal-card-icon" size={20} />            {isEditing ? (
              <div className="goal-card-input-row">
                <input
                  className="goal-card-input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
                <button
                  onClick={handleUpdate}
                  className="goal-card-btn goal-card-btn-save"
                >
                  Save
                </button>
              </div>
            ) : (
              <>
                <h3 className="goal-card-title">{goal.title}</h3>

                {isOverdue ? (
                  <span className="goal-badge-overdue">Past Due</span>
                ) : null}

                {isPaused ? (
                  <span className="goal-badge-paused">Paused</span>
                ) : null}
              </>
            )}
          </div>

          {goal.description ? (
            <p className="goal-card-description">{goal.description}</p>
          ) : null}

          <p className="goal-card-value">
            {formatNumber(goal.current_value)} / {formatNumber(goal.target_value)} {unit}
          </p>
        </div>

<div className="goal-card-right" />
      </div>

<div className="goal-progress-wrap">
  <div className="goal-progress-track">
    <div
      className="goal-progress-fill"
      style={{ width: `${progress}%` }}
    />
  </div>

  {isComplete ? (
    <span className="goal-badge-complete goal-badge-complete--onbar">
      ✓ Complete
    </span>
  ) : null}
</div>

      <div className="goal-card-meta">
        <p className="goal-card-percent">{Math.round(progress)}% completed</p>

        {isOverdue ? (
          <p className="goal-card-overdue-text">
            Overdue by {overdueDays} {overdueDays === 1 ? 'day' : 'days'}
          </p>
        ) : isPaused ? (
          <p className="goal-card-paused-text">On hold</p>
        ) : !isComplete ? (
          <p className="goal-card-remaining">
            {formatNumber(remaining)} {unit} remaining
          </p>
        ) : null}
      </div>

      <div className="goal-card-actions">
        {!isComplete ? (
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="goal-card-btn goal-card-btn-edit"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        ) : null}

        {!isComplete && !isOverdue ? (
          <button
            onClick={handleTogglePause}
            className="goal-card-btn goal-card-btn-pause"
          >
            {isPaused ? 'Resume' : 'Pause'}
          </button>
        ) : null}

        <button
          onClick={handleDelete}
          className="goal-card-btn goal-card-btn-delete"
        >
          Delete
        </button>
      </div>
    </div>
  );
};