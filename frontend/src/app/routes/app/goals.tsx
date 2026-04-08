import { useState } from 'react';

import { ContentLayout } from '@/components/layouts/content-layout';
import { GoalsList } from '@/features/goals/components/goals-list';
import { WeeklyDistanceGoalForm } from '@/features/goals/components/weekly-distance-goal-form';

function GoalsRoute() {
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  return (
    <ContentLayout title="Weekly Distance Goals">
      <p>Set a weekly target distance so you have a clear objective to work toward.</p>
      <WeeklyDistanceGoalForm
        onSuccess={() => setSuccessMessage('Weekly distance goal saved successfully.')}
      />
      {successMessage && <p role="status">{successMessage}</p>}
      <GoalsList />
    </ContentLayout>
  );
}

export default GoalsRoute;
