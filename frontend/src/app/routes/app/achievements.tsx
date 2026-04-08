import { ContentLayout } from '@/components/layouts/content-layout';
import { GamificationPage } from '@/features/gamification/components/gamification-page';

function AchievementsRoute() {
  return (
    <ContentLayout title="Achievements">
      <GamificationPage />
    </ContentLayout>
  );
}

export default AchievementsRoute;
