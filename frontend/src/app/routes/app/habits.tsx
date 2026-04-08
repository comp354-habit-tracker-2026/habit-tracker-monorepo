import { ContentLayout } from '@/components/layouts/content-layout';
import { HabitsList } from '@/features/habits/components/habits-list';

function HabitsRoute() {
  return (
    <ContentLayout title="My Habits">
      <HabitsList />
    </ContentLayout>
  );
}

export default HabitsRoute;
