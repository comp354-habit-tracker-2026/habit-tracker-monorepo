import { ContentLayout } from '@/components/layouts/content-layout';
import { ActivityBarChart } from '@/components/charts/activity-bar-chart';
import { ActivityPieChart } from '@/components/charts/activity-pie-chart';
import { ActivityTimeSeriesChart } from '@/components/charts/activity-time-series-chart';
import { ActivityCard } from '@/components/activities/activity-card';
import {
  mockActivities,
  mockActivitiesOverTimeBySessionCount,
  mockActivityAggregates,
  mockPieChartByCount,
  mockPieChartByDistance,
} from '@/mocks/mock-activities';
import {
  mockMyWhooshHeartRateZones,
  mockMyWhooshPowerZones,
  mockMyWhooshSpeedZones,
} from '@/mocks/mock-chart-data';
import {
  mockMyWhooshRouteMapPoints,
  mockMyWhooshStreamSeriesDense,
  mockWeSkiRouteMapPoints,
} from '@/mocks/mock-chart-raw-data';

import './activities.css';

const totalSessions = mockActivityAggregates.reduce(
  (sum, a) => sum + a.activity_count,
  0,
);
const totalDistanceKm = mockActivityAggregates.reduce(
  (sum, a) => sum + a.total_distance,
  0,
);
const totalCalories = mockActivityAggregates.reduce(
  (sum, a) => sum + a.total_calories,
  0,
);

const myWhooshDetail = {
  streamData: mockMyWhooshStreamSeriesDense,
  routeData: mockMyWhooshRouteMapPoints,
  hrZones: mockMyWhooshHeartRateZones,
  powerZones: mockMyWhooshPowerZones,
  speedZones: mockMyWhooshSpeedZones,
};

export default function ActivitiesRoute() {
  return (
    <ContentLayout title="Activities">
      <div className="activities-route">
        <section
          className="activities-route__section"
          aria-labelledby="overview-title"
        >
          <div className="activities-route__section-header">
            <h2
              id="overview-title"
              className="activities-route__section-title"
            >
              Overview
            </h2>
            <p className="activities-route__section-copy">
              Rollup across all connected sources for the selected period.
            </p>
          </div>

          <ul
            className="activities-route__agg-stats"
            aria-label="All-time totals"
          >
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">{totalSessions}</span>
              <span className="activities-route__agg-label">Sessions</span>
            </li>
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">
                {totalDistanceKm.toFixed(1)}
                <span className="activities-route__agg-unit">km</span>
              </span>
              <span className="activities-route__agg-label">Distance</span>
            </li>
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">
                {totalCalories.toLocaleString('en-US')}
              </span>
              <span className="activities-route__agg-label">Calories</span>
            </li>
          </ul>

          <ActivityTimeSeriesChart
            title="Activities over time"
            description="Weekly activity volume trend to help monitor consistency and progression."
            valueLabel="Sessions"
            startDate={new Date(2026, 0, 1)}
            endDate={new Date(2026, 2, 31)}
            data={mockActivitiesOverTimeBySessionCount}
            height={220}
          />

          <div className="activities-route__charts-grid">
            <ActivityPieChart
              title="Activity breakdown"
              description="Distribution of activity types to understand focus areas and variety."
              totalLabel="Sessions"
              startDate={new Date(2026, 0, 1)}
              endDate={new Date(2026, 2, 31)}
              data={mockPieChartByCount}
              height={220}
            />

            <ActivityBarChart
              title="Distance by activity"
              description="Comparative distance totals by activity type for the selected period."
              startDate={new Date(2026, 0, 1)}
              endDate={new Date(2026, 2, 31)}
              data={mockPieChartByDistance}
              valueFormatter={(value: number) => `${value.toFixed(1)} km`}
              height={220}
            />
          </div>
        </section>

        <section
          className="activities-route__section"
          aria-labelledby="activities-title"
        >
          <div className="activities-route__section-header">
            <h2
              id="activities-title"
              className="activities-route__section-title"
            >
              Your Activities
            </h2>
            <p className="activities-route__section-copy">
              Select an activity to see its route, stats, and detailed analysis.
            </p>
          </div>

          <div className="activities-route__list">
            <ActivityCard
              activity={mockActivities[0]}
              weSkiRoutePoints={mockWeSkiRouteMapPoints}
            />
            <ActivityCard activity={mockActivities[1]} />
            <ActivityCard
              activity={mockActivities[2]}
              myWhooshDetail={myWhooshDetail}
            />
          </div>
        </section>
      </div>
    </ContentLayout>
  );
}
