# Dummy Consent API This folder contains a mock API for simulating user consent and provider data integration in the frontend, without requiring a real backend. ## Files - dummyConsentApi.ts: Implements a fake consent API for testing the consent toggles UI. It manages dummy consent state and provides mock data for each provider. ## Usage - Import the functions from dummyConsentApi.ts in your frontend code to simulate granting or revoking consent for providers (Strava, MapMyRun, We Ski, MyWhoosh). - The API manages a fake "logged-in user" and returns dummy data for each provider when consent is granted. - Used in the consent-test.tsx route to demonstrate toggling provider consent and viewing associated user data. ## Functions - setConsent(provider: string, consentGranted: boolean): Simulates granting or revoking consent for a provider. Updates the dummy user data. - getUserData(): Returns the current dummy data for all providers with consent granted. - getUserConsents(): Returns the current consent state for all providers. ## Example
ts
import { setConsent, getUserData, getUserConsents } from './dummyConsentApi';

// Grant Strava consent
await setConsent('Strava', true);

// Get user data
const data = getUserData();
console.log(data);
## Purpose This mock API is for frontend development and testing only. It allows you to: - Develop and test UI components that depend on consent and provider data - Simulate user interactions without a backend - Easily reset or change the dummy data as needed