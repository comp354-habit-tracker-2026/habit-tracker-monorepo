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
// Response interceptor – normalise errors into a consistent shape so feature
// code never has to inspect raw Axios errors.
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const data = error.response?.data;

    const fieldMessage =
      data && typeof data === 'object'
        ? Object.values(data).flat().find((value) => typeof value === 'string')
        : undefined;

    const message =
      data?.message ??
      fieldMessage ??
      error.message ??
      'An error occurred';

    return Promise.reject(new Error(message));
  },
);
