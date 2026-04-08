# Jest Unit Testing Setup

## Prerequisites
- Node.js 20.x or 22.x
- npm installed
- Frontend dependencies installed (`npm install` in `frontend/`)

## Installation
Jest is already installed as a dev dependency. No extra steps needed.

## Configuration
- Config file: `frontend/jest.config.ts`
- Tests in: `frontend/jest/`
- Setup file: `jest/setup-tests.ts`

## Running Tests Locally
- Run all tests: `npm test`
- Watch mode: `npm run test:watch`
- Run tests from a specific subfolder: `npm test -- --testPathPatterns=jest/<subfolderName>`

## Creating Jest unit tests for React

1. Create a new file under `frontend/jest/`, for example:
   - `frontend/jest/MyComponent.test.tsx`

2. Import React, your component, and testing utilities:
   ```ts
   import { render, screen } from "@testing-library/react";
   import MyComponent from "../src/components/MyComponent";
   ```

3. Write a sample test:
   ```ts
   describe("MyComponent", () => {
    it("renders the title", () => {
        render(<MyComponent title="Hello" />); 
        expect(screen.getByText("Hello")).toBeInTheDocument();
        });
    });
   ```

4. Run the test:
    - `npm test`
        - `npm run test:watch` for interactive watch mode
        - `npm test -- --testPathPatterns=jest/<subfolderName>` for running tests from a specific folder