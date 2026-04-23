import axios from 'axios';

import { env } from '@/config/env';

/**
 * Pre-configured Axios instance.
 *
 * All API calls in features should import this client instead of
 * calling axios directly. This keeps auth headers, base URL, and
 * error interceptors in one place.
 */
export const apiClient = axios.create({
  baseURL: env.BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// ---------------------------------------------------------------------------
// Token storage utilities - Simple token management from localStorage for testing
// This is temporary until login is implemented
// ---------------------------------------------------------------------------

const TOKEN_KEY = 'access_token';

export function setAccessToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearAccessToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// Request interceptor – add Authorization header if token exists
// Automatically sends bearer token with every API request
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Response interceptor – normalise errors into a consistent shape so feature
// code never has to inspect raw Axios errors.
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.message ?? error.message ?? 'An error occurred';
    return Promise.reject(new Error(message));
  },
);
