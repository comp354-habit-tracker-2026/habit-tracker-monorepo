import { useParams } from 'react-router';

import { ContentLayout } from '@/components/layouts/content-layout';
import { useHabit } from '@/features/habits/hooks/use-habit';

function HabitDetailRoute() {
  const { habitId } = useParams<{ habitId: string }>();

  const habitQuery = useHabit({ habitId: habitId! });

  if (habitQuery.isLoading) return <p>Loading…</p>;
  if (habitQuery.isError) return <p>Failed to load habit.</p>;

  const habit = habitQuery.data;

  return (
    <ContentLayout title={habit?.name ?? 'Habit Detail'}>
      <p>{habit?.description}</p>
    </ContentLayout>
  );
}

export default HabitDetailRoute;
