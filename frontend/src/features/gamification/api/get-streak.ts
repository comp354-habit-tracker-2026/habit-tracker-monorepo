import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Streak } from '../types/gamification';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getStreak(): Promise<Streak> {
  const response = await apiClient.get<Streak>('/gamification/streaks/');
  return response as unknown as Streak;
}

// ---------------------------------------------------------------------------
// Query options factory
// ---------------------------------------------------------------------------
export function getStreakQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'streak'],
    queryFn: getStreak,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useStreak() {
  return useQuery(getStreakQueryOptions());
}
