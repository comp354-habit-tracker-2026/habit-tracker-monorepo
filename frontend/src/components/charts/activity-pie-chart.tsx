import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

import type { ActivityBreakdownItem } from '@/mocks/activity-types';

import './activity-pie-chart.css';

type ActivityPieChartProps = {
  data: ActivityBreakdownItem[];
  title?: string;
  description?: string;
  totalLabel?: string;
  height?: number;
  valueFormatter?: (value: number) => string;
};

function defaultValueFormatter(value: number) {
  return new Intl.NumberFormat('en-US').format(value);
}

export function ActivityPieChart({
  data,
  title = 'Activity breakdown',
  description,
  totalLabel = 'Total',
  height = 320,
  valueFormatter = defaultValueFormatter,
}: ActivityPieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  if (data.length === 0) {
    return (
      <section className="activity-pie-chart activity-pie-chart--empty">
        <div className="activity-pie-chart__header">
          <h2 className="activity-pie-chart__title">{title}</h2>
          {description ? (
            <p className="activity-pie-chart__description">{description}</p>
          ) : null}
        </div>
        <p className="activity-pie-chart__empty-copy">No activity data available yet.</p>
      </section>
    );
  }

  return (
    <section className="activity-pie-chart">
      <div className="activity-pie-chart__header">
        <h2 className="activity-pie-chart__title">{title}</h2>
        {description ? <p className="activity-pie-chart__description">{description}</p> : null}
      </div>

      <div className="activity-pie-chart__content">
        <div className="activity-pie-chart__visual" style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip
                formatter={(value) =>
                  typeof value === 'number' ? valueFormatter(value) : String(value ?? '')
                }
                contentStyle={{
                  borderRadius: 12,
                  border: '1px solid #d7deea',
                  boxShadow: '0 12px 32px rgba(15, 23, 42, 0.12)',
                }}
              />
              <Pie
                data={data}
                dataKey="value"
                nameKey="label"
                innerRadius={68}
                outerRadius={104}
                paddingAngle={2}
                cornerRadius={8}
                strokeWidth={0}
              >
                {data.map((entry) => (
                  <Cell key={entry.label} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          <div className="activity-pie-chart__summary" aria-hidden="true">
            <span className="activity-pie-chart__summary-label">{totalLabel}</span>
            <strong className="activity-pie-chart__summary-value">
              {valueFormatter(total)}
            </strong>
          </div>
        </div>

        <ul className="activity-pie-chart__legend" aria-label={`${title} legend`}>
          {data.map((item) => (
            <li key={item.label} className="activity-pie-chart__legend-item">
              <span
                className="activity-pie-chart__legend-swatch"
                style={{ backgroundColor: item.color }}
                aria-hidden="true"
              />
              <div className="activity-pie-chart__legend-copy">
                <span className="activity-pie-chart__legend-label">{item.label}</span>
                <span className="activity-pie-chart__legend-value">
                  {valueFormatter(item.value)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
