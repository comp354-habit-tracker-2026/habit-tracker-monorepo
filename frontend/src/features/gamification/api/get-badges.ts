import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

import { type Badge, type UserBadge, type BadgeProgress } from '../types/gamification';

// ---------------------------------------------------------------------------
// All badge definitions
// ---------------------------------------------------------------------------
async function getBadges(): Promise<Badge[]> {
  const response = await apiClient.get<Badge[]>('/gamification/badges/');
  return response as unknown as Badge[];
}

export function getBadgesQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'badges'],
    queryFn: getBadges,
  });
}

export function useBadges() {
  return useQuery(getBadgesQueryOptions());
}

// ---------------------------------------------------------------------------
// Earned badges for the current user
// ---------------------------------------------------------------------------
async function getEarnedBadges(): Promise<UserBadge[]> {
  const response = await apiClient.get<UserBadge[]>('/gamification/badges/earned/');
  return response as unknown as UserBadge[];
}

export function getEarnedBadgesQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'badges', 'earned'],
    queryFn: getEarnedBadges,
  });
}

export function useEarnedBadges() {
  return useQuery(getEarnedBadgesQueryOptions());
}

// ---------------------------------------------------------------------------
// Badge progress
// ---------------------------------------------------------------------------
async function getBadgeProgress(): Promise<BadgeProgress[]> {
  const response = await apiClient.get<BadgeProgress[]>('/gamification/badges/progress/');
  return response as unknown as BadgeProgress[];
}

export function getBadgeProgressQueryOptions() {
  return queryOptions({
    queryKey: ['gamification', 'badges', 'progress'],
    queryFn: getBadgeProgress,
  });
}

export function useBadgeProgress() {
  return useQuery(getBadgeProgressQueryOptions());
}
