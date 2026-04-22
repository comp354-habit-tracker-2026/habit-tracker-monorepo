import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockWeSkiRouteMapPoints } from '@/mocks/mock-chart-raw-data';

import { WeSkiRouteMapChart } from './we-ski-route-map-chart';

const meta = {
  title: 'Components/Charts/WeSkiRouteMapChart',
  component: WeSkiRouteMapChart,
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 'min(92vw, 1080px)' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof WeSkiRouteMapChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    data: mockWeSkiRouteMapPoints,
  },
};

export const EmptyState: Story = {
  args: {
    data: [],
  },
};
