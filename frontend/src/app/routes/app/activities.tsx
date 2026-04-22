import { ContentLayout } from '@/components/layouts/content-layout';
import { ActivityTimeSeriesChart } from '@/components/charts/activity-time-series-chart';
import { ActivityPieChart } from '@/components/charts/activity-pie-chart';
import { ActivityBarChart } from '@/components/charts/activity-bar-chart';
import { WeSkiRouteMapChart } from '@/components/charts/we-ski-route-map-chart';
import { MyWhooshRouteOverlayChart } from '@/components/charts/my-whoosh-route-overlay-chart';
import {
  mockActivitiesOverTimeBySessionCount,
  mockPieChartByCount,
  mockPieChartByDistance,
} from '@/mocks/mock-activities';
import {
  mockMyWhooshRouteMapPoints,
  mockWeSkiRouteMapPoints,
} from '@/mocks/mock-chart-raw-data';

import './activities.css';

export default function ActivitiesRoute() {
  return (
    <ContentLayout title="Activities">
      <div className="activities-route">
        <section className="activities-route__section" aria-labelledby="weski-section-title">
          <div className="activities-route__section-header">
            <h2
              id="weski-section-title"
              className="activities-route__section-title"
            >
              WeSki
            </h2>
            <p className="activities-route__section-copy">
              WeSki exports real-world GPX tracks, so route visualization lives
              on an actual basemap and can grow into ski-specific map and run
              analysis.
            </p>
          </div>

          <WeSkiRouteMapChart data={mockWeSkiRouteMapPoints} />
        </section>

        <section className="activities-route__section" aria-labelledby="mywhoosh-section-title">
          <div className="activities-route__section-header">
            <h2
              id="mywhoosh-section-title"
              className="activities-route__section-title"
            >
              MyWhoosh
            </h2>
            <p className="activities-route__section-copy">
              MyWhoosh data is fundamentally virtual-course telemetry, so its
              route remains an overlay chart rather than a geographic map.
            </p>
          </div>

          <MyWhooshRouteOverlayChart data={mockMyWhooshRouteMapPoints} />
        </section>

        <section className="activities-route__section" aria-labelledby="overall-section-title">
          <div className="activities-route__section-header">
            <h2
              id="overall-section-title"
              className="activities-route__section-title"
            >
              Overall Summary
            </h2>
            <p className="activities-route__section-copy">
              These rollups stay at a high level. Detailed charting is split by
              provider because the underlying data models are not equivalent.
            </p>
          </div>

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
        </section>
      </div>
    </ContentLayout>
  );
}
