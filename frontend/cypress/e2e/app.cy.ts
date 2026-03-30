/// <reference types="cypress" />

describe('Navigation flows', () => {
  it('loads the landing page', () => {
    cy.visit('/');
    cy.contains('Habit Tracker').should('be.visible');
    cy.contains('Build better habits, one day at a time.').should('be.visible');
    cy.contains('Get started').should('be.visible');
  });

  it('navigates from landing page to dashboard', () => {
    cy.visit('/');
    cy.contains('Get started').click();
    cy.url().should('include', '/app');
    cy.contains('Dashboard').should('be.visible');
    cy.contains('Welcome back! Use the navigation to manage your habits.').should('be.visible');
    cy.contains('Habits').should('be.visible');
    cy.contains('Profile').should('be.visible');
  });

  it('opens the profile page', () => {
    cy.visit('/app/profile');
    cy.contains('Profile').should('be.visible');
    cy.contains('Manage your account settings here.').should('be.visible');
  });

  it('opens the habits page', () => {
  cy.visit('/app/habits');
  cy.contains('My Habits').should('be.visible');
  cy.contains(/Loading habits\.\.\.|Failed to load habits\./).should('be.visible');
});

it('navigates to habits page from dashboard navigation', () => {
  cy.visit('/');

  cy.contains('Get started').click();

  cy.url().should('include', '/app');
  cy.contains('Habits').click();

  cy.url().should('include', '/app/habits');
  cy.contains('My Habits').should('be.visible');
});

it('shows empty state when habits API returns no habits', () => {
  cy.intercept(
    {
      method: 'GET',
      url: '**/habits',
      middleware: true,
    },
    (req) => {
      if (req.url.includes('/app/habits')) {
        req.continue();
        return;
      }

      req.reply({
        statusCode: 200,
        body: [],
      });
    }
  ).as('getHabitsEmpty');

  cy.visit('/app/habits');

  cy.wait('@getHabitsEmpty');
  cy.contains('My Habits').should('be.visible');
  cy.contains('No habits yet. Create your first one!').should('be.visible');
});

it('shows error state when habits API fails', () => {
  cy.intercept(
    {
      method: 'GET',
      url: '**/habits',
      middleware: true,
    },
    (req) => {
      if (req.url.includes('/app/habits')) {
        req.continue();
        return;
      }

      req.reply({
        statusCode: 500,
        body: { message: 'Internal Server Error' },
      });
    }
  ).as('getHabitsError');

  cy.visit('/app/habits');

  cy.wait('@getHabitsError');
  cy.contains('My Habits').should('be.visible');
  cy.contains('Failed to load habits.').should('be.visible');
});
});