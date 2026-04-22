import { useState } from 'react';

import { WeSkiRouteMapChart } from '@/components/charts/we-ski-route-map-chart';
import { MyWhooshDashboard } from '@/components/dashboards/my-whoosh-dashboard';
import { ActivitySource, ActivityType } from '@/mocks/activity-types';
import type { ActivityListItem, ActivitySummary } from '@/mocks/activity-types';
import type {
  ActivityRoutePoint,
  ActivityStreamChartPoint,
  ActivityZoneDatum,
} from '@/mocks/mock-chart-data';

import './activity-card.css';

export type MyWhooshDetailData = {
  streamData: ActivityStreamChartPoint[];
  routeData: ActivityRoutePoint[];
  hrZones: ActivityZoneDatum[];
  powerZones: ActivityZoneDatum[];
  speedZones: ActivityZoneDatum[];
};

type ActivityCardProps = {
  activity: ActivityListItem;
  weSkiRoutePoints?: ActivityRoutePoint[];
  myWhooshDetail?: MyWhooshDetailData;
};

type StatEntry = {
  label: string;
  number: string;
  unit?: string;
};

const ACTIVITY_TYPE_META: Record<ActivityType, { label: string; color: string }> = {
  [ActivityType.Ski]: { label: 'Ski', color: '#f18f01' },
  [ActivityType.BikeRide]: { label: 'Bike Ride', color: '#2e86ab' },
  [ActivityType.Cycling]: { label: 'Cycling', color: '#2e86ab' },
  [ActivityType.Run]: { label: 'Run', color: '#c73e1d' },
  [ActivityType.Walking]: { label: 'Walk', color: '#7d8f69' },
  [ActivityType.Snowboarding]: { label: 'Snowboard', color: '#7b2cbf' },
};

function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) {
    return `${minutes}m`;
  }
  return `${hours}h ${minutes.toString().padStart(2, '0')}m`;
}

function formatActivityDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

function buildCompactStats(summary: ActivitySummary): string {
  const parts: string[] = [formatDuration(summary.durationSeconds)];
  if (summary.distanceKm !== undefined) {
    parts.push(`${summary.distanceKm.toFixed(1)} km`);
  }
  if (summary.avgPowerWatts !== undefined) {
    parts.push(`${Math.round(summary.avgPowerWatts)} W avg`);
  } else if (summary.avgSpeedKmh !== undefined) {
    parts.push(`${summary.avgSpeedKmh.toFixed(1)} km/h avg`);
  }
  return parts.join(' · ');
}

function buildDetailStats(summary: ActivitySummary): StatEntry[] {
  const stats: StatEntry[] = [];
  if (summary.distanceKm !== undefined) {
    stats.push({
      label: 'Distance',
      number: summary.distanceKm.toFixed(2),
      unit: 'km',
    });
  }
  stats.push({ label: 'Moving Time', number: formatDuration(summary.durationSeconds) });
  if (summary.avgSpeedKmh !== undefined) {
    stats.push({
      label: 'Avg Speed',
      number: summary.avgSpeedKmh.toFixed(1),
      unit: 'km/h',
    });
  }
  if (summary.maxSpeedKmh !== undefined) {
    stats.push({
      label: 'Max Speed',
      number: summary.maxSpeedKmh.toFixed(1),
      unit: 'km/h',
    });
  }
  if (summary.elevationGainM !== undefined) {
    stats.push({
      label: 'Elevation',
      number: `↑${summary.elevationGainM}`,
      unit: 'm',
    });
  }
  if (summary.avgPowerWatts !== undefined) {
    stats.push({
      label: 'Avg Power',
      number: String(Math.round(summary.avgPowerWatts)),
      unit: 'W',
    });
  }
  if (summary.avgHeartRate !== undefined) {
    stats.push({
      label: 'Avg HR',
      number: String(summary.avgHeartRate),
      unit: 'bpm',
    });
  }
  if (summary.calories !== undefined) {
    stats.push({
      label: 'Calories',
      number: summary.calories.toLocaleString('en-US'),
    });
  }
  return stats;
}

function StatRow({ summary }: { summary: ActivitySummary }) {
  const stats = buildDetailStats(summary);
  if (stats.length === 0) {
    return null;
  }
  return (
    <ul className="activity-card__stat-row" aria-label="Activity stats">
      {stats.map((stat) => (
        <li key={stat.label} className="activity-card__stat">
          <span className="activity-card__stat-value">
            {stat.number}
            {stat.unit ? (
              <span className="activity-card__stat-unit">{stat.unit}</span>
            ) : null}
          </span>
          <span className="activity-card__stat-label">{stat.label}</span>
        </li>
      ))}
    </ul>
  );
}

export function ActivityCard({ activity, weSkiRoutePoints, myWhooshDetail }: ActivityCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  const typeMeta =
    ACTIVITY_TYPE_META[activity.activityType] ?? {
      label: activity.activityType,
      color: '#94a3b8',
    };

  function renderDetail() {
    if (activity.source === ActivitySource.WeSki && weSkiRoutePoints) {
      return (
        <>
          <StatRow summary={activity.summary} />
          <div className="activity-card__map">
            <WeSkiRouteMapChart data={weSkiRoutePoints} height={340} />
          </div>
        </>
      );
    }

    if (activity.source === ActivitySource.MyWhoosh && myWhooshDetail) {
      return (
        <MyWhooshDashboard
          embedded
          startedAt={activity.startedAt}
          summary={activity.summary}
          {...myWhooshDetail}
        />
      );
    }

    return (
      <>
        <StatRow summary={activity.summary} />
        {activity.externalUrl ? (
          <a
            href={activity.externalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="activity-card__external-link"
          >
            View on source ↗
          </a>
        ) : null}
      </>
    );
  }

  return (
    <article
      className={[
        'activity-card',
        isOpen ? 'activity-card--open' : '',
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <button
        type="button"
        className="activity-card__trigger"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-label={`${isOpen ? 'Collapse' : 'Expand'} ${activity.title}`}
      >
        <span
          className="activity-card__badge"
          style={{ backgroundColor: typeMeta.color }}
        >
          {typeMeta.label}
        </span>
        <div className="activity-card__info">
          <span className="activity-card__title">{activity.title}</span>
          <span className="activity-card__compact-stats">
            {buildCompactStats(activity.summary)}
          </span>
        </div>
        <span className="activity-card__date">
          {formatActivityDate(activity.startedAt)}
        </span>
        <span className="activity-card__chevron" aria-hidden="true" />
      </button>

      {isOpen ? (
        <div className="activity-card__detail">{renderDetail()}</div>
      ) : null}
    </article>
  );
}
