import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockMyWhooshRouteMapPoints } from '@/mocks/mock-chart-raw-data';

import { MyWhooshRouteOverlayChart } from './my-whoosh-route-overlay-chart';

const meta = {
  title: 'Components/Charts/MyWhooshRouteOverlayChart',
  component: MyWhooshRouteOverlayChart,
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
} satisfies Meta<typeof MyWhooshRouteOverlayChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    data: mockMyWhooshRouteMapPoints,
  },
};

export const EmptyState: Story = {
  args: {
    data: [],
  },
};
