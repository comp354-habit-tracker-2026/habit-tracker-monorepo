# Cypress E2E Testing Setup

## Prerequisites
- Node.js 20.x or 22.x
- npm installed
- Frontend dependencies installed (`npm install` in `frontend/`)

## Installation
Cypress is already installed as a dev dependency. No extra steps needed.

## Configuration
- Config file: `frontend/cypress.config.ts`
- Tests in: `frontend/cypress/e2e/`
- Fixtures in: `frontend/cypress/fixtures/`

## Running Tests Locally
- Open Cypress UI: `npm run cypress:open`
- Run headless: `npm run cypress:run`
- CI mode: `npm run cypress:ci`

## Creating Cypress E2E tests for React

1. Create a new file under `frontend/cypress/e2e/`, for example:
   - `frontend/cypress/e2e/home-page.cy.ts`

2. Use Cypress commands to visit the app and assert behavior:
   ```ts
   describe("Home page", () => {
     it("loads and shows the app title", () => {
       cy.visit("/");
       cy.contains("Habit Tracker").should("be.visible");
     });
   });
   ```

3. Run Cypress locally:
    - `npm run cypress:open` to open the Cypress UI
    - `npm run cypress:run` to run headlessly.