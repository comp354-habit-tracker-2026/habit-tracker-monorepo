# G26 Test Naming Conventions

## Purpose
This document defines the naming conventions for all test files contributed 
to Group 26's automated testing suite. All contributors must follow these 
conventions to ensure consistency across the codebase.

---

## File Naming
- All test files must use **kebab-case**
- Cypress E2E test files must end in `.cy.ts`
- Jest unit test files must end in `.test.ts`

**Examples:**
- ✅ `habit-creation.cy.ts`
- ✅ `user-auth.test.ts`
- ❌ `HabitCreation.cy.ts`
- ❌ `userAuth.test.ts`

---

## Describe Block Naming
- Use plain English describing the feature being tested
- Start with a capital letter

**Examples:**
- ✅ `describe("Habit creation flow", () => {`
- ❌ `describe("habitCreation", () => {`

---

## It Block Naming
- Start with "should" to describe expected behavior

**Examples:**
- ✅ `it("should create a new habit successfully", () => {`
- ❌ `it("creates habit", () => {`

---

## Variable Naming
- Use **camelCase** for all variables
- Selector variables should be descriptive

**Examples:**
- ✅ `const habitNameInput = cy.get('[data-cy="habit-name"]')`
- ❌ `const el = cy.get('[data-cy="habit-name"]')`

---

## Data Attributes for Selectors
- Always use `data-cy` attributes for Cypress selectors
- Never select by class or ID

**Examples:**
- ✅ `cy.get('[data-cy="submit-button"]')`
- ❌ `cy.get('.submit-btn')`
- ❌ `cy.get('#submit')`
