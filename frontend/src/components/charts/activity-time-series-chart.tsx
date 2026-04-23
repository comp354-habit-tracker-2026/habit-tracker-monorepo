import { useEffect, useId, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import type { ActivityTimeSeriesPoint } from '@/mocks/activity-types';

import { formatChartDate, formatChartDateRange } from './charts-util';

import './activity-time-series-chart.css';

type ActivityTimeSeriesChartProps = {
  data: ActivityTimeSeriesPoint[];
  title?: string;
  description?: string;
  valueLabel?: string;
  startDate?: Date | string;
  endDate?: Date | string;
  height?: number;
  emptyStateMessage?: string;
  className?: string;
  valueFormatter?: (value: number) => string;
};

type NormalizedPoint = ActivityTimeSeriesPoint & {
  dateValue: number;
  shortLabel: string;
  fullLabel: string;
};

function defaultValueFormatter(value: number) {
  return new Intl.NumberFormat('en-US').format(value);
}

function normalizeAverageForDisplay(value: number) {
  return Number.isInteger(value) ? value : Number(value.toFixed(1));
}

function isDefined<T>(value: T | null): value is T {
  return value !== null;
}

export function ActivityTimeSeriesChart({
  data,
  title = 'Activities over time',
  description,
  valueLabel = 'Sessions',
  startDate,
  endDate,
  height = 320,
  emptyStateMessage = 'No time-series activity data available yet.',
  className,
  valueFormatter = defaultValueFormatter,
}: ActivityTimeSeriesChartProps) {
  const gradientId = useId().replace(/:/g, '');
  const [isChartReady, setIsChartReady] = useState(false);

  useEffect(() => {
    const frameId = requestAnimationFrame(() => setIsChartReady(true));
    return () => cancelAnimationFrame(frameId);
  }, []);

  const normalizedData = useMemo<NormalizedPoint[]>(() => {
    return data
      .map((item) => {
        const parsedDate =
          item.date instanceof Date ? item.date : new Date(item.date);

        if (Number.isNaN(parsedDate.getTime())) {
          return null;
        }

        const shortLabel = new Intl.DateTimeFormat('en-US', {
          month: 'short',
          day: 'numeric',
        }).format(parsedDate);

        return {
          ...item,
          dateValue: parsedDate.getTime(),
          shortLabel,
          fullLabel: formatChartDate(parsedDate) ?? shortLabel,
        };
      })
      .filter(isDefined)
      .sort((a, b) => a.dateValue - b.dateValue);
  }, [data]);

  const dateRange = formatChartDateRange(startDate, endDate);

  if (normalizedData.length === 0) {
    return (
      <section
        className={[
          'activity-time-series-chart',
          'activity-time-series-chart--empty',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <div className="activity-time-series-chart__header">
          <h2 className="activity-time-series-chart__title">{title}</h2>
          {description ? (
            <p className="activity-time-series-chart__description">
              {description}
            </p>
          ) : null}
          {dateRange ? (
            <p className="activity-time-series-chart__date-range">{dateRange}</p>
          ) : null}
        </div>
        <p className="activity-time-series-chart__empty-copy">
          {emptyStateMessage}
        </p>
      </section>
    );
  }

  const total = normalizedData.reduce((sum, item) => sum + item.value, 0);
  const average = total / normalizedData.length;
  const firstValue = normalizedData[0]?.value ?? 0;
  const lastValue = normalizedData.at(-1)?.value ?? 0;
  const trendDelta = lastValue - firstValue;
  const trendPercent =
    firstValue === 0 ? (lastValue === 0 ? 0 : 100) : (trendDelta / firstValue) * 100;
  const trendPrefix = trendPercent > 0 ? '+' : '';

  return (
    <section
      className={['activity-time-series-chart', className].filter(Boolean).join(' ')}
    >
      <div className="activity-time-series-chart__header">
        <h2 className="activity-time-series-chart__title">{title}</h2>
        {description ? (
          <p className="activity-time-series-chart__description">{description}</p>
        ) : null}
        {dateRange ? (
          <p className="activity-time-series-chart__date-range">{dateRange}</p>
        ) : null}
      </div>

      <div className="activity-time-series-chart__content">
        <div className="activity-time-series-chart__visual" style={{ height }}>
          {isChartReady ? (
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <AreaChart
                data={normalizedData}
                margin={{ top: 8, right: 8, left: 0, bottom: 8 }}
              >
                <defs>
                  <linearGradient
                    id={`${gradientId}-fill`}
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#3a93bb" stopOpacity={0.45} />
                    <stop offset="100%" stopColor="#3a93bb" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="shortLabel"
                  tickLine={false}
                  axisLine={false}
                  minTickGap={28}
                  tick={{ fontSize: 13 }}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) =>
                    typeof value === 'number'
                      ? valueFormatter(value)
                      : String(value ?? '')
                  }
                />
                <Tooltip
                  labelFormatter={(_, payload) => {
                    const point = payload?.[0]?.payload as
                      | NormalizedPoint
                      | undefined;
                    return point?.fullLabel ?? '';
                  }}
                  formatter={(value) =>
                    typeof value === 'number'
                      ? valueFormatter(value)
                      : String(value ?? '')
                  }
                  contentStyle={{
                    borderRadius: 12,
                    border: '1px solid #d7deea',
                    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.12)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#2f88ae"
                  strokeWidth={2.25}
                  fill={`url(#${gradientId}-fill)`}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#1f6185"
                  strokeWidth={2.5}
                  dot={{ r: 2.5, fill: '#1f6185' }}
                  activeDot={{ r: 5, fill: '#1f6185' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="activity-time-series-chart__chart-skeleton" aria-hidden="true" />
          )}
        </div>

        <ul className="activity-time-series-chart__stats" aria-label="Chart summary">
          <li className="activity-time-series-chart__stat-item">
            <span className="activity-time-series-chart__stat-label">Total {valueLabel}</span>
            <strong className="activity-time-series-chart__stat-value">
              {valueFormatter(total)}
            </strong>
          </li>
          <li className="activity-time-series-chart__stat-item">
            <span className="activity-time-series-chart__stat-label">
              Average / period
            </span>
            <strong className="activity-time-series-chart__stat-value">
              {valueFormatter(normalizeAverageForDisplay(average))}
            </strong>
          </li>
          <li className="activity-time-series-chart__stat-item">
            <span className="activity-time-series-chart__stat-label">Trend</span>
            <strong
              className={[
                'activity-time-series-chart__stat-value',
                'activity-time-series-chart__trend',
                trendPercent > 0
                  ? 'activity-time-series-chart__trend--up'
                  : trendPercent < 0
                    ? 'activity-time-series-chart__trend--down'
                    : 'activity-time-series-chart__trend--flat',
              ].join(' ')}
            >
              {trendPrefix}
              {trendPercent.toFixed(1)}%
            </strong>
          </li>
        </ul>
      </div>
    </section>
  );
}
