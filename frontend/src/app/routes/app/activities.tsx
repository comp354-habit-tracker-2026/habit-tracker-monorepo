import { ContentLayout } from '@/components/layouts/content-layout';
import { ActivityTimeSeriesChart } from '@/components/charts/activity-time-series-chart';
import { ActivityPieChart } from '@/components/charts/activity-pie-chart';
import { ActivityBarChart } from '@/components/charts/activity-bar-chart';
import {
  mockActivitiesOverTimeBySessionCount,
  mockPieChartByCount,
  mockPieChartByDistance,
} from '@/mocks/mock-activities';

export default function ActivitiesRoute() {
  return (
    <ContentLayout title="Activities">
      <ActivityTimeSeriesChart
        title="Activities over time"
        description="Weekly activity volume trend to help monitor consistency and progression."
        valueLabel="Sessions"
        startDate={new Date(2026, 0, 1)}
        endDate={new Date(2026, 2, 31)}
        data={mockActivitiesOverTimeBySessionCount}
      />

      <ActivityPieChart
        title="Activity breakdown"
        description="Distribution of activity types to understand focus areas and variety."
        totalLabel="Sessions"
        startDate={new Date(2026, 0, 1)}
        endDate={new Date(2026, 2, 31)}
        data={mockPieChartByCount}
      />

      <ActivityBarChart
        title="Distance by activity"
        description="Comparative distance totals by activity type for the selected period."
        startDate={new Date(2026, 0, 1)}
        endDate={new Date(2026, 2, 31)}
        data={mockPieChartByDistance}
        valueFormatter={(value: number) => `${value.toFixed(1)} km`}
      />
    </ContentLayout>
  );
}
