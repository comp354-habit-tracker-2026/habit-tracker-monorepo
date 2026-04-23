import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  mockActivitiesOverTimeByDistance,
  mockActivitiesOverTimeBySessionCount,
} from '@/mocks/mock-activities';

import { ActivityTimeSeriesChart } from './activity-time-series-chart';

const meta = {
  title: 'Components/Charts/ActivityTimeSeriesChart',
  component: ActivityTimeSeriesChart,
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 'min(94vw, 900px)' }}>
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ActivityTimeSeriesChart>;

export default meta;

type Story = StoryObj<typeof meta>;

export const SessionsOverTime: Story = {
  args: {
    title: 'Activities over time',
    description: 'Session volume trend across the last twelve weeks.',
    valueLabel: 'Sessions',
    startDate: '2026-01-01',
    endDate: '2026-03-31',
    data: mockActivitiesOverTimeBySessionCount,
  },
};

export const DistanceOverTime: Story = {
  args: {
    title: 'Distance trend',
    description: 'Weekly distance totals to monitor endurance consistency.',
    valueLabel: 'Distance',
    startDate: '2026-01-01',
    endDate: '2026-03-31',
    data: mockActivitiesOverTimeByDistance,
    valueFormatter: (value: number) => `${value.toFixed(1)} km`,
  },
};

export const StartDateOnly: Story = {
  args: {
    title: 'Activity trend since date',
    description: 'Open-ended period with only the start date provided.',
    valueLabel: 'Sessions',
    startDate: '2026-02-01',
    data: mockActivitiesOverTimeBySessionCount,
  },
};

export const EmptyStateMessage: Story = {
  args: {
    title: 'No activity trend yet',
    emptyStateMessage: 'No timeline data exists for the selected period.',
    startDate: '2026-01-01',
    endDate: '2026-03-31',
    data: [],
  },
};
