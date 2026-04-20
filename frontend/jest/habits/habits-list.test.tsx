import { render, screen } from "@testing-library/react";
import { HabitsList } from "@/features/habits/components/habits-list";

jest.mock("@/features/habits/api/get-habits", () => ({
  useHabits: jest.fn(),
}));

const { useHabits } = jest.requireMock("@/features/habits/api/get-habits");

describe("HabitsList", () => {
  it("shows loading state", () => {
    useHabits.mockReturnValue({ isLoading: true, isError: false, data: undefined });
    render(<HabitsList />);
    expect(screen.getByText(/Loading habits/i)).toBeInTheDocument();
  });

  it("shows empty state", () => {
    useHabits.mockReturnValue({ isLoading: false, isError: false, data: [] });
    render(<HabitsList />);
    expect(screen.getByText("No habits yet. Create your first one!")).toBeInTheDocument();
  });

  it("shows error state", () => {
    useHabits.mockReturnValue({ isLoading: false, isError: true, data: undefined });
    render(<HabitsList />);
    expect(screen.getByText("Failed to load habits.")).toBeInTheDocument();
  });
});