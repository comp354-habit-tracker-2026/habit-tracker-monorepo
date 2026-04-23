import { fireEvent, render, screen } from "@testing-library/react";

const mockActivitiesQuery = {
  data: undefined,
  isError: true,
  isLoading: false,
  isRefetching: false,
  isSuccess: false,
  refetch: jest.fn(),
};

jest.mock("@/features/activities/api/get-activities", () => ({
  useActivities: () => mockActivitiesQuery,
}));

jest.mock("@/components/activities/activity-card", () => ({
  ActivityCard: ({ activity }: { activity: { title: string } }) => (
    <div>{activity.title}</div>
  ),
}));

jest.mock("@/components/charts/activity-bar-chart", () => ({
  ActivityBarChart: ({ title }: { title?: string }) => <div>{title}</div>,
}));

jest.mock("@/components/charts/activity-pie-chart", () => ({
  ActivityPieChart: ({ title }: { title?: string }) => <div>{title}</div>,
}));

jest.mock("@/components/charts/activity-time-series-chart", () => ({
  ActivityTimeSeriesChart: ({ title }: { title?: string }) => <div>{title}</div>,
}));

import ActivitiesRoute from "@/app/routes/app/activities";

describe("Activities page", () => {
  it("filters the dashboard by activity type", () => {
    render(<ActivitiesRoute />);
    expect(
      screen.getByRole("heading", {
        name: /slice your training by source, discipline, and date/i,
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/demo data is showing instead/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/showing 9 of 9 activities/i),
    ).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", {
        name: /filter by activity type run/i,
      }),
    );

    expect(screen.getByText(/showing 2 of 9 activities/i)).toBeInTheDocument();
    expect(screen.getByText("Tempo Run")).toBeInTheDocument();
    expect(screen.getByText("Recovery Run")).toBeInTheDocument();
    expect(screen.queryByText("Sommet Saint-Sauveur")).not.toBeInTheDocument();
  });

  it("filters the dashboard by source", () => {
    render(<ActivitiesRoute />);

    fireEvent.click(
      screen.getByRole("button", {
        name: /filter by source mywhoosh/i,
      }),
    );

    expect(screen.getByText(/showing 3 of 9 activities/i)).toBeInTheDocument();
    expect(screen.getByText("Indoor Ride")).toBeInTheDocument();
    expect(screen.getByText("Threshold Intervals")).toBeInTheDocument();
    expect(screen.queryByText("Sommet Saint-Sauveur")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: /filter by activity type ski/i,
      }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", {
        name: /filter by activity type snowboard/i,
      }),
    ).not.toBeInTheDocument();
  });
});