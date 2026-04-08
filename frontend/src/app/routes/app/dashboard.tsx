import { ContentLayout } from '@/components/layouts/content-layout';
import { ActivitySummaryPanel } from '@/features/analytics/components/activity-summary-panel';

function DashboardRoute() {
  return (
    <ContentLayout title="Dashboard">
      <p>Welcome back! Use the navigation to manage your habits.</p>
      <ActivitySummaryPanel />
    </ContentLayout>
  );
}

export default DashboardRoute;