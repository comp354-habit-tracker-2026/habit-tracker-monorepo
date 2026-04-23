import { useState } from 'react';

import { ActivityCard } from '@/components/activities/activity-card';
import { ActivityBarChart } from '@/components/charts/activity-bar-chart';
import { ActivityPieChart } from '@/components/charts/activity-pie-chart';
import { ActivityTimeSeriesChart } from '@/components/charts/activity-time-series-chart';
import { ContentLayout } from '@/components/layouts/content-layout';
import {
  ActivitySource,
  ActivityType,
} from '@/mocks/activity-types';
import type {
  ActivityBreakdownItem,
  ActivityListItem,
  ActivityTimeSeriesPoint,
} from '@/mocks/activity-types';
import { mockActivities } from '@/mocks/mock-activities';
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

type ActivitySourceFilter = ActivitySource | 'all';
type ActivityTypeFilter = ActivityType | 'all';

const ACTIVITY_TYPE_LABELS: Record<ActivityType, string> = {
  [ActivityType.Ski]: 'Ski',
  [ActivityType.BikeRide]: 'Bike Ride',
  [ActivityType.Cycling]: 'Cycling',
  [ActivityType.Run]: 'Run',
  [ActivityType.Walking]: 'Walk',
  [ActivityType.Snowboarding]: 'Snowboard',
};

const SOURCE_OPTIONS: Array<{ value: ActivitySourceFilter; label: string }> = [
  { value: 'all', label: 'All sources' },
  { value: ActivitySource.WeSki, label: 'WeSki' },
  { value: ActivitySource.MapMyRun, label: 'MapMyRun' },
  { value: ActivitySource.MyWhoosh, label: 'MyWhoosh' },
];

const TYPE_OPTIONS: Array<{ value: ActivityTypeFilter; label: string }> = [
  { value: 'all', label: 'All activities' },
  { value: ActivityType.Ski, label: 'Ski' },
  { value: ActivityType.BikeRide, label: 'Bike Ride' },
  { value: ActivityType.Cycling, label: 'Cycling' },
  { value: ActivityType.Run, label: 'Run' },
  { value: ActivityType.Walking, label: 'Walk' },
  { value: ActivityType.Snowboarding, label: 'Snowboard' },
];

const ACTIVITY_TYPE_COLORS: Record<ActivityType, string> = {
  [ActivityType.Ski]: '#f18f01',
  [ActivityType.BikeRide]: '#2e86ab',
  [ActivityType.Cycling]: '#2e86ab',
  [ActivityType.Run]: '#c73e1d',
  [ActivityType.Walking]: '#7d8f69',
  [ActivityType.Snowboarding]: '#7b2cbf',
};

const myWhooshDetail = {
  streamData: mockMyWhooshStreamSeriesDense,
  routeData: mockMyWhooshRouteMapPoints,
  hrZones: mockMyWhooshHeartRateZones,
  powerZones: mockMyWhooshPowerZones,
  speedZones: mockMyWhooshSpeedZones,
};

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US').format(value);
}

function formatDistance(value: number) {
  return `${value.toFixed(1)} km`;
}

function getActivitySliceKey(activity: ActivityListItem): ActivityType {
  return activity.activityKey ?? activity.activityType;
}

function getSourceLabel(source: ActivitySourceFilter) {
  if (source === 'all') {
    return 'All sources';
  }

  return SOURCE_OPTIONS.find((option) => option.value === source)?.label ?? source;
}

function getTypeLabel(type: ActivityTypeFilter) {
  if (type === 'all') {
    return 'All activities';
  }

  return ACTIVITY_TYPE_LABELS[type];
}

function sortActivitiesByDateDescending(
  left: ActivityListItem,
  right: ActivityListItem,
) {
  return new Date(right.startedAt).getTime() - new Date(left.startedAt).getTime();
}

function countActivitiesBySource(activities: ActivityListItem[]) {
  return activities.reduce<Record<ActivitySource, number>>(
    (counts, activity) => ({
      ...counts,
      [activity.source]: (counts[activity.source] ?? 0) + 1,
    }),
    {
      [ActivitySource.WeSki]: 0,
      [ActivitySource.MapMyRun]: 0,
      [ActivitySource.MyWhoosh]: 0,
    },
  );
}

