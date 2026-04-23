import { useId } from 'react';

import type { ActivityRoutePoint } from '@/mocks/mock-chart-data';

import './my-whoosh-route-overlay-chart.css';

type MyWhooshRouteOverlayChartProps = {
  data: ActivityRoutePoint[];
  height?: number;
  emptyStateMessage?: string;
  className?: string;
};

export function MyWhooshRouteOverlayChart({
  data,
  height = 420,
  emptyStateMessage,
  className,
}: MyWhooshRouteOverlayChartProps) {
  const id = useId().replace(/:/g, '');

  if (data.length === 0) {
    return (
      <section
        className={[
          'my-whoosh-route-overlay-chart',
          'my-whoosh-route-overlay-chart--empty',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <p className="my-whoosh-route-overlay-chart__empty-copy">
          {emptyStateMessage ?? 'No MyWhoosh route points are available yet.'}
        </p>
      </section>
    );
  }

  const VIEWBOX_WIDTH = 1000;
  const VIEWBOX_HEIGHT = 620;
  const PADDING = 68;
  const xValues = data.map((point) => point.lon);
  const yValues = data.map((point) => point.lat);
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const minY = Math.min(...yValues);
  const maxY = Math.max(...yValues);
  const spanX = Math.max(maxX - minX, 0.000001);
  const spanY = Math.max(maxY - minY, 0.000001);
  const drawableWidth = VIEWBOX_WIDTH - PADDING * 2;
  const drawableHeight = VIEWBOX_HEIGHT - PADDING * 2;
  const scale = Math.min(drawableWidth / spanX, drawableHeight / spanY);
  const offsetX = (VIEWBOX_WIDTH - spanX * scale) / 2;
  const offsetY = (VIEWBOX_HEIGHT - spanY * scale) / 2;

  const points = data.map((point, index) => ({
    ...point,
    plotX: offsetX + (xValues[index] - minX) * scale,
    plotY: VIEWBOX_HEIGHT - offsetY - (yValues[index] - minY) * scale,
  }));

  const routePath = points
    .map((point, index) => {
      const command = index === 0 ? 'M' : 'L';
      return `${command}${point.plotX.toFixed(1)},${point.plotY.toFixed(1)}`;
    })
    .join(' ');

  const startPoint = points[0];
  const endPoint = points.at(-1) ?? startPoint;
  const hasDistinctEndMarker =
    startPoint.plotX !== endPoint.plotX || startPoint.plotY !== endPoint.plotY;

  return (
    <section
      className={[
        'my-whoosh-route-overlay-chart',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="my-whoosh-route-overlay-chart__visual" style={{ height }}>
        <svg
          viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
          className="my-whoosh-route-overlay-chart__svg"
          role="img"
          aria-label="Virtual route overlay with highlighted start and end points"
        >
          <defs>
            <linearGradient
              id={`${id}-background`}
              x1="0"
              y1="0"
              x2="1"
              y2="1"
            >
              <stop offset="0%" stopColor="#f6fbff" />
              <stop offset="55%" stopColor="#e7f2fb" />
              <stop offset="100%" stopColor="#d8e9f8" />
            </linearGradient>

            <pattern
              id={`${id}-grid`}
              width="72"
              height="72"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 72 0 L 0 0 0 72"
                fill="none"
                stroke="rgba(47, 95, 134, 0.12)"
                strokeWidth="1"
              />
            </pattern>

            <filter id={`${id}-shadow`} x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow
                dx="0"
                dy="16"
                stdDeviation="18"
                floodColor="rgba(22, 50, 79, 0.18)"
              />
            </filter>
          </defs>

          <rect
            width={VIEWBOX_WIDTH}
            height={VIEWBOX_HEIGHT}
            rx="28"
            fill={`url(#${id}-background)`}
          />
          <rect
            width={VIEWBOX_WIDTH}
            height={VIEWBOX_HEIGHT}
            rx="28"
            fill={`url(#${id}-grid)`}
          />

          <g filter={`url(#${id}-shadow)`}>
            <path
              d={routePath}
              className="my-whoosh-route-overlay-chart__route-shadow"
            />
            <path
              d={routePath}
              className="my-whoosh-route-overlay-chart__route"
            />
          </g>

          <circle
            cx={startPoint.plotX}
            cy={startPoint.plotY}
            r="10"
            className="my-whoosh-route-overlay-chart__point my-whoosh-route-overlay-chart__point--start"
          />

          {hasDistinctEndMarker ? (
            <circle
              cx={endPoint.plotX}
              cy={endPoint.plotY}
              r="10"
              className="my-whoosh-route-overlay-chart__point my-whoosh-route-overlay-chart__point--end"
            />
          ) : null}
        </svg>
      </div>
    </section>
  );
}
