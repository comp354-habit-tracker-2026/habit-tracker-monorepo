import { useState } from 'react';

import { ContentLayout } from '@/components/layouts/content-layout';
import { apiClient } from '@/lib/api-client';

type ConsentResponse = {
  provider: string;
  consent_granted: boolean;
  status: string;
};

function ConsentTestRoute() {
  const [result, setResult] = useState<ConsentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function setConsent(consentGranted: boolean) {
    setError(null);

    try {
      const response = await apiClient.post<ConsentResponse>('/api/v1/data-integrations/consent/', {
        provider: 'strava',
        consent_granted: consentGranted,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    }
  }

  return (
    <ContentLayout title="Consent Test">
      <p>This page is a small dummy test for the new consent API.</p>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <button onClick={() => setConsent(true)}>Grant Strava Consent</button>
        <button onClick={() => setConsent(false)}>Revoke Strava Consent</button>
      </div>

      {result ? (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      ) : (
        <p>Click a button to send a consent request to the backend.</p>
      )}

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </ContentLayout>
  );
}

export default ConsentTestRoute;
