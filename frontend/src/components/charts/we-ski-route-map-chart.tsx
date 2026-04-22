import type { LatLngBoundsExpression, LatLngTuple } from 'leaflet';
import { CircleMarker, MapContainer, Polyline, TileLayer } from 'react-leaflet';

import type { ActivityRoutePoint } from '@/mocks/mock-chart-data';

import 'leaflet/dist/leaflet.css';
import './we-ski-route-map-chart.css';

type WeSkiRouteMapChartProps = {
  data: ActivityRoutePoint[];
  height?: number;
  emptyStateMessage?: string;
  className?: string;
};

export function WeSkiRouteMapChart({
  data,
  height = 420,
  emptyStateMessage,
  className,
}: WeSkiRouteMapChartProps) {
  if (data.length === 0) {
    return (
      <section
        className={[
          'we-ski-route-map-chart',
          'we-ski-route-map-chart--empty',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <p className="we-ski-route-map-chart__empty-copy">
          {emptyStateMessage ?? 'No WeSki route points are available yet.'}
        </p>
      </section>
    );
  }

  const positions: LatLngTuple[] = data.map((point) => [
    point.lat,
    point.lon,
  ]);
  const bounds = positions as LatLngBoundsExpression;
  const startPosition = positions[0];
  const endPosition = positions.at(-1) ?? startPosition;
  const hasDistinctEndMarker =
    startPosition[0] !== endPosition[0] || startPosition[1] !== endPosition[1];

  return (
    <section
      className={['we-ski-route-map-chart', className].filter(Boolean).join(' ')}
    >
      <div className="we-ski-route-map-chart__visual" style={{ height }}>
        <MapContainer
          center={startPosition}
          zoom={14}
          bounds={bounds}
          boundsOptions={{ padding: [28, 28] }}
          scrollWheelZoom={false}
          className="we-ski-route-map-chart__map"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Polyline
            positions={positions}
            pathOptions={{
              color: '#1f8f63',
              weight: 6,
              opacity: 0.95,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />
          <CircleMarker
            center={startPosition}
            radius={7}
            pathOptions={{
              color: '#ffffff',
              weight: 3,
              fillColor: '#0f766e',
              fillOpacity: 1,
            }}
          />
          {hasDistinctEndMarker ? (
            <CircleMarker
              center={endPosition}
              radius={7}
              pathOptions={{
                color: '#ffffff',
                weight: 3,
                fillColor: '#b91c1c',
                fillOpacity: 1,
              }}
            />
          ) : null}
        </MapContainer>
      </div>
    </section>
  );
}