function countActivitiesByType(activities: ActivityListItem[]) {
  return activities.reduce<Record<ActivityType, number>>(
    (counts, activity) => ({
      ...counts,
      [getActivitySliceKey(activity)]: (counts[getActivitySliceKey(activity)] ?? 0) + 1,
    }),
    {
      [ActivityType.Ski]: 0,
      [ActivityType.BikeRide]: 0,
      [ActivityType.Cycling]: 0,
      [ActivityType.Run]: 0,
      [ActivityType.Walking]: 0,
      [ActivityType.Snowboarding]: 0,
    },
  );
}

function filterActivities(
  activities: ActivityListItem[],
  sourceFilter: ActivitySourceFilter,
  typeFilter: ActivityTypeFilter,
) {
  return [...activities]
    .filter(
      (activity) => sourceFilter === 'all' || activity.source === sourceFilter,
    )
    .filter(
      (activity) => typeFilter === 'all' || getActivitySliceKey(activity) === typeFilter,
    )
    .sort(sortActivitiesByDateDescending);
}

function buildBreakdown(
  activities: ActivityListItem[],
  metric: 'count' | 'distance',
): ActivityBreakdownItem[] {
  const totals = new Map<ActivityType, number>();

  activities.forEach((activity) => {
    const key = getActivitySliceKey(activity);
    const currentTotal = totals.get(key) ?? 0;
    const nextTotal =
      metric === 'count'
        ? currentTotal + 1
        : currentTotal + (activity.summary.distanceKm ?? 0);

    totals.set(key, nextTotal);
  });

  return Array.from(totals.entries())
    .map(([activityType, value]) => ({
      label: ACTIVITY_TYPE_LABELS[activityType],
      value,
      color: ACTIVITY_TYPE_COLORS[activityType],
      filterKey: activityType,
    }))
    .sort((left, right) => {
      if (right.value !== left.value) {
        return right.value - left.value;
      }

      return left.label.localeCompare(right.label);
    });
}

function buildTimeSeries(activities: ActivityListItem[]): ActivityTimeSeriesPoint[] {
  const totalsByMonth = new Map<string, number>();

  activities.forEach((activity) => {
    const startedAt = new Date(activity.startedAt);
    if (Number.isNaN(startedAt.getTime())) {
      return;
    }

    const monthKey = `${startedAt.getUTCFullYear()}-${String(startedAt.getUTCMonth() + 1).padStart(2, '0')}-01`;
    totalsByMonth.set(monthKey, (totalsByMonth.get(monthKey) ?? 0) + 1);
  });

  return Array.from(totalsByMonth.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([date, value]) => ({
      date,
      value,
    }));
}

function getDateRange(activities: ActivityListItem[]) {
  const timestamps = activities
    .map((activity) => new Date(activity.startedAt).getTime())
    .filter((timestamp) => !Number.isNaN(timestamp));

  if (timestamps.length === 0) {
    return undefined;
  }

  return {
    startDate: new Date(Math.min(...timestamps)),
    endDate: new Date(Math.max(...timestamps)),
  };
}

