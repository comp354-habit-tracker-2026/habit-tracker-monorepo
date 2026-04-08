import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type GamificationSummary } from '../types/gamification';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getSummary(): Promise<GamificationSummary> {
  const response = await apiClient.get<GamificationSummary>(
    '/gamification/summary/',
  );
  return response as unknown as GamificationSummary;
}

// ---------------------------------------------------------------------------
// Query options factory
// ---------------------------------------------------------------------------
export function getSummaryQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'summary'],
    queryFn: getSummary,
  });
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useSummary() {
  return useQuery(getSummaryQueryOptions());
}
