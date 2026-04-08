import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type AnalyticsOverview } from '../types/analytics';

async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const response = await apiClient.get<AnalyticsOverview>('/analytics/overview');
  return response as unknown as AnalyticsOverview;
}

export function getAnalyticsOverviewQueryOptions() {
  return queryOptions({
    queryKey: ['analytics', 'overview'],
    queryFn: getAnalyticsOverview,
  });
}

export function useAnalyticsOverview() {
  return useQuery(getAnalyticsOverviewQueryOptions());
}