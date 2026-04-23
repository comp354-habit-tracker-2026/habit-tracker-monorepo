import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";

import AppRoot from "@/app/routes/app/root";
import HealthRoute from "@/app/routes/app/health";
import { paths } from "@/config/paths";
import { apiClient } from "@/lib/api-client";

jest.mock("@/lib/api-client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Health route", () => {
  const mockedApiClient = apiClient as { get: jest.Mock };

  beforeEach(() => {
    mockedApiClient.get.mockReset();
  });

  it("renders /app/health and displays mocked health response", async () => {
    mockedApiClient.get.mockResolvedValue({
      status: "healthy",
      timestamp: new Date().toISOString(),
      checks: {
        database: {
          status: "healthy",
          message: "Database is responding",
          timestamp: new Date().toISOString(),
        },
      },
      summary: {
        total: 1,
        healthy: 1,
        unhealthy: 0,
      },
    });

    const router = createMemoryRouter(
      [
        {
          path: paths.app.root.path,
          element: <AppRoot />,
          children: [
            {
              path: paths.app.health.path,
              element: <HealthRoute />,
            },
          ],
        },
      ],
      { initialEntries: [paths.app.health.getHref()] }
    );

    render(<RouterProvider router={router} />);

    expect(await screen.findByText("System Health Dashboard")).toBeInTheDocument();
    expect(await screen.findByText("Overall Status: HEALTHY")).toBeInTheDocument();
    expect(mockedApiClient.get).toHaveBeenCalledWith("/api/v1/health/");
  });
});
