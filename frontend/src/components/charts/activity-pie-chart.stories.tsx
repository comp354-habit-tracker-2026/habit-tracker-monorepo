import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  mockPieChartByCount,
  mockPieChartByDistance,
} from '@/mocks/mock-activities';

import { ActivityPieChart } from './activity-pie-chart';

const meta = {
  title: 'Components/Charts/ActivityPieChart',
  component: ActivityPieChart,
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
} satisfies Meta<typeof ActivityPieChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const ByCount: Story = {
  args: {
    title: 'Activities by count',
    description: 'Mock aggregate activity counts grouped by activity type.',
    totalLabel: 'Sessions',
    startDate: '2026-03-01',
    endDate: '2026-03-31',
    data: mockPieChartByCount,
  },
};

export const ByDistance: Story = {
  args: {
    title: 'Distance by activity',
    description: 'Mock aggregate distance totals grouped by activity type.',
    totalLabel: 'Kilometres',
    startDate: '2026-03-01',
    endDate: '2026-03-31',
    data: mockPieChartByDistance,
    valueFormatter: (value: number) => `${value.toFixed(1)} km`,
  },
};

export const StartDateOnly: Story = {
  args: {
    title: 'Activities since start date',
    description: 'Example showing an open-ended range with only a start date.',
    totalLabel: 'Sessions',
    startDate: '2026-03-15',
    data: mockPieChartByCount,
  },
};

export const EndDateOnly: Story = {
  args: {
    title: 'Activities until end date',
    description: 'Example showing an open-ended range with only an end date.',
    totalLabel: 'Sessions',
    endDate: '2026-03-31',
    data: mockPieChartByCount,
  },
};
