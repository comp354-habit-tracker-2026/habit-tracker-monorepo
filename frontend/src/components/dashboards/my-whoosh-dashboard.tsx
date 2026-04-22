import { useEffect, useId, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { MyWhooshRouteOverlayChart } from '@/components/charts/my-whoosh-route-overlay-chart';
import type { ActivitySummary } from '@/mocks/activity-types';
import type {
  ActivityRoutePoint,
  ActivityStreamChartPoint,
  ActivityZoneDatum,
} from '@/mocks/mock-chart-data';

import './my-whoosh-dashboard.css';

type ZoneTabId = 'hr' | 'power' | 'speed';

type MyWhooshDashboardProps = {
  title?: string;
  startedAt?: string;
  summary: ActivitySummary;
  streamData: ActivityStreamChartPoint[];
  routeData: ActivityRoutePoint[];
  hrZones: ActivityZoneDatum[];
  powerZones: ActivityZoneDatum[];
  speedZones: ActivityZoneDatum[];
  embedded?: boolean;
  className?: string;
};

function formatDuration(seconds: number) {
  const totalMinutes = Math.round(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) {
    return `${minutes}m`;
  }
  return `${hours}h ${minutes.toString().padStart(2, '0')}m`;
}

function formatSessionDate(iso?: string) {
  if (!iso) {
    return null;
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

function formatClock(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainder = Math.floor(seconds % 60);
  return `${minutes}:${remainder.toString().padStart(2, '0')}`;
}

function ZoneBars({ zones }: { zones: ActivityZoneDatum[] }) {
  const total = zones.reduce((sum, zone) => sum + zone.minutes, 0);
  const peak = zones.reduce((max, zone) => Math.max(max, zone.minutes), 0);

  if (total === 0) {
    return (
      <p className="my-whoosh-dashboard__zones-empty">
        No zone data for this session.
      </p>
    );
  }

  return (
    <ul className="my-whoosh-dashboard__zone-list">
      {zones.map((zone) => {
        const fillWidth = peak > 0 ? (zone.minutes / peak) * 100 : 0;
        const sharePercent = (zone.minutes / total) * 100;
        return (
          <li key={zone.label} className="my-whoosh-dashboard__zone-row">
            <span className="my-whoosh-dashboard__zone-label">{zone.label}</span>
            <div className="my-whoosh-dashboard__zone-track">
              <div
                className="my-whoosh-dashboard__zone-fill"
                style={{
                  width: `${fillWidth}%`,
                  backgroundColor: zone.color,
                }}
              />
            </div>
            <span className="my-whoosh-dashboard__zone-minutes">
              {zone.minutes.toFixed(1)} min
            </span>
            <span className="my-whoosh-dashboard__zone-percent">
              {sharePercent.toFixed(0)}%
            </span>
          </li>
        );
      })}
    </ul>
  );
}

export function MyWhooshDashboard({
  title = 'Indoor Ride',
  startedAt,
  summary,
  streamData,
  routeData,
  hrZones,
  powerZones,
  speedZones,
  embedded = false,
  className,
}: MyWhooshDashboardProps) {
  const gradientId = useId().replace(/:/g, '');
  const [isChartReady, setIsChartReady] = useState(false);
  const [zoneTab, setZoneTab] = useState<ZoneTabId>('hr');

  useEffect(() => {
    const frameId = requestAnimationFrame(() => setIsChartReady(true));
    return () => cancelAnimationFrame(frameId);
  }, []);

  const streamChartData = useMemo(
    () =>
      streamData.map((point) => ({
        ...point,
        clock: formatClock(point.timeSeconds),
        heartRateBpmSafe: point.heartRateBpm > 0 ? point.heartRateBpm : null,
      })),
    [streamData],
  );

  const powerStats = useMemo(() => {
    if (streamData.length === 0) {
      return { avg: 0, peak: 0 };
    }
    let sum = 0;
    let peak = 0;
    for (const point of streamData) {
      sum += point.powerWatts;
      if (point.powerWatts > peak) {
        peak = point.powerWatts;
      }
    }
    return {
      avg: Math.round(sum / streamData.length),
      peak: Math.round(peak),
    };
  }, [streamData]);

  const hrStats = useMemo(() => {
    const live = streamData.filter((point) => point.heartRateBpm > 0);
    if (live.length === 0) {
      return { avg: 0, peak: 0 };
    }
    let sum = 0;
    let peak = 0;
    for (const point of live) {
      sum += point.heartRateBpm;
      if (point.heartRateBpm > peak) {
        peak = point.heartRateBpm;
      }
    }
    return {
      avg: Math.round(sum / live.length),
      peak: Math.round(peak),
    };
  }, [streamData]);

  const hrYDomain = useMemo<[number, number]>(() => {
    const live = streamData
      .map((point) => point.heartRateBpm)
      .filter((bpm) => bpm > 0);
    if (live.length === 0) {
      return [0, 200];
    }
    const min = Math.min(...live);
    const max = Math.max(...live);
    return [Math.max(0, Math.floor(min - 5)), Math.ceil(max + 5)];
  }, [streamData]);

  const sessionDate = formatSessionDate(startedAt);

  const zoneTabs: { id: ZoneTabId; label: string; data: ActivityZoneDatum[] }[] =
    [
      { id: 'hr', label: 'Heart Rate', data: hrZones },
      { id: 'power', label: 'Power', data: powerZones },
      { id: 'speed', label: 'Speed', data: speedZones },
    ];
  const activeTab = zoneTabs.find((tab) => tab.id === zoneTab) ?? zoneTabs[0];

  const Wrapper = embedded ? 'div' : 'section';

  return (
    <Wrapper
      className={[
        'my-whoosh-dashboard',
        embedded ? 'my-whoosh-dashboard--embedded' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      aria-label={title}
    >
      {!embedded ? (
        <header className="my-whoosh-dashboard__header">
          <div className="my-whoosh-dashboard__eyebrow">MyWhoosh · Virtual Ride</div>
          <h2 className="my-whoosh-dashboard__title">{title}</h2>
          {sessionDate ? (
            <p className="my-whoosh-dashboard__meta">{sessionDate}</p>
          ) : null}
        </header>
      ) : null}

      <div className="my-whoosh-dashboard__hero">
        <MyWhooshRouteOverlayChart data={routeData} height={380} />
      </div>

      <ul
        className="my-whoosh-dashboard__headline-stats"
        aria-label="Session headline stats"
      >
        {summary.distanceKm !== undefined ? (
          <li className="my-whoosh-dashboard__headline-stat">
            <span className="my-whoosh-dashboard__headline-value">
              {summary.distanceKm.toFixed(2)}
              <span className="my-whoosh-dashboard__headline-unit">km</span>
            </span>
            <span className="my-whoosh-dashboard__headline-label">Distance</span>
          </li>
        ) : null}
        <li className="my-whoosh-dashboard__headline-stat">
          <span className="my-whoosh-dashboard__headline-value">
            {formatDuration(summary.durationSeconds)}
          </span>
          <span className="my-whoosh-dashboard__headline-label">Moving Time</span>
        </li>
        {summary.avgSpeedKmh !== undefined ? (
          <li className="my-whoosh-dashboard__headline-stat">
            <span className="my-whoosh-dashboard__headline-value">
              {summary.avgSpeedKmh.toFixed(1)}
              <span className="my-whoosh-dashboard__headline-unit">km/h</span>
            </span>
            <span className="my-whoosh-dashboard__headline-label">Avg Speed</span>
          </li>
        ) : null}
        {summary.avgPowerWatts !== undefined ? (
          <li className="my-whoosh-dashboard__headline-stat">
            <span className="my-whoosh-dashboard__headline-value">
              {Math.round(summary.avgPowerWatts)}
              <span className="my-whoosh-dashboard__headline-unit">W</span>
            </span>
            <span className="my-whoosh-dashboard__headline-label">Avg Power</span>
          </li>
        ) : null}
        {summary.calories !== undefined ? (
          <li className="my-whoosh-dashboard__headline-stat">
            <span className="my-whoosh-dashboard__headline-value">
              {summary.calories.toLocaleString('en-US')}
            </span>
            <span className="my-whoosh-dashboard__headline-label">Calories</span>
          </li>
        ) : null}
      </ul>

      <ul
        className="my-whoosh-dashboard__secondary-stats"
        aria-label="Secondary stats"
      >
        {summary.maxSpeedKmh !== undefined ? (
          <li className="my-whoosh-dashboard__secondary-stat">
            <span className="my-whoosh-dashboard__secondary-label">Max Speed</span>
            <strong className="my-whoosh-dashboard__secondary-value">
              {summary.maxSpeedKmh.toFixed(1)} km/h
            </strong>
          </li>
        ) : null}
        {summary.avgHeartRate !== undefined ? (
          <li className="my-whoosh-dashboard__secondary-stat">
            <span className="my-whoosh-dashboard__secondary-label">Avg HR</span>
            <strong className="my-whoosh-dashboard__secondary-value">
              {summary.avgHeartRate} bpm
            </strong>
          </li>
        ) : null}
        {summary.avgCadenceRpm !== undefined ? (
          <li className="my-whoosh-dashboard__secondary-stat">
            <span className="my-whoosh-dashboard__secondary-label">Avg Cadence</span>
            <strong className="my-whoosh-dashboard__secondary-value">
              {summary.avgCadenceRpm} rpm
            </strong>
          </li>
        ) : null}
      </ul>

      <section
        className="my-whoosh-dashboard__analysis"
        aria-labelledby={`${gradientId}-analysis`}
      >
        <h3
          id={`${gradientId}-analysis`}
          className="my-whoosh-dashboard__section-title"
        >
          Analysis
        </h3>

        <div className="my-whoosh-dashboard__stream-row">
          <div className="my-whoosh-dashboard__stream-row-header">
            <h4 className="my-whoosh-dashboard__stream-row-title">Power</h4>
            <span className="my-whoosh-dashboard__stream-row-meta">
              Peak {powerStats.peak} W · Avg {powerStats.avg} W
            </span>
          </div>
          <div
            className="my-whoosh-dashboard__stream-row-chart"
            style={{ height: 160 }}
          >
            {isChartReady ? (
              <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                <AreaChart
                  data={streamChartData}
                  margin={{ top: 4, right: 12, left: 0, bottom: 4 }}
                >
                  <defs>
                    <linearGradient
                      id={`${gradientId}-power`}
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="0%" stopColor="#FC4C02" stopOpacity={0.45} />
                      <stop offset="100%" stopColor="#FC4C02" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#eef1f6"
                  />
                  <XAxis
                    dataKey="clock"
                    tickLine={false}
                    axisLine={false}
                    minTickGap={56}
                    tick={{ fontSize: 11, fill: '#6b7a8a' }}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11, fill: '#6b7a8a' }}
                    tickFormatter={(value) => `${value}`}
                    width={40}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 10,
                      border: '1px solid #d7deea',
                      boxShadow: '0 12px 32px rgba(15, 23, 42, 0.12)',
                    }}
                    formatter={(value) => [`${value} W`, 'Power']}
                    labelFormatter={(label) => `@ ${label}`}
                  />
                  <Area
                    type="monotone"
                    dataKey="powerWatts"
                    stroke="#FC4C02"
                    strokeWidth={1.5}
                    fill={`url(#${gradientId}-power)`}
                    activeDot={{ r: 4, fill: '#FC4C02' }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div
                className="my-whoosh-dashboard__stream-skeleton"
                aria-hidden="true"
              />
            )}
          </div>
        </div>

        <div className="my-whoosh-dashboard__stream-row">
          <div className="my-whoosh-dashboard__stream-row-header">
            <h4 className="my-whoosh-dashboard__stream-row-title">Heart Rate</h4>
            <span className="my-whoosh-dashboard__stream-row-meta">
              Peak {hrStats.peak} bpm · Avg {hrStats.avg} bpm
            </span>
          </div>
          <div
            className="my-whoosh-dashboard__stream-row-chart"
            style={{ height: 160 }}
          >
            {isChartReady ? (
              <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                <LineChart
                  data={streamChartData}
                  margin={{ top: 4, right: 12, left: 0, bottom: 4 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#eef1f6"
                  />
                  <XAxis
                    dataKey="clock"
                    tickLine={false}
                    axisLine={false}
                    minTickGap={56}
                    tick={{ fontSize: 11, fill: '#6b7a8a' }}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11, fill: '#6b7a8a' }}
                    width={40}
                    domain={hrYDomain}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 10,
                      border: '1px solid #d7deea',
                      boxShadow: '0 12px 32px rgba(15, 23, 42, 0.12)',
                    }}
                    formatter={(value) => [`${value} bpm`, 'Heart rate']}
                    labelFormatter={(label) => `@ ${label}`}
                  />
                  <Line
                    type="monotone"
                    dataKey="heartRateBpmSafe"
                    stroke="#c73e1d"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                    connectNulls={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div
                className="my-whoosh-dashboard__stream-skeleton"
                aria-hidden="true"
              />
            )}
          </div>
        </div>
      </section>

      <section
        className="my-whoosh-dashboard__zones"
        aria-labelledby={`${gradientId}-zones`}
      >
        <div className="my-whoosh-dashboard__zones-header">
          <h3
            id={`${gradientId}-zones`}
            className="my-whoosh-dashboard__section-title"
          >
            Training zones
          </h3>
          <div className="my-whoosh-dashboard__tabs" role="tablist">
            {zoneTabs.map((tab) => {
              const isActive = tab.id === zoneTab;
              return (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  className={[
                    'my-whoosh-dashboard__tab',
                    isActive ? 'my-whoosh-dashboard__tab--active' : '',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  onClick={() => setZoneTab(tab.id)}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
        <ZoneBars zones={activeTab.data} />
      </section>
    </Wrapper>
  );
}
