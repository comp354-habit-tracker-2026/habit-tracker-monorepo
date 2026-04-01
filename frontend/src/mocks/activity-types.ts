// just a placeholder for now replace with real data when available

export type ActivitySource = 'we-ski' | 'map-my-run' | 'my-whoosh';
export type ActivitySourceFormat = 'gpx' | 'xlsx' | 'fit';
export type ActivityType = 'ski' | 'bike-ride' | 'cycling' | 'run' | 'walk';

export type ActivitySummary = {
  durationSeconds: number;
  distanceKm?: number;
  elevationGainM?: number;
  elevationLossM?: number;
  avgSpeedKmh?: number;
  maxSpeedKmh?: number;
  avgPaceMinPerKm?: number;
  maxPaceMinPerKm?: number;
  avgHeartRate?: number;
  avgCadenceRpm?: number;
  avgPowerWatts?: number;
  calories?: number;
  steps?: number;
};

export type ActivityListItem = {
  id: string;
  source: ActivitySource;
  sourceFormat: ActivitySourceFormat;
  activityType: ActivityType;
  title: string;
  startedAt: string;
  endedAt: string;
  summary: ActivitySummary;
  externalUrl?: string;
};

export type SplitPoint = {
  index: number;
  distanceKm: number;
  durationSeconds: number;
  avgSpeedKmh?: number;
  avgPaceMinPerKm?: number;
};

export type TrackPoint = {
  time: string;
  lat: number;
  lon: number;
  elevationM?: number;
  speedMps?: number;
};

export type TrackBounds = {
  north: number;
  south: number;
  east: number;
  west: number;
};

export type ActivityDetail = ActivityListItem & {
  splits?: SplitPoint[];
  track?: {
    bounds: TrackBounds;
    points: TrackPoint[];
  };
};

export type ActivityStreams = {
  time: number[];
  distanceKm?: number[];
  speedKmh?: number[];
  heartRateBpm?: number[];
  cadenceRpm?: number[];
  powerWatts?: number[];
  elevationM?: number[];
};

export type ActivityStreamPayload = {
  id: string;
  activityType: ActivityType;
  streams: ActivityStreams;
};
