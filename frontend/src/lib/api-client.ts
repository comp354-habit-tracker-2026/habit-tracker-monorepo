import axios from 'axios';

import { env } from '@/config/env';
import { getAccessToken } from '@/lib/auth';

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

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
