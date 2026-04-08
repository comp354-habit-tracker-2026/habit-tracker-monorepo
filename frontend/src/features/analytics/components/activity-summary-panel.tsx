import { useAnalyticsOverview } from '../api/get-analytics-overview';

/**
 * Displays a summary of the user's activity statistics.
 * Weekly filtering is pending backend support; currently shows all-time totals.
 */
export function ActivitySummaryPanel() {
  const { data, isLoading, isError } = useAnalyticsOverview();

  if (isLoading) return <p>Loading activity summary…</p>;
  if (isError) return <p>Unable to load activity summary. Please try again later.</p>;

  const stats = data?.activity_statistics;

  if (!stats || stats.activity_count === 0) {
    return <p>No activity recorded yet. Start tracking to see your summary here.</p>;
  }

  return (
    <div>
      <h2>Activity Summary</h2>
      <ul>
        <li>Total Distance: {stats.total_distance} km</li>
        <li>Total Calories: {stats.total_calories} kcal</li>
        <li>Average Duration: {stats.average_duration} min</li>
        <li>Total Activities: {stats.activity_count}</li>
      </ul>
    </div>
  );
}