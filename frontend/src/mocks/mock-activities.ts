// just a placeholder for now replace with real data when available


import {
  ActivityBreakdownMetric,
  ActivitySource,
  ActivitySourceFormat,
  ActivityType,
} from './activity-types';

import type {
  ActivityAggregate,
  ActivityBreakdownItem,
  ActivityDetail,
  ActivityListItem,
  ActivityStreamPayload,
  ActivityTimeSeriesPoint,
} from './activity-types';

export const mockActivities: ActivityListItem[] = [
  {
    id: 'weski_2026_01_25',
    activityKey: ActivityType.Ski,
    source: ActivitySource.WeSki,
    sourceFormat: ActivitySourceFormat.Gpx,
    activityType: ActivityType.Ski,
    title: 'Sommet Saint-Sauveur',
    startedAt: '2026-01-25T16:16:36Z',
    endedAt: '2026-01-25T17:54:55Z',
    summary: {
      durationSeconds: 5900,
      distanceKm: 18.6,
      elevationGainM: 742,
      elevationLossM: 741,
      avgSpeedKmh: 11.4,
      maxSpeedKmh: 48.2,
      calories: 910,
    },
  },
  {
    id: 'mapmyrun_8700883871',
    activityKey: ActivityType.BikeRide,
    source: ActivitySource.MapMyRun,
    sourceFormat: ActivitySourceFormat.Xlsx,
    activityType: ActivityType.BikeRide,
    title: 'Bike Ride',
    startedAt: '2025-11-04T14:00:00Z',
    endedAt: '2025-11-04T16:27:45Z',
    summary: {
      durationSeconds: 8865,
      distanceKm: 61.67,
      avgPaceMinPerKm: 2.4,
      maxPaceMinPerKm: 1.61,
      avgSpeedKmh: 25.04,
      maxSpeedKmh: 37.24,
      calories: 1837,
    },
    externalUrl: 'http://www.mapmyfitness.com/workout/8700883871',
  },
  {
    id: 'mywhoosh_r7whm',
    activityKey: ActivityType.Cycling,
    source: ActivitySource.MyWhoosh,
    sourceFormat: ActivitySourceFormat.Fit,
    activityType: ActivityType.Cycling,
    title: 'Indoor Ride',
    startedAt: '2025-10-21T18:30:00Z',
    endedAt: '2025-10-21T19:42:00Z',
    summary: {
      durationSeconds: 4320,
      distanceKm: 34.8,
      avgSpeedKmh: 29.0,
      maxSpeedKmh: 52.7,
      avgHeartRate: 151,
      avgCadenceRpm: 86,
      avgPowerWatts: 214,
      calories: 740,
    },
  },
  {
    id: 'mapmyrun_8700883900',
    activityKey: ActivityType.Run,
    source: ActivitySource.MapMyRun,
    sourceFormat: ActivitySourceFormat.Xlsx,
    activityType: ActivityType.Run,
    title: 'Tempo Run',
    startedAt: '2026-02-08T12:15:00Z',
    endedAt: '2026-02-08T13:02:00Z',
    summary: {
      durationSeconds: 2820,
      distanceKm: 10.4,
      avgPaceMinPerKm: 4.6,
      maxPaceMinPerKm: 3.7,
      avgSpeedKmh: 13.1,
      maxSpeedKmh: 17.8,
      calories: 688,
    },
    externalUrl: 'http://www.mapmyfitness.com/workout/8700883900',
  },
  {
    id: 'mapmyrun_8700883925',
    activityKey: ActivityType.Walking,
    source: ActivitySource.MapMyRun,
    sourceFormat: ActivitySourceFormat.Xlsx,
    activityType: ActivityType.Walking,
    title: 'Lunch Walk',
    startedAt: '2026-02-10T17:30:00Z',
    endedAt: '2026-02-10T18:34:00Z',
    summary: {
      durationSeconds: 3840,
      distanceKm: 5.6,
      avgSpeedKmh: 5.4,
      maxSpeedKmh: 7.2,
      calories: 301,
      steps: 7348,
    },
  },
  {
    id: 'weski_2026_02_18_snowboard',
    activityKey: ActivityType.Snowboarding,
    source: ActivitySource.WeSki,
    sourceFormat: ActivitySourceFormat.Gpx,
    activityType: ActivityType.Snowboarding,
    title: 'Evening Snowboard Laps',
    startedAt: '2026-02-18T18:05:00Z',
    endedAt: '2026-02-18T20:12:00Z',
    summary: {
      durationSeconds: 7620,
      distanceKm: 14.8,
      elevationGainM: 812,
      elevationLossM: 811,
      avgSpeedKmh: 12.1,
      maxSpeedKmh: 44.1,
      calories: 980,
    },
  },
  {
    id: 'mywhoosh_2026_03_03_threshold',
    activityKey: ActivityType.Cycling,
    source: ActivitySource.MyWhoosh,
    sourceFormat: ActivitySourceFormat.Fit,
    activityType: ActivityType.Cycling,
    title: 'Threshold Intervals',
    startedAt: '2026-03-03T18:10:00Z',
    endedAt: '2026-03-03T19:02:00Z',
    summary: {
      durationSeconds: 3120,
      distanceKm: 29.4,
      avgSpeedKmh: 33.8,
      maxSpeedKmh: 52.6,
      avgHeartRate: 158,
      avgCadenceRpm: 91,
      avgPowerWatts: 241,
      calories: 760,
    },
  },
  {
    id: 'mywhoosh_2026_03_06_recovery',
    activityKey: ActivityType.Cycling,
    source: ActivitySource.MyWhoosh,
    sourceFormat: ActivitySourceFormat.Fit,
    activityType: ActivityType.Cycling,
    title: 'Recovery Spin',
    startedAt: '2026-03-06T06:45:00Z',
    endedAt: '2026-03-06T07:24:00Z',
    summary: {
      durationSeconds: 2340,
      distanceKm: 18.7,
      avgSpeedKmh: 30.4,
      maxSpeedKmh: 44.3,
      avgHeartRate: 141,
      avgCadenceRpm: 88,
      avgPowerWatts: 186,
      calories: 482,
    },
  },
  {
    id: 'mapmyrun_8700884001',
    activityKey: ActivityType.Run,
    source: ActivitySource.MapMyRun,
    sourceFormat: ActivitySourceFormat.Xlsx,
    activityType: ActivityType.Run,
    title: 'Recovery Run',
    startedAt: '2026-03-10T07:20:00Z',
    endedAt: '2026-03-10T08:06:00Z',
    summary: {
      durationSeconds: 2760,
      distanceKm: 8.1,
      avgPaceMinPerKm: 5.1,
      maxPaceMinPerKm: 4.0,
      avgSpeedKmh: 11.9,
      maxSpeedKmh: 16.4,
      calories: 541,
    },
    externalUrl: 'http://www.mapmyfitness.com/workout/8700884001',
  },
];

