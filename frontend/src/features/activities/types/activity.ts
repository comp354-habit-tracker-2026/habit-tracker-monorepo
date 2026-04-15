// ---------------------------------------------------------------------------
// Domain types for Activity feature
// Matches backend activities.models.Activity fields
// ---------------------------------------------------------------------------

export type ActivityProvider =
  | 'manual'
  | 'strava'
  | 'mapmyrun'
  | 'weski'
  | 'mywhoosh';

export type Activity = {
  id: string;
  activity_type: string;
  duration: number; // minutes
  date: string; // ISO date
  provider: ActivityProvider;
  external_id: string | null;
  distance: number | null; // km
  calories: number | null;
  created_at: string;
  updated_at: string;
};

// ---------------------------------------------------------------------------
// Activity type display metadata (for icons/colors)
// ---------------------------------------------------------------------------

export const ACTIVITY_TYPE_CONFIG: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  Ski: { label: 'Ski', icon: '🎿', color: 'bg-blue-500' },
  Snowboard: { label: 'Snowboard', icon: '🏂', color: 'bg-blue-600' },
  Cycling: { label: 'Cycling', icon: '🚴', color: 'bg-green-500' },
  Walking: { label: 'Walking', icon: '🚶', color: 'bg-gray-500' },
  Running: { label: 'Running', icon: '🏃', color: 'bg-orange-500' },
  Indoor: { label: 'Indoor', icon: '🏠', color: 'bg-purple-500' },
  Swimming: { label: 'Swimming', icon: '🏊', color: 'bg-cyan-500' },
  Workout: { label: 'Workout', icon: '💪', color: 'bg-red-500' },
  Yoga: { label: 'Yoga', icon: '🧘', color: 'bg-teal-500' },
  Hiking: { label: 'Hiking', icon: '🥾', color: 'bg-emerald-500' },
};

export function getActivityConfig(activityType: string): {
  label: string;
  icon: string;
  color: string;
} {
  return (
    ACTIVITY_TYPE_CONFIG[activityType] || {
      label: activityType,
      icon: '📋',
      color: 'bg-gray-400',
    }
  );
}
