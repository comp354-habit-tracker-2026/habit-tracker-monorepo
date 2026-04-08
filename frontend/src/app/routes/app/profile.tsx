import { ContentLayout } from '@/components/layouts/content-layout';
import './profile.css';
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from '@/features/notifications/api';

function ProfileRoute() {
  const { data: preferences, isLoading, isError } = useNotificationPreferences();
  const { mutate: updatePreferences, isPending } = useUpdateNotificationPreferences();

  const handleToggle = (key: 'email_enabled' | 'push_enabled') => {
    if (!preferences || isPending) return;
    
    updatePreferences({
      ...preferences,
      [key]: !preferences[key],
    });
  };

  return (
    <ContentLayout title="Profile">
      <div className="profile-settings">
        <div className="profile-settings__header">
          <h2>Notification Preferences</h2>
          <p>Control how you want to be notified about events and updates.</p>
        </div>

        {isLoading ? (
          <div className="settings-loading">Loading preferences...</div>
        ) : isError || !preferences ? (
          <div className="settings-error">Failed to load preferences.</div>
        ) : (
          <div className="profile-settings__section">
            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-title">Email Notifications</span>
                <span className="setting-desc">Receive daily summaries and alerts via email.</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  data-cy="email-notification-toggle"
                  checked={preferences.email_enabled}
                  onChange={() => handleToggle('email_enabled')}
                  disabled={isPending}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-title">Push Notifications</span>
                <span className="setting-desc">Receive immediate alerts directly on your device.</span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  data-cy="push-notification-toggle"
                  checked={preferences.push_enabled}
                  onChange={() => handleToggle('push_enabled')}
                  disabled={isPending}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        )}
      </div>
    </ContentLayout>
  );
}

export default ProfileRoute;