export const mockActivityDetail: ActivityDetail = {
  id: 'weski_2026_01_25',
  activityKey: ActivityType.Ski,
  source: ActivitySource.WeSki,
  sourceFormat: ActivitySourceFormat.Gpx,
  activityType: ActivityType.Ski,
  title: 'Sommet Saint-Sauveur',
  startedAt: '2026-01-25T16:16:36Z',
  endedAt: '2026-01-25T17:54:55Z',
  summary: {
    durationSeconds: 5900,
    distanceKm: 18.6,
    elevationGainM: 742,
    elevationLossM: 741,
    avgSpeedKmh: 11.4,
    maxSpeedKmh: 48.2,
    calories: 910,
  },
  splits: [
    { index: 1, distanceKm: 1, durationSeconds: 356, avgSpeedKmh: 10.1 },
    { index: 2, distanceKm: 2, durationSeconds: 318, avgSpeedKmh: 11.3 },
    { index: 3, distanceKm: 3, durationSeconds: 305, avgSpeedKmh: 11.8 },
  ],
  track: {
    bounds: {
      north: 45.8852,
      south: 45.8798,
      east: -74.1549,
      west: -74.1613,
    },
    points: [
      {
        time: '2026-01-25T16:16:36Z',
        lat: 45.8814883,
        lon: -74.1599907,
        elevationM: 213,
        speedMps: 1.08,
      },
      {
        time: '2026-01-25T16:16:37Z',
        lat: 45.8815861,
        lon: -74.1599683,
        elevationM: 223,
        speedMps: 1.45,
      },
      {
        time: '2026-01-25T16:16:38Z',
        lat: 45.8815012,
        lon: -74.1600329,
        elevationM: 216,
        speedMps: 1.72,
      },
      {
        time: '2026-01-25T16:16:39Z',
        lat: 45.8816348,
        lon: -74.1600848,
        elevationM: 231,
        speedMps: 1.52,
      },
    ],
  },
};

