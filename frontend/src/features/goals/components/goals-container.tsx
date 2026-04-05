import { useState } from 'react';
import { useGoals } from '../api/get-goals';
import { GoalCard } from './goal-card';
import { GoalFilterTabs } from './goal-filter-tabs';
import { CreateGoalForm } from './create-goal-form';

export const GoalsContainer = () => {
  const { data: goals, isLoading } = useGoals();
  console.log('GOALS IN COMPONENT:', goals);
  const [filter, setFilter] = useState('all');

  if (isLoading) return <div>Loading goals...</div>;

  const filtered =
    filter === 'all' ? goals : goals?.filter((g) => g.goal_type === filter);

  return (
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-2">Goals</h2>

      <div className="mb-3">
        <CreateGoalForm />
      </div>

      <GoalFilterTabs value={filter} onChange={setFilter} />

      <div className="grid gap-4 md:grid-cols-2">
        {filtered?.map((goal) => (
          <GoalCard key={goal.id} goal={goal} />
        ))}
      </div>
    </div>
  );
};
