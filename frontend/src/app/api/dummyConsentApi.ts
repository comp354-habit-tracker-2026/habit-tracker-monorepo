// Dummy consent API for frontend testing

export type DummyConsent = {
  provider: string;
  consent_granted: boolean;
  status: string;
};

// Simulate a user profile with consents
let userConsents: Record<string, boolean> = {
  Strava: false,
  MapMyRun: false,
  'We Ski': false,
  MyWhoosh: false,
};

// Dummy data for each provider
const dummyData: Record<string, any> = {
  Strava: { activities: ['Run', 'Bike'], profile: { name: 'Strava User', id: 1 } },
  MapMyRun: { activities: ['Walk', 'Run'], profile: { name: 'MMR User', id: 2 } },
  'We Ski': { activities: ['Ski'], profile: { name: 'Ski User', id: 3 } },
  MyWhoosh: { activities: ['Ride'], profile: { name: 'Whoosh User', id: 4 } },
};

export function setConsent(provider: string, consentGranted: boolean): Promise<DummyConsent> {
  return new Promise((resolve) => {
    setTimeout(() => {
      userConsents[provider] = consentGranted;
      resolve({
        provider,
        consent_granted: consentGranted,
        status: consentGranted ? 'granted' : 'revoked',
      });
    }, 400);
  });
}

export function getUserData() {
  // Return dummy data for providers with consent
  const data: Record<string, any> = {};
  Object.entries(userConsents).forEach(([provider, granted]) => {
    if (granted) data[provider] = dummyData[provider];
  });
  return data;
}

export function getUserConsents() {
  return { ...userConsents };
}
