import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockPieChartByCount, mockPieChartByDistance } from '@/mocks/mock-activities';

import { ActivityBarChart } from './activity-bar-chart';

const meta = {
  title: 'Components/Charts/ActivityBarChart',
  component: ActivityBarChart,
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 'min(92vw, 820px)' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ActivityBarChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const ByCount: Story = {
  args: {
    title: 'Activities by count',
    description: 'Mock aggregate activity counts grouped by activity type.',
    data: mockPieChartByCount,
  },
};

export const ByDistance: Story = {
  args: {
    title: 'Distance by activity',
    description: 'Mock aggregate distance totals grouped by activity type.',
    data: mockPieChartByDistance,
    valueFormatter: (value: number) => `${value.toFixed(1)} km`,
  },
};