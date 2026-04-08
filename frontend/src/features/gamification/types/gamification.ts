import { z } from 'zod';

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

export type Badge = {
  id: number;
  name: string;
  description: string;
  icon: string;
  badge_type: 'single' | 'cumulative' | 'streak' | 'frequency';
  activity_type: string;
  threshold: string;
  metric: string;
  points: number;
};

export type UserBadge = {
  id: number;
  badge: Badge;
  earned_at: string;
};

export type Streak = {
  current_count: number;
  longest_count: number;
  last_activity_date: string | null;
};

export type Milestone = {
  id: number;
  name: string;
  description: string;
  icon: string;
  metric: string;
  threshold: string;
  activity_type: string;
  points: number;
};

export type UserMilestone = {
  id: number;
  milestone: Milestone;
  reached_at: string;
};

export type BadgeProgress = {
  badge: Badge;
  current_value: number;
  progress_percent: number;
  earned: boolean;
};

export type MilestoneProgress = {
  milestone: Milestone;
  current_value: number;
  progress_percent: number;
  reached: boolean;
};

export type GamificationSummary = {
  total_points: number;
  badges_earned: UserBadge[];
  milestones_reached: UserMilestone[];
  streak: Streak;
  badge_progress: BadgeProgress[];
  milestone_progress: MilestoneProgress[];
};

// ---------------------------------------------------------------------------
// Zod schemas – for response validation if needed
// ---------------------------------------------------------------------------
export const badgeSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string(),
  icon: z.string(),
  badge_type: z.enum(['single', 'cumulative', 'streak', 'frequency']),
  activity_type: z.string(),
  threshold: z.string(),
  metric: z.string(),
  points: z.number(),
});

export const streakSchema = z.object({
  current_count: z.number(),
  longest_count: z.number(),
  last_activity_date: z.string().nullable(),
});