export const mockActivityStreams: ActivityStreamPayload = {
  id: 'mywhoosh_r7whm',
  activityType: ActivityType.Cycling,
  streams: {
    time: [0, 5, 10, 15, 20, 25, 30],
    distanceKm: [0, 0.04, 0.09, 0.14, 0.19, 0.24, 0.29],
    speedKmh: [0, 22.1, 28.4, 31.0, 30.2, 29.6, 30.5],
    heartRateBpm: [98, 112, 128, 136, 141, 145, 148],
    cadenceRpm: [0, 74, 81, 85, 87, 88, 89],
    powerWatts: [0, 145, 188, 214, 226, 221, 230],
    elevationM: [204, 204, 205, 205, 206, 206, 207],
  },
};

export const mockActivityAggregates: ActivityAggregate[] = [
  {
    activity_type: ActivityType.Cycling,
    total_distance: 412.8,
    total_duration: 5580,
    average_speed: 29.4,
    average_heart_rate: 152,
    total_calories: 12840,
    activity_count: 22,
  },
  {
    activity_type: ActivityType.Walking,
    total_distance: 84.3,
    total_duration: 2140,
    average_speed: 5.2,
    average_heart_rate: 108,
    total_calories: 4210,
    activity_count: 26,
  },
  {
    activity_type: ActivityType.Run,
    total_distance: 120.5,
    total_duration: 540,
    average_speed: 9.5,
    average_heart_rate: 145,
    total_calories: 3500,
    activity_count: 18,
  },
  {
    activity_type: ActivityType.Snowboarding,
    total_distance: 62.1,
    total_duration: 1780,
    average_speed: 14.8,
    average_heart_rate: 132,
    total_calories: 4960,
    activity_count: 9,
  },
  {
    activity_type: ActivityType.Ski,
    total_distance: 77.4,
    total_duration: 1960,
    average_speed: 12.6,
    average_heart_rate: 136,
    total_calories: 5820,
    activity_count: 11,
  },
];

const activityColors: Partial<Record<ActivityType, string>> = {
  [ActivityType.Cycling]: '#2e86ab',
  [ActivityType.Walking]: '#7d8f69',
  [ActivityType.Run]: '#c73e1d',
  [ActivityType.Snowboarding]: '#7b2cbf',
  [ActivityType.Ski]: '#f18f01',
};

export function mapActivityAggregatesToPieData(
  aggregates: ActivityAggregate[],
  metric: ActivityBreakdownMetric,
): ActivityBreakdownItem[] {
  return aggregates.map((activity) => ({
    label: activity.activity_type,
    value: activity[metric],
    color: activityColors[activity.activity_type] ?? '#8884d8',
    filterKey: activity.activity_type,
  }));
}

export const mockPieChartByCount = mapActivityAggregatesToPieData(
  mockActivityAggregates,
  ActivityBreakdownMetric.ActivityCount,
);

export const mockPieChartByDistance = mapActivityAggregatesToPieData(
  mockActivityAggregates,
  ActivityBreakdownMetric.TotalDistance,
);

