import { useMemo, useState } from 'react';

import { ContentLayout } from '@/components/layouts/content-layout';

type GoalStatus = 'active' | 'completed';

type Goal = {
  id: number;
  title: string;
  activityType: string;
  targetValue: number;
  currentProgress: number;
  unit: string;
  deadline: string;
  status: GoalStatus;
};

type GoalFormData = {
  title: string;
  activityType: string;
  targetValue: string;
  currentProgress: string;
  unit: string;
  deadline: string;
};

const initialGoals: Goal[] = [
  {
    id: 1,
    title: 'Run 20 km this month',
    activityType: 'Running',
    targetValue: 20,
    currentProgress: 8,
    unit: 'km',
    deadline: '2026-04-30',
    status: 'active',
  },
  {
    id: 2,
    title: 'Cycle 100 km this month',
    activityType: 'Cycling',
    targetValue: 100,
    currentProgress: 45,
    unit: 'km',
    deadline: '2026-04-30',
    status: 'active',
  },
  {
    id: 3,
    title: 'Walk 10,000 steps goal',
    activityType: 'Walking',
    targetValue: 10000,
    currentProgress: 10000,
    unit: 'steps',
    deadline: '2026-04-10',
    status: 'completed',
  },
];

const emptyForm: GoalFormData = {
  title: '',
  activityType: 'Running',
  targetValue: '',
  currentProgress: '',
  unit: 'km',
  deadline: '',
};

