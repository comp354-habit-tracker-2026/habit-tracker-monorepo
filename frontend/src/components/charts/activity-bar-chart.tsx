import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import type { ActivityBreakdownItem } from '@/mocks/activity-types';

import { formatChartDateRange } from './charts-util';

import './activity-bar-chart.css';

type ActivityBarChartProps = {
  data: ActivityBreakdownItem[];
  title?: string;
  description?: string;
  startDate?: Date | string;
  endDate?: Date | string;
  height?: number;
  showLegend?: boolean;
  emptyStateMessage?: string;
  className?: string;
  valueFormatter?: (value: number) => string;
};

function defaultValueFormatter(value: number) {
  return new Intl.NumberFormat('en-US').format(value);
}

export function ActivityBarChart({
  data,
  title = 'Activity breakdown',
  description,
  startDate,
  endDate,
  height = 320,
  showLegend = true,
  emptyStateMessage = 'No activity data available yet.',
  className,
  valueFormatter = defaultValueFormatter,
}: ActivityBarChartProps) {
  const dateRange = formatChartDateRange(startDate, endDate);

  if (data.length === 0) {
    return (
      <section
        className={[
          'activity-bar-chart',
          'activity-bar-chart--empty',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <div className="activity-bar-chart__header">
          <h2 className="activity-bar-chart__title">{title}</h2>
          {description ? (
            <p className="activity-bar-chart__description">{description}</p>
          ) : null}
          {dateRange ? (
            <p className="activity-bar-chart__date-range">{dateRange}</p>
          ) : null}
        </div>
        <p className="activity-bar-chart__empty-copy">{emptyStateMessage}</p>
      </section>
    );
  }

  return (
    <section
      className={['activity-bar-chart', className].filter(Boolean).join(' ')}
    >
      <div className="activity-bar-chart__header">
        <h2 className="activity-bar-chart__title">{title}</h2>
        {description ? (
          <p className="activity-bar-chart__description">{description}</p>
        ) : null}
        {dateRange ? (
          <p className="activity-bar-chart__date-range">{dateRange}</p>
        ) : null}
      </div>

      <div className="activity-bar-chart__content">
        <div className="activity-bar-chart__visual" style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 8, right: 8, left: 0, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="label"
                tickLine={false}
                axisLine={false}
                interval={0}
                tick={{ fontSize: 14 }}
                tickFormatter={(value) =>
                  value.charAt(0).toUpperCase() + value.slice(1)
                }
              />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip
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
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {data.map((entry) => (
                  <Cell key={entry.label} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {showLegend ? (
          <ul
            className="activity-bar-chart__legend"
            aria-label={`${title} legend`}
          >
            {data.map((item) => (
              <li key={item.label} className="activity-bar-chart__legend-item">
                <span
                  className="activity-bar-chart__legend-swatch"
                  style={{ backgroundColor: item.color }}
                  aria-hidden="true"
                />
                <div className="activity-bar-chart__legend-copy">
                  <span className="activity-bar-chart__legend-label">
                    {item.label}
                  </span>
                  <span className="activity-bar-chart__legend-value">
                    {valueFormatter(item.value)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </section>
  );
}
