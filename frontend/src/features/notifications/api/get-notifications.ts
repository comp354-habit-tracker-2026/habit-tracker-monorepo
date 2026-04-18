//copy from Brandon Cameron get-activities.ts

import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Notification } from '../types/notification';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getNotifications(): Promise<Notification[]> {
  const response = await apiClient.get<{ results: Notification[] }>('/api/v1/notifications/');
  return (response as unknown as { results: Notification[] }).results;
}

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated
// ---------------------------------------------------------------------------
export function getNotificationsQueryOptions() {
  return queryOptions({
    queryKey: ['notifications'],
    queryFn: getNotifications,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useNotifications() {
  return useQuery(getNotificationsQueryOptions());
}