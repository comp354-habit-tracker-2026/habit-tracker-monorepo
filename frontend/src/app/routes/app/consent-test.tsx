
import { useState } from 'react';
import { ContentLayout } from '@/components/layouts/content-layout';
import { ConsentToggle } from '../../components/ConsentToggle';
import { setConsent as setDummyConsent, getUserData, getUserConsents } from '../../api/dummyConsentApi';


type ConsentResponse = {
  provider: string;
  consent_granted: boolean;
  status: string;
};

const PROVIDERS = [
  'Strava',
  'MapMyRun',
  'We Ski',
  'MyWhoosh',
];

function ConsentTestRoute() {

  const [consents, setConsents] = useState<Record<string, boolean>>(getUserConsents());
  const [result, setResult] = useState<ConsentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userData, setUserData] = useState<Record<string, any>>(getUserData());

  async function setConsent(provider: string, consentGranted: boolean) {
    setError(null);
    setConsents((prev) => ({ ...prev, [provider]: consentGranted }));
    try {
      const response = await setDummyConsent(provider, consentGranted);
      setResult(response);
      setUserData(getUserData());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    }
  }

  return (
    <ContentLayout title="Consent Test">
      <p>This page is a small dummy test for the new consent API.</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1rem', maxWidth: 300 }}>
        {PROVIDERS.map((provider) => (
          <ConsentToggle
            key={provider}
            provider={provider}
            consentGranted={consents[provider]}
            onToggle={setConsent}
          />
        ))}
      </div>

      {result ? (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      ) : (
        <p>Toggle a provider to simulate a consent request.</p>
      )}

      <div style={{ marginTop: 24 }}>
        <strong>User Data (dummy):</strong>
        <pre>{JSON.stringify(userData, null, 2)}</pre>
      </div>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </ContentLayout>
  );
}

export default ConsentTestRoute;
