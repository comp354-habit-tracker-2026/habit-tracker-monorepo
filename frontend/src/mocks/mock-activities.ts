// just a placeholder for now replace with real data when available

import type {
  ActivityDetail,
  ActivityListItem,
  ActivityStreamPayload,
} from './activity-types';

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