export default function GoalsRoute() {
  const [goals, setGoals] = useState<Goal[]>(initialGoals);
  const [selectedFilter, setSelectedFilter] = useState<'all' | GoalStatus>('all');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingGoalId, setEditingGoalId] = useState<number | null>(null);
  const [formData, setFormData] = useState<GoalFormData>(emptyForm);
  const [formError, setFormError] = useState('');

  const filteredGoals = useMemo(() => {
    if (selectedFilter === 'all') {
      return goals;
    }

    return goals.filter((goal) => goal.status === selectedFilter);
  }, [goals, selectedFilter]);

  const activeGoals = filteredGoals.filter((goal) => goal.status === 'active');
  const completedGoals = filteredGoals.filter((goal) => goal.status === 'completed');

  function openCreateForm() {
    setEditingGoalId(null);
    setFormData(emptyForm);
    setFormError('');
    setIsFormOpen(true);
  }

  function openEditForm(goal: Goal) {
    setEditingGoalId(goal.id);
    setFormData({
      title: goal.title,
      activityType: goal.activityType,
      targetValue: String(goal.targetValue),
      currentProgress: String(goal.currentProgress),
      unit: goal.unit,
      deadline: goal.deadline,
    });
    setFormError('');
    setIsFormOpen(true);
  }

  function closeForm() {
    setIsFormOpen(false);
    setEditingGoalId(null);
    setFormData(emptyForm);
    setFormError('');
  }

  function handleInputChange(
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError('');

    const trimmedTitle = formData.title.trim();
    const parsedTarget = Number(formData.targetValue);
    const parsedProgress = Number(formData.currentProgress);

    if (!trimmedTitle) {
      setFormError('Goal title is required.');
      return;
    }

    if (!formData.deadline) {
      setFormError('Please choose a deadline.');
      return;
    }

    if (Number.isNaN(parsedTarget) || parsedTarget <= 0) {
      setFormError('Target value must be greater than 0.');
      return;
    }

    if (Number.isNaN(parsedProgress) || parsedProgress < 0) {
      setFormError('Current progress cannot be negative.');
      return;
    }

    // code generated using ChatGPT: keep status automatically aligned with progress
    // so a goal becomes completed when progress reaches or exceeds target
    const derivedStatus: GoalStatus =
      parsedProgress >= parsedTarget ? 'completed' : 'active';

    if (editingGoalId !== null) {
      setGoals((prevGoals) =>
        prevGoals.map((goal) =>
          goal.id === editingGoalId
            ? {
                ...goal,
                title: trimmedTitle,
                activityType: formData.activityType,
                targetValue: parsedTarget,
                currentProgress: parsedProgress,
                unit: formData.unit,
                deadline: formData.deadline,
                status: derivedStatus,
              }
            : goal,
        ),
      );
    } else {
      // code generated using ChatGPT: derive next id from current items instead of
      // hardcoding one, which keeps local mock-data creation safer
      const nextId =
        goals.length > 0 ? Math.max(...goals.map((goal) => goal.id)) + 1 : 1;

      const newGoal: Goal = {
        id: nextId,
        title: trimmedTitle,
        activityType: formData.activityType,
        targetValue: parsedTarget,
        currentProgress: parsedProgress,
        unit: formData.unit,
        deadline: formData.deadline,
        status: derivedStatus,
      };

      setGoals((prevGoals) => [newGoal, ...prevGoals]);
    }

    closeForm();
  }

  function getProgressPercentage(goal: Goal) {
    if (goal.targetValue <= 0) {
      return 0;
    }

    return Math.min((goal.currentProgress / goal.targetValue) * 100, 100);
  }

  return (
    <ContentLayout title="Goals">
      <div className="space-y-6">
        <section className="rounded-md border p-4">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Your fitness goals</h2>
              <p className="text-sm text-gray-600">
                Create, edit, and track your progress across activities.
              </p>
            </div>

            <button
              type="button"
              className="rounded-md border px-3 py-2"
              onClick={openCreateForm}
            >
              + Create Goal
            </button>
          </div>
        </section>

        <section className="rounded-md border p-4">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-md border px-3 py-2"
              onClick={() => setSelectedFilter('all')}
            >
              All
            </button>
            <button
              type="button"
              className="rounded-md border px-3 py-2"
              onClick={() => setSelectedFilter('active')}
            >
              Active
            </button>
            <button
              type="button"
              className="rounded-md border px-3 py-2"
              onClick={() => setSelectedFilter('completed')}
            >
              Completed
            </button>
          </div>
        </section>

        {isFormOpen && (
          <section className="rounded-md border p-4">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-md font-semibold">
                {editingGoalId !== null ? 'Edit goal' : 'Create a new goal'}
              </h3>
              <button
                type="button"
                className="rounded-md border px-3 py-2"
                onClick={closeForm}
              >
                Cancel
              </button>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="mb-1 block text-sm font-medium" htmlFor="title">
                  Goal title
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full rounded-md border px-3 py-2"
                  placeholder="Example: Run 15 km this month"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label
                    className="mb-1 block text-sm font-medium"
                    htmlFor="activityType"
                  >
                    Activity type
                  </label>
                  <select
                    id="activityType"
                    name="activityType"
                    value={formData.activityType}
                    onChange={handleInputChange}
                    className="w-full rounded-md border px-3 py-2"
                  >
                    <option value="Running">Running</option>
                    <option value="Cycling">Cycling</option>
                    <option value="Walking">Walking</option>
                    <option value="Workout">Workout</option>
                    <option value="Swimming">Swimming</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium" htmlFor="unit">
                    Unit
                  </label>
                  <select
                    id="unit"
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    className="w-full rounded-md border px-3 py-2"
                  >
                    <option value="km">km</option>
                    <option value="steps">steps</option>
                    <option value="minutes">minutes</option>
                    <option value="sessions">sessions</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label
                    className="mb-1 block text-sm font-medium"
                    htmlFor="targetValue"
                  >
                    Target value
                  </label>
                  <input
                    id="targetValue"
                    name="targetValue"
                    type="number"
                    min="1"
                    value={formData.targetValue}
                    onChange={handleInputChange}
                    className="w-full rounded-md border px-3 py-2"
                    placeholder="20"
                  />
                </div>

                <div>
                  <label
                    className="mb-1 block text-sm font-medium"
                    htmlFor="currentProgress"
                  >
                    Current progress
                  </label>
                  <input
                    id="currentProgress"
                    name="currentProgress"
                    type="number"
                    min="0"
                    value={formData.currentProgress}
                    onChange={handleInputChange}
                    className="w-full rounded-md border px-3 py-2"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label
                    className="mb-1 block text-sm font-medium"
                    htmlFor="deadline"
                  >
                    Deadline
                  </label>
                  <input
                    id="deadline"
                    name="deadline"
                    type="date"
                    value={formData.deadline}
                    onChange={handleInputChange}
                    className="w-full rounded-md border px-3 py-2"
                  />
                </div>
              </div>

              {formError && (
                <div className="rounded-md border border-red-300 p-3 text-sm text-red-700">
                  {formError}
                </div>
              )}

              <button type="submit" className="rounded-md border px-4 py-2">
                {editingGoalId !== null ? 'Save Changes' : 'Add Goal'}
              </button>
            </form>
          </section>
        )}

        <section className="rounded-md border p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-md font-semibold">Active goals</h3>
            <span className="text-sm text-gray-600">{activeGoals.length} goal(s)</span>
          </div>

          {activeGoals.length === 0 ? (
            <p className="text-sm text-gray-600">
              No active goals in this view. Try creating one or changing the filter.
            </p>
          ) : (
            <div className="space-y-4">
              {activeGoals.map((goal) => {
                const progressPercentage = getProgressPercentage(goal);

                return (
                  <article key={goal.id} className="rounded-md border p-4">
                    <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <h4 className="font-semibold">{goal.title}</h4>
                        <p className="text-sm text-gray-600">
                          {goal.activityType} • Deadline: {goal.deadline}
                        </p>
                      </div>

                      <button
                        type="button"
                        className="rounded-md border px-3 py-2"
                        onClick={() => openEditForm(goal)}
                      >
                        Edit
                      </button>
                    </div>

                    <div className="mb-2 flex items-center justify-between text-sm">
                      <span>
                        {goal.currentProgress} / {goal.targetValue} {goal.unit}
                      </span>
                      <span>{progressPercentage.toFixed(0)}%</span>
                    </div>

                    <div className="h-3 w-full rounded-full bg-gray-200">
                      <div
                        className="h-3 rounded-full bg-blue-500"
                        style={{ width: `${progressPercentage}%` }}
                      />
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <section className="rounded-md border p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-md font-semibold">Completed goals</h3>
            <span className="text-sm text-gray-600">
              {completedGoals.length} goal(s)
            </span>
          </div>

          {completedGoals.length === 0 ? (
            <p className="text-sm text-gray-600">
              Completed goals will appear here once progress reaches the target.
            </p>
          ) : (
            <div className="space-y-4">
              {completedGoals.map((goal) => (
                <article key={goal.id} className="rounded-md border p-4">
                  <div className="mb-2 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <h4 className="font-semibold">{goal.title}</h4>
                      <p className="text-sm text-gray-600">
                        {goal.activityType} • Completed
                      </p>
                    </div>

                    <button
                      type="button"
                      className="rounded-md border px-3 py-2"
                      onClick={() => openEditForm(goal)}
                    >
                      Edit
                    </button>
                  </div>

                  <p className="text-sm">
                    {goal.currentProgress} / {goal.targetValue} {goal.unit}
                  </p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </ContentLayout>
  );
}