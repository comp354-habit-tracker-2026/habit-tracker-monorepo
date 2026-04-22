import { render, screen } from "@testing-library/react";
import ProfileRoute from "@/app/routes/app/profile";

describe("Profile page", () => {
  it("renders the Profile page content", () => {
    render(<ProfileRoute />);
    expect(screen.getByText("Profile")).toBeInTheDocument();
    expect(screen.getByText("Manage your account settings here.")).toBeInTheDocument();
  });
});