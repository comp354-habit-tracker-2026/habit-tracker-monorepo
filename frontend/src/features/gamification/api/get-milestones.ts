import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type MilestoneProgress } from '../types/gamification';

// ---------------------------------------------------------------------------
// Milestone progress
// ---------------------------------------------------------------------------
async function getMilestoneProgress(): Promise<MilestoneProgress[]> {
  const response = await apiClient.get<MilestoneProgress[]>(
    '/gamification/milestones/progress/',
  );
  return response as unknown as MilestoneProgress[];
}

export function getMilestoneProgressQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'milestones', 'progress'],
    queryFn: getMilestoneProgress,
  });
}

export function useMilestoneProgress() {
  return useQuery(getMilestoneProgressQueryOptions());
}
