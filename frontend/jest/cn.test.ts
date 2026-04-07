import { cn } from "../src/utils/cn";

describe("cn utility", () => {
  it("joins truthy class names and ignores falsy values", () => {
    expect(cn("foo", false, "bar", undefined, "baz")).toBe("foo bar baz");
  });
  // sample test that fails
//   it("demonstrates a failing assertion", () => {
//     // This is intentionally wrong so the test suite fails
//     expect(cn("foo", false, "bar", undefined, "baz")).toBe("foo baz");
//   });
});