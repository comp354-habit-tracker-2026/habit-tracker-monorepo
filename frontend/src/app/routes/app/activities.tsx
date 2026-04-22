import { ContentLayout } from '@/components/layouts/content-layout';
import { ActivitiesList } from '@/features/activities/components/activities-list';

/**
 * Activities page - displays all user activities.
 * 
 * Original scaffold by Group 18 (developed from ChatGPT code).
 * Enhanced in User Story #192 to integrate ActivitiesList.
 * TODO (#191): Add AuthGuard when auth feature is implemented by team member
 */
function ActivitiesRoute() {
  return (
    <ContentLayout title="Activities">
      <ActivitiesList />
    </ContentLayout>
  );
}

export default ActivitiesRoute;
