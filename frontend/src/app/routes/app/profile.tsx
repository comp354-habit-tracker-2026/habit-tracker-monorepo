import { ContentLayout } from '@/components/layouts/content-layout';
import { ConnectedAccountsSettings } from '@/components/connected-accounts-settings';
import './profile.css';

function ProfileRoute() {
  return (
    <ContentLayout title="Profile & Settings">
      <div className="profile-route">
        <section className="profile-route__section">
          <ConnectedAccountsSettings />
        </section>
      </div>
    </ContentLayout>
  );
}

export default ProfileRoute;
