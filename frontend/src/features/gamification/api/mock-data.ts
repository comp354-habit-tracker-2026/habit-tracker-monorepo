import { type GamificationSummary } from '../types/gamification';

/**
 * Demo data used when the backend is not running.
 * This matches the seed data from backend/gamification/management/commands/seed_gamification.py
 * Remove this file or switch useDemoData to false once the backend is live.
 */
export const DEMO_SUMMARY: GamificationSummary = {
  total_points: 435,
  streak: {
    current_count: 5,
    longest_count: 12,
    last_activity_date: '2026-03-30',
  },
  badges_earned: [
    {
      id: 1,
      badge: {
        id: 1,
        name: 'First Steps',
        description: 'Log your very first activity',
        icon: 'first-steps',
        badge_type: 'single',
        activity_type: '',
        threshold: '0.00',
        metric: 'count',
        points: 10,
      },
      earned_at: '2026-03-20T10:00:00Z',
    },
    {
      id: 2,
      badge: {
        id: 2,
        name: '10K Runner',
        description: 'Complete a single run of 10 km or more',
        icon: '10k-runner',
        badge_type: 'single',
        activity_type: 'running',
        threshold: '10.00',
        metric: 'distance',
        points: 50,
      },
      earned_at: '2026-03-22T14:30:00Z',
    },
    {
      id: 5,
      badge: {
        id: 5,
        name: 'Iron Will',
        description: 'Maintain a 7-day activity streak',
        icon: 'iron-will',
        badge_type: 'streak',
        activity_type: '',
        threshold: '7.00',
        metric: 'streak',
        points: 100,
      },
      earned_at: '2026-03-26T09:00:00Z',
    },
    {
      id: 8,
      badge: {
        id: 8,
        name: 'Calorie Crusher',
        description: 'Burn 500+ calories in a single session',
        icon: 'calorie-crusher',
        badge_type: 'single',
        activity_type: '',
        threshold: '500.00',
        metric: 'calories',
        points: 50,
      },
      earned_at: '2026-03-28T16:45:00Z',
    },
    {
      id: 11,
      badge: {
        id: 11,
        name: 'Tri-Weekly Runner',
        description: 'Run 3 or more times in a single week',
        icon: 'tri-weekly',
        badge_type: 'frequency',
        activity_type: 'running',
        threshold: '3.00',
        metric: 'count',
        points: 100,
      },
      earned_at: '2026-03-29T11:00:00Z',
    },
  ],
  milestones_reached: [
    {
      id: 1,
      milestone: {
        id: 1,
        name: '50km Total Distance',
        description: 'Accumulate 50 km across all activities',
        icon: '50km',
        metric: 'total_distance',
        threshold: '50.00',
        activity_type: '',
        points: 50,
      },
      reached_at: '2026-03-24T12:00:00Z',
    },
    {
      id: 2,
      milestone: {
        id: 5,
        name: '10 Activities Logged',
        description: 'Complete 10 activities of any type',
        icon: '10-activities',
        metric: 'total_activities',
        threshold: '10.00',
        activity_type: '',
        points: 25,
      },
      reached_at: '2026-03-25T08:00:00Z',
    },
    {
      id: 3,
      milestone: {
        id: 8,
        name: '10 Hours Active',
        description: 'Spend 10 total hours doing activities',
        icon: '10-hours',
        metric: 'total_duration',
        threshold: '600.00',
        activity_type: '',
        points: 50,
      },
      reached_at: '2026-03-27T17:00:00Z',
    },
  ],
  badge_progress: [
    {
      badge: { id: 1, name: 'First Steps', description: 'Log your very first activity', icon: 'first-steps', badge_type: 'single', activity_type: '', threshold: '0.00', metric: 'count', points: 10 },
      current_value: 1, progress_percent: 100, earned: true,
    },
    {
      badge: { id: 2, name: '10K Runner', description: 'Complete a single run of 10 km or more', icon: '10k-runner', badge_type: 'single', activity_type: 'running', threshold: '10.00', metric: 'distance', points: 50 },
      current_value: 12.5, progress_percent: 100, earned: true,
    },
    {
      badge: { id: 3, name: 'Half Marathon Hero', description: 'Complete a single run of 21.1 km', icon: 'half-marathon', badge_type: 'single', activity_type: 'running', threshold: '21.10', metric: 'distance', points: 100 },
      current_value: 12.5, progress_percent: 59, earned: false,
    },
    {
      badge: { id: 4, name: 'Century Ride', description: 'Cycle 100 km in a single ride', icon: 'century-ride', badge_type: 'single', activity_type: 'cycling', threshold: '100.00', metric: 'distance', points: 100 },
      current_value: 45, progress_percent: 45, earned: false,
    },
    {
      badge: { id: 5, name: 'Iron Will', description: 'Maintain a 7-day activity streak', icon: 'iron-will', badge_type: 'streak', activity_type: '', threshold: '7.00', metric: 'streak', points: 100 },
      current_value: 7, progress_percent: 100, earned: true,
    },
    {
      badge: { id: 6, name: 'Week Warrior', description: 'Maintain a 14-day activity streak', icon: 'week-warrior', badge_type: 'streak', activity_type: '', threshold: '14.00', metric: 'streak', points: 200 },
      current_value: 5, progress_percent: 36, earned: false,
    },
    {
      badge: { id: 7, name: 'Monthly Machine', description: 'Maintain a 30-day activity streak', icon: 'monthly', badge_type: 'streak', activity_type: '', threshold: '30.00', metric: 'streak', points: 500 },
      current_value: 5, progress_percent: 17, earned: false,
    },
    {
      badge: { id: 8, name: 'Calorie Crusher', description: 'Burn 500+ calories in a single session', icon: 'calorie-crusher', badge_type: 'single', activity_type: '', threshold: '500.00', metric: 'calories', points: 50 },
      current_value: 620, progress_percent: 100, earned: true,
    },
    {
      badge: { id: 9, name: '100km Club', description: 'Accumulate 100 km total distance', icon: '100km-club', badge_type: 'cumulative', activity_type: '', threshold: '100.00', metric: 'distance', points: 100 },
      current_value: 78, progress_percent: 78, earned: false,
    },
    {
      badge: { id: 10, name: '500km Club', description: 'Accumulate 500 km total distance', icon: '500km-club', badge_type: 'cumulative', activity_type: '', threshold: '500.00', metric: 'distance', points: 300 },
      current_value: 78, progress_percent: 16, earned: false,
    },
    {
      badge: { id: 11, name: 'Tri-Weekly Runner', description: 'Run 3 or more times in a single week', icon: 'tri-weekly', badge_type: 'frequency', activity_type: 'running', threshold: '3.00', metric: 'count', points: 100 },
      current_value: 3, progress_percent: 100, earned: true,
    },
    {
      badge: { id: 12, name: 'Daily Grinder', description: 'Log an activity 5 times in one week', icon: 'daily-grinder', badge_type: 'frequency', activity_type: '', threshold: '5.00', metric: 'count', points: 150 },
      current_value: 3, progress_percent: 60, earned: false,
    },
  ],
  milestone_progress: [
    {
      milestone: { id: 1, name: '50km Total Distance', description: 'Accumulate 50 km across all activities', icon: '50km', metric: 'total_distance', threshold: '50.00', activity_type: '', points: 50 },
      current_value: 78, progress_percent: 100, reached: true,
    },
    {
      milestone: { id: 2, name: '100km Total Distance', description: 'Accumulate 100 km across all activities', icon: '100km', metric: 'total_distance', threshold: '100.00', activity_type: '', points: 100 },
      current_value: 78, progress_percent: 78, reached: false,
    },
    {
      milestone: { id: 3, name: '500km Total Distance', description: 'Accumulate 500 km across all activities', icon: '500km', metric: 'total_distance', threshold: '500.00', activity_type: '', points: 250 },
      current_value: 78, progress_percent: 16, reached: false,
    },
    {
      milestone: { id: 4, name: '1,000km Total Distance', description: 'Accumulate 1,000 km across all activities', icon: '1000km', metric: 'total_distance', threshold: '1000.00', activity_type: '', points: 500 },
      current_value: 78, progress_percent: 8, reached: false,
    },
    {
      milestone: { id: 5, name: '10 Activities Logged', description: 'Complete 10 activities of any type', icon: '10-activities', metric: 'total_activities', threshold: '10.00', activity_type: '', points: 25 },
      current_value: 18, progress_percent: 100, reached: true,
    },
    {
      milestone: { id: 6, name: '50 Activities Logged', description: 'Complete 50 activities of any type', icon: '50-activities', metric: 'total_activities', threshold: '50.00', activity_type: '', points: 75 },
      current_value: 18, progress_percent: 36, reached: false,
    },
    {
      milestone: { id: 7, name: '100 Activities Logged', description: 'Complete 100 activities of any type', icon: '100-activities', metric: 'total_activities', threshold: '100.00', activity_type: '', points: 150 },
      current_value: 18, progress_percent: 18, reached: false,
    },
    {
      milestone: { id: 8, name: '10 Hours Active', description: 'Spend 10 total hours doing activities', icon: '10-hours', metric: 'total_duration', threshold: '600.00', activity_type: '', points: 50 },
      current_value: 740, progress_percent: 100, reached: true,
    },
    {
      milestone: { id: 9, name: '50 Hours Active', description: 'Spend 50 total hours doing activities', icon: '50-hours', metric: 'total_duration', threshold: '3000.00', activity_type: '', points: 200 },
      current_value: 740, progress_percent: 25, reached: false,
    },
    {
      milestone: { id: 10, name: '10,000 Calories Burned', description: 'Burn a total of 10,000 calories', icon: '10k-cal', metric: 'total_calories', threshold: '10000.00', activity_type: '', points: 100 },
      current_value: 6200, progress_percent: 62, reached: false,
    },
    {
      milestone: { id: 11, name: '50,000 Calories Burned', description: 'Burn a total of 50,000 calories', icon: '50k-cal', metric: 'total_calories', threshold: '50000.00', activity_type: '', points: 300 },
      current_value: 6200, progress_percent: 12, reached: false,
    },
  ],
};
