import { ContentLayout } from '@/components/layouts/content-layout';
import '@coreui/coreui-pro/dist/css/coreui.min.css';
import { CCalendar } from '@coreui/react-pro';

function DashboardRoute() {
  return (
    <ContentLayout title="Dashboard">
      <p>Welcome back! Use the navigation to manage your habits.</p>
      <div className="d-flex justify-content-center">
        <CCalendar
          className="border rounded"
          locale="en-US"
          startDate="2024/02/13"
        />
      </div>
    </ContentLayout>
  );
}

export default DashboardRoute;
