export type ActivitySummary = {
  total_distance: number;
  total_calories: number;
  average_duration: number;
  activity_count: number;
};

export type AnalyticsOverview = {
  activity_statistics: ActivitySummary;
};