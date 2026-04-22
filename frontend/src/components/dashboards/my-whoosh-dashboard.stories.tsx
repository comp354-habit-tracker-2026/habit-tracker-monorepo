import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  mockMyWhooshHeartRateZones,
  mockMyWhooshPowerZones,
  mockMyWhooshSpeedZones,
} from '@/mocks/mock-chart-data';
import {
  mockMyWhooshRouteMapPoints,
  mockMyWhooshStreamSeriesDense,
} from '@/mocks/mock-chart-raw-data';

import { MyWhooshDashboard } from './my-whoosh-dashboard';

const meta = {
  title: 'Components/Dashboards/MyWhooshDashboard',
  component: MyWhooshDashboard,
  parameters: {
    layout: 'padded',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 'min(94vw, 1200px)' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof MyWhooshDashboard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    startedAt: '2025-10-21T18:30:00Z',
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
    streamData: mockMyWhooshStreamSeriesDense,
    routeData: mockMyWhooshRouteMapPoints,
    hrZones: mockMyWhooshHeartRateZones,
    powerZones: mockMyWhooshPowerZones,
    speedZones: mockMyWhooshSpeedZones,
  },
};
