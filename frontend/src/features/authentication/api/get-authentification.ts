//copy from Brandon Cameron get-activities.ts

//different for login or register?

import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type User } from '@/types/api';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getAuthentification(): Promise<User[]> {
  const response = await apiClient.get<{ results: User[] }>('/api/v1/auth/');
  return (response as unknown as { results: User[] }).results;
}

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated
// ---------------------------------------------------------------------------
export function getAuthentificationQueryOptions() {
  return queryOptions({
    queryKey: ['authentification'],
    queryFn: getAuthentification,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useAuthentification() {
  return useQuery(getAuthentificationQueryOptions());
}
