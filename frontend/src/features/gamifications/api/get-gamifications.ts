//copy from Brandon Cameron get-activities.ts
//add UserBadge + UserMilestone
//gamification.tests.test_gamification
//add earned + progress Badges
//add reached + progress Milestones
//add summary

import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Badge } from '../types/badges';
import { type Milestone } from '../types/milestones';
import { type Streak } from '../types/streaks';

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
async function getBadges(): Promise<Badge[]> {
  const response = await apiClient.get<{ results: Badge[] }>('/api/v1/gamification/badges/');
  return (response as unknown as { results: Badge[] }).results;
}
async function getStreaks(): Promise<Streak[]> {
  const response = await apiClient.get<{ results: Streak[] }>('/api/v1/gamification/streaks/');
  return (response as unknown as { results: Streak[] }).results;
}
async function getMilestones(): Promise<Milestone[]> {
  const response = await apiClient.get<{ results: Milestone[] }>('/api/v1/gamification/milestones/');
  return (response as unknown as { results: Milestone[] }).results;
}
// async function getGamifications(): Promise<User[]> {
//   const response = await apiClient.get<{ results: User[] }>('/api/v1/auth/');
//   return (response as unknown as { results: User[] }).results;
// }

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated
// ---------------------------------------------------------------------------
export function getBadgesQueryOptions() {
  return queryOptions({
    queryKey: ['badges'],
    queryFn: getBadges,
  });
}
export function getStreaksQueryOptions() {
  return queryOptions({
    queryKey: ['streaks'],
    queryFn: getStreaks,
  });
}
export function getMilestonesQueryOptions() {
  return queryOptions({
    queryKey: ['milestones'],
    queryFn: getMilestones,
  });
}
// export function getGamificationsQueryOptions() {
//   return queryOptions({
//     queryKey: ['gamifications'],
//     queryFn: getGamifications,
//   });
// }

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useBadges() {
  return useQuery(getBadgesQueryOptions());
}
export function useStreaks() {
  return useQuery(getStreaksQueryOptions());
}
export function useMilestones() {
  return useQuery(getMilestonesQueryOptions());
}
// export function useGamifications() {
//   return useQuery(getGamificationsQueryOptions());
// }
