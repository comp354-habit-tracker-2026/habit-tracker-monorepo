// just a placeholder for now replace with real data when available

import type {
  ActivityAggregate,
  ActivityBreakdownItem,
  ActivityBreakdownMetric,
  ActivityDetail,
  ActivityListItem,
  ActivityStreamPayload,
} from './activity-types';

function toLocalDateKey(value: string | Date) {
  const date = new Date(value);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

function toLocalDate(value: string | Date) {
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-').map(Number);

    return new Date(year, month - 1, day);
  }

  const date = new Date(value);

  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export const mockActivities: ActivityListItem[] = [
  {
    id: 'weski_2026_01_25',
    source: 'we-ski',
    sourceFormat: 'gpx',
    activityType: 'ski',
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
    id: 'mapmyrun_8700883999',
    source: 'map-my-run',
    sourceFormat: 'xlsx',
    activityType: 'run',
    title: 'Evening Run',
    startedAt: '2025-11-04T18:15:00Z',
    endedAt: '2025-11-04T19:02:00Z',
    summary: {
      durationSeconds: 2820,
      distanceKm: 8.2,
      avgPaceMinPerKm: 5.7,
      maxPaceMinPerKm: 4.6,
      avgSpeedKmh: 10.2,
      maxSpeedKmh: 13.1,
      avgHeartRate: 154,
      calories: 496,
    },
    externalUrl: 'http://www.mapmyfitness.com/workout/8700883999',
  },
  {
    id: 'mapmyrun_8700883871',
    source: 'map-my-run',
    sourceFormat: 'xlsx',
    activityType: 'bike-ride',
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
    id: 'mywhoosh_recovery_2025_11_05',
    source: 'my-whoosh',
    sourceFormat: 'fit',
    activityType: 'cycling',
    title: 'Recovery Spin',
    startedAt: '2025-11-05T07:10:00Z',
    endedAt: '2025-11-05T07:55:00Z',
    summary: {
      durationSeconds: 2700,
      distanceKm: 18.4,
      avgSpeedKmh: 24.5,
      maxSpeedKmh: 33.8,
      avgHeartRate: 132,
      avgCadenceRpm: 89,
      avgPowerWatts: 162,
      calories: 382,
    },
  },
  {
    id: 'mapmyrun_walk_2025_11_06',
    source: 'map-my-run',
    sourceFormat: 'xlsx',
    activityType: 'walking',
    title: 'Morning Walk',
    startedAt: '2025-11-06T12:20:00Z',
    endedAt: '2025-11-06T13:05:00Z',
    summary: {
      durationSeconds: 2700,
      distanceKm: 4.9,
      avgSpeedKmh: 6.5,
      calories: 221,
      steps: 6120,
    },
  },
  {
    id: 'mywhoosh_r7whm',
    source: 'my-whoosh',
    sourceFormat: 'fit',
    activityType: 'cycling',
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
];

export const mockActivityCalendarByDate = mockActivities.reduce(
  (calendar, activity) => {
    const dateKey = toLocalDateKey(activity.startedAt);
    const activitiesForDay = calendar.get(dateKey) ?? [];

    activitiesForDay.push(activity);
    calendar.set(dateKey, activitiesForDay);

    return calendar;
  },
  new Map<string, ActivityListItem[]>(),
);

export const mockActivityCalendarDays = [...mockActivityCalendarByDate.entries()]
  .map(([dateKey, activities]) => ({
    dateKey,
    date: toLocalDate(dateKey),
    activities,
  }))
  .sort((left, right) => right.date.getTime() - left.date.getTime());

export function getMockActivitiesForDate(date: Date) {
  return mockActivityCalendarByDate.get(toLocalDateKey(date)) ?? [];
}

export function formatMockActivityDate(date: Date) {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export const mockActivityDetail: ActivityDetail = {
  id: 'weski_2026_01_25',
  source: 'we-ski',
  sourceFormat: 'gpx',
  activityType: 'ski',
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
  activityType: 'cycling',
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
    activity_type: 'cycling',
    total_distance: 412.8,
    total_duration: 5580,
    average_speed: 29.4,
    average_heart_rate: 152,
    total_calories: 12840,
    activity_count: 22,
  },
  {
    activity_type: 'walking',
    total_distance: 84.3,
    total_duration: 2140,
    average_speed: 5.2,
    average_heart_rate: 108,
    total_calories: 4210,
    activity_count: 26,
  },
  {
    activity_type: 'run',
    total_distance: 120.5,
    total_duration: 540,
    average_speed: 9.5,
    average_heart_rate: 145,
    total_calories: 3500,
    activity_count: 18,
  },
  {
    activity_type: 'snowboarding',
    total_distance: 62.1,
    total_duration: 1780,
    average_speed: 14.8,
    average_heart_rate: 132,
    total_calories: 4960,
    activity_count: 9,
  },
  {
    activity_type: 'ski',
    total_distance: 77.4,
    total_duration: 1960,
    average_speed: 12.6,
    average_heart_rate: 136,
    total_calories: 5820,
    activity_count: 11,
  },
];

const activityColors: Record<string, string> = {
  cycling: '#2e86ab',
  walking: '#7d8f69',
  run: '#c73e1d',
  snowboarding: '#7b2cbf',
  ski: '#f18f01',
};

export function mapActivityAggregatesToPieData(
  aggregates: ActivityAggregate[],
  metric: ActivityBreakdownMetric,
): ActivityBreakdownItem[] {
  return aggregates.map((activity) => ({
    label: activity.activity_type,
    value: activity[metric],
    color: activityColors[activity.activity_type] ?? '#8884d8',
  }));
}

export const mockPieChartByCount = mapActivityAggregatesToPieData(
  mockActivityAggregates,
  'activity_count',
);

export const mockPieChartByDistance = mapActivityAggregatesToPieData(
  mockActivityAggregates,
  'total_distance',
);