export default function ActivitiesRoute() {
  const [selectedSource, setSelectedSource] = useState<ActivitySourceFilter>('all');
  const [selectedType, setSelectedType] = useState<ActivityTypeFilter>('all');

  const activitiesForSource = filterActivities(mockActivities, selectedSource, 'all');
  const activitiesForType = filterActivities(mockActivities, 'all', selectedType);
  const visibleActivities = filterActivities(
    mockActivities,
    selectedSource,
    selectedType,
  );
  const sourceCounts = countActivitiesBySource(activitiesForType);
  const typeCounts = countActivitiesByType(activitiesForSource);
  const activityBreakdown = buildBreakdown(visibleActivities, 'count');
  const distanceBreakdown = buildBreakdown(visibleActivities, 'distance');
  const timeSeries = buildTimeSeries(visibleActivities);
  const dateRange = getDateRange(visibleActivities);

  const totalSessions = visibleActivities.length;
  const totalDistanceKm = visibleActivities.reduce(
    (sum, activity) => sum + (activity.summary.distanceKm ?? 0),
    0,
  );
  const totalCalories = visibleActivities.reduce(
    (sum, activity) => sum + (activity.summary.calories ?? 0),
    0,
  );
  const sourceCount = new Set(visibleActivities.map((activity) => activity.source)).size;
  const typeCount = new Set(
    visibleActivities.map((activity) => getActivitySliceKey(activity)),
  ).size;

  const hasFilters = selectedSource !== 'all' || selectedType !== 'all';

  return (
    <ContentLayout title="Activities">
      <div className="activities-route">
        <section className="activities-route__hero" aria-labelledby="activities-hero-title">
          <div className="activities-route__hero-copy">
            <p className="activities-route__eyebrow">Connected activity dashboard</p>
            <h2 id="activities-hero-title" className="activities-route__hero-title">
              Slice your training by source, discipline, and date.
            </h2>
            <p className="activities-route__hero-lede">
              The overview, charts, and activity cards stay synchronized so you can
              narrow the view without losing the bigger picture.
            </p>
            <p className="activities-route__hero-scope">
              {visibleActivities.length > 0 ? (
                <>
                  Viewing <strong>{getSourceLabel(selectedSource)}</strong> ·{' '}
                  <strong>{getTypeLabel(selectedType)}</strong> with{' '}
                  <strong>
                    {visibleActivities.length} visible activities across {sourceCount}{' '}
                    sources and {typeCount} activity types
                  </strong>
                  .
                </>
              ) : (
                <>
                  Viewing <strong>{getSourceLabel(selectedSource)}</strong> ·{' '}
                  <strong>{getTypeLabel(selectedType)}</strong> with no matching
                  activities.
                </>
              )}
            </p>
          </div>

          <dl className="activities-route__hero-stats" aria-label="Visible activity summary">
            <div className="activities-route__hero-stat">
              <dt className="activities-route__hero-stat-label">Visible activities</dt>
              <dd className="activities-route__hero-stat-value">{formatNumber(totalSessions)}</dd>
            </div>
            <div className="activities-route__hero-stat">
              <dt className="activities-route__hero-stat-label">Distance</dt>
              <dd className="activities-route__hero-stat-value">
                {formatDistance(totalDistanceKm)}
              </dd>
            </div>
            <div className="activities-route__hero-stat">
              <dt className="activities-route__hero-stat-label">Calories</dt>
              <dd className="activities-route__hero-stat-value">
                {formatNumber(totalCalories)}
              </dd>
            </div>
          </dl>
        </section>

        <section
          className="activities-route__section activities-route__section--filters"
          aria-labelledby="filters-title"
        >
          <div className="activities-route__section-header activities-route__section-header--split">
            <div>
              <h2 id="filters-title" className="activities-route__section-title">
                Filters
              </h2>
              <p className="activities-route__section-copy">
                Click a chip to focus the dashboard. Reset clears both filters.
              </p>
            </div>

            <button
              type="button"
              className="activities-route__reset-button"
              onClick={() => {
                setSelectedSource('all');
                setSelectedType('all');
              }}
              disabled={!hasFilters}
            >
              Reset filters
            </button>
          </div>

          <div className="activities-route__filters-panel">
            <div className="activities-route__filter-group">
              <span className="activities-route__filter-label">Source</span>
              <div className="activities-route__chip-row">
                {SOURCE_OPTIONS.map((option) => {
                  const isActive = selectedSource === option.value;
                  const count =
                    option.value === 'all' ? activitiesForType.length : sourceCounts[option.value];

                  return (
                    <button
                      key={option.value}
                      type="button"
                      className={[
                        'activities-route__chip-button',
                        isActive ? 'activities-route__chip-button--active' : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() => setSelectedSource(option.value)}
                      aria-pressed={isActive}
                      aria-label={`Filter by source ${option.label}`}
                    >
                      <span className="activities-route__chip-button-label">{option.label}</span>
                      <span className="activities-route__chip-count">
                        {formatNumber(count)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="activities-route__filter-group">
              <span className="activities-route__filter-label">Type</span>
              <div className="activities-route__chip-row">
                {TYPE_OPTIONS.map((option) => {
                  const isActive = selectedType === option.value;
                  const count =
                    option.value === 'all' ? activitiesForSource.length : typeCounts[option.value];

                  if (option.value !== 'all' && count === 0 && !isActive) {
                    return null;
                  }

                  return (
                    <button
                      key={option.value}
                      type="button"
                      className={[
                        'activities-route__chip-button',
                        isActive ? 'activities-route__chip-button--active' : '',
                      ]
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() => setSelectedType(option.value)}
                      aria-pressed={isActive}
                      aria-label={`Filter by activity type ${option.label}`}
                    >
                      <span className="activities-route__chip-button-label">{option.label}</span>
                      <span className="activities-route__chip-count">
                        {formatNumber(count)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        <section
          className="activities-route__section"
          aria-labelledby="overview-title"
        >
          <div className="activities-route__section-header">
            <h2 id="overview-title" className="activities-route__section-title">
              Overview
            </h2>
            <p className="activities-route__section-copy">
              The overview, charts, and cards all reflect the visible slice of your
              activity library.
            </p>
          </div>

          <ul
            className="activities-route__agg-stats"
            aria-label="Visible activity totals"
          >
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">
                {formatNumber(totalSessions)}
              </span>
              <span className="activities-route__agg-label">Activities</span>
            </li>
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">
                {formatDistance(totalDistanceKm)}
              </span>
              <span className="activities-route__agg-label">Distance</span>
            </li>
            <li className="activities-route__agg-stat">
              <span className="activities-route__agg-value">
                {formatNumber(totalCalories)}
              </span>
              <span className="activities-route__agg-label">Calories</span>
            </li>
          </ul>

          <div className="activities-route__chart-stack">
            <ActivityTimeSeriesChart
              title="Activity volume over time"
              description="Monthly totals update with the visible activity slice."
              valueLabel="Activities"
              startDate={dateRange?.startDate}
              endDate={dateRange?.endDate}
              data={timeSeries}
              height={220}
              valueFormatter={formatNumber}
              emptyStateMessage="No visible activities match the current filters."
            />

            <div className="activities-route__charts-grid">
              <ActivityPieChart
                title="Activity mix"
                description="Sessions by activity type within the current slice."
                totalLabel="Activities"
                startDate={dateRange?.startDate}
                endDate={dateRange?.endDate}
                data={activityBreakdown}
                height={220}
                valueFormatter={formatNumber}
                emptyStateMessage="No activity types match the current filters."
              />

              <ActivityBarChart
                title="Distance by activity type"
                description="Distance totals recalculate with the active filters."
                startDate={dateRange?.startDate}
                endDate={dateRange?.endDate}
                data={distanceBreakdown}
                valueFormatter={formatDistance}
                height={220}
                emptyStateMessage="No distance data matches the current filters."
              />
            </div>
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
              {visibleActivities.length > 0
                ? `Showing ${formatNumber(visibleActivities.length)} of ${formatNumber(mockActivities.length)} activities.`
                : 'No activities match the current filters. Reset them to bring the list back.'}
            </p>
          </div>

          {visibleActivities.length > 0 ? (
            <div className="activities-route__list">
              {visibleActivities.map((activity) => {
                const activityProps =
                  activity.source === ActivitySource.WeSki
                    ? { weSkiRoutePoints: mockWeSkiRouteMapPoints }
                    : activity.source === ActivitySource.MyWhoosh
                      ? { myWhooshDetail }
                      : {};

                return (
                  <ActivityCard
                    key={activity.id}
                    activity={activity}
                    {...activityProps}
                  />
                );
              })}
            </div>
          ) : (
            <div className="activities-route__empty-state">
              <h3 className="activities-route__empty-state-title">
                Nothing matches this slice.
              </h3>
              <p className="activities-route__empty-state-copy">
                Clear the filters to restore the full activity list and dashboards.
              </p>
              <div className="activities-route__empty-state-actions">
                <button
                  type="button"
                  className="activities-route__reset-button"
                  onClick={() => {
                    setSelectedSource('all');
                    setSelectedType('all');
                  }}
                >
                  Reset filters
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </ContentLayout>
  );
}
