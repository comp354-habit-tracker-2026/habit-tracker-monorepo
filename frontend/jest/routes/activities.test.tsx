import { render, screen } from "@testing-library/react";
import ActivitiesRoute from "@/app/routes/app/activities";

describe("Activities page", () => {
  it("renders the Activities page", () => {
    render(<ActivitiesRoute />);
    expect(screen.getByText("Activities")).toBeInTheDocument();
    expect(screen.getByText(/Activities page scaffold/i)).toBeInTheDocument();
  });
});