export const mockPieChartByCountWithDates: ActivityBreakdownItem[] = [
  { label: ActivityType.Cycling, value: 8, color: activityColors[ActivityType.Cycling] ?? '#8884d8', date: '2026-01-05' },
  { label: ActivityType.Walking, value: 10, color: activityColors[ActivityType.Walking] ?? '#8884d8', date: '2026-01-08' },
  { label: ActivityType.Run, value: 6, color: activityColors[ActivityType.Run] ?? '#8884d8', date: '2026-01-12' },
  { label: ActivityType.Ski, value: 4, color: activityColors[ActivityType.Ski] ?? '#8884d8', date: '2026-01-20' },
  { label: ActivityType.Cycling, value: 12, color: activityColors[ActivityType.Cycling] ?? '#8884d8', date: '2026-02-03' },
  { label: ActivityType.Walking, value: 16, color: activityColors[ActivityType.Walking] ?? '#8884d8', date: '2026-02-10' },
  { label: ActivityType.Run, value: 9, color: activityColors[ActivityType.Run] ?? '#8884d8', date: '2026-02-14' },
  { label: ActivityType.Snowboarding, value: 5, color: activityColors[ActivityType.Snowboarding] ?? '#8884d8', date: '2026-02-18' },
];

export const mockPieChartByDistanceWithDates: ActivityBreakdownItem[] = [
  { label: ActivityType.Cycling, value: 98.4, color: activityColors[ActivityType.Cycling] ?? '#8884d8', date: '2026-01-05' },
  { label: ActivityType.Walking, value: 24.2, color: activityColors[ActivityType.Walking] ?? '#8884d8', date: '2026-01-08' },
  { label: ActivityType.Run, value: 42.7, color: activityColors[ActivityType.Run] ?? '#8884d8', date: '2026-01-12' },
  { label: ActivityType.Ski, value: 31.6, color: activityColors[ActivityType.Ski] ?? '#8884d8', date: '2026-01-20' },
  { label: ActivityType.Cycling, value: 144.1, color: activityColors[ActivityType.Cycling] ?? '#8884d8', date: '2026-02-03' },
  { label: ActivityType.Walking, value: 37.9, color: activityColors[ActivityType.Walking] ?? '#8884d8', date: '2026-02-10' },
  { label: ActivityType.Run, value: 55.3, color: activityColors[ActivityType.Run] ?? '#8884d8', date: '2026-02-14' },
  { label: ActivityType.Snowboarding, value: 28.8, color: activityColors[ActivityType.Snowboarding] ?? '#8884d8', date: '2026-02-18' },
];

export const mockActivitiesOverTimeBySessionCount: ActivityTimeSeriesPoint[] = [
  { date: '2026-01-05', value: 4 },
  { date: '2026-01-12', value: 5 },
  { date: '2026-01-19', value: 6 },
  { date: '2026-01-26', value: 5 },
  { date: '2026-02-02', value: 7 },
  { date: '2026-02-09', value: 8 },
  { date: '2026-02-16', value: 6 },
  { date: '2026-02-23', value: 9 },
  { date: '2026-03-02', value: 10 },
  { date: '2026-03-09', value: 9 },
  { date: '2026-03-16', value: 11 },
  { date: '2026-03-23', value: 12 },
];

export const mockActivitiesOverTimeByDistance: ActivityTimeSeriesPoint[] = [
  { date: '2026-01-05', value: 18.4 },
  { date: '2026-01-12', value: 21.7 },
  { date: '2026-01-19', value: 25.8 },
  { date: '2026-01-26', value: 24.1 },
  { date: '2026-02-02', value: 29.2 },
  { date: '2026-02-09', value: 33.5 },
  { date: '2026-02-16', value: 30.4 },
  { date: '2026-02-23', value: 35.8 },
  { date: '2026-03-02', value: 39.1 },
  { date: '2026-03-09', value: 36.9 },
  { date: '2026-03-16', value: 42.2 },
  { date: '2026-03-23', value: 45.7 },
];