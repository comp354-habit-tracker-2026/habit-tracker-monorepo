import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router";
import { paths } from "@/config/paths";
import LandingRoute from "@/app/routes/landing";
import AppRoot from "@/app/routes/app/root";
import DashboardRoute from "@/app/routes/app/dashboard";
import NotFoundRoute from "@/app/routes/not-found";

describe("Navigation flows", () => {
  it("renders the landing page", () => {
    const router = createMemoryRouter(
      [
        { path: paths.home.path, element: <LandingRoute /> },
        {
          path: paths.app.root.path,
          element: <AppRoot />,
          children: [
            { index: true, element: <DashboardRoute /> },
            { path: paths.app.habits.path, element: <div /> },
            { path: paths.app.activities.path, element: <div /> },
            { path: paths.app.profile.path, element: <div /> },
          ],
        },
        { path: "*", element: <NotFoundRoute /> },
      ],
      { initialEntries: [paths.home.path] }
    );

    render(<RouterProvider router={router} />);
    expect(screen.getByText("Habit Tracker")).toBeInTheDocument();
    expect(screen.getByText("Build better habits, one day at a time.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Get started/i })).toBeInTheDocument();
  });

  it("renders the 404 page", () => {
    const router = createMemoryRouter(
      [
        { path: paths.home.path, element: <LandingRoute /> },
        {
          path: paths.app.root.path,
          element: <AppRoot />,
          children: [
            { index: true, element: <DashboardRoute /> },
            { path: paths.app.habits.path, element: <div /> },
            { path: paths.app.activities.path, element: <div /> },
            { path: paths.app.profile.path, element: <div /> },
          ],
        },
        { path: "*", element: <NotFoundRoute /> },
      ],
      { initialEntries: ["/does-not-exist"] }
    );

    render(<RouterProvider router={router} />);
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Go home/i })).toBeInTheDocument();
  });
});