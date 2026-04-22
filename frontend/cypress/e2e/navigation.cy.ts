/// <reference types="cypress" />

describe('Public routes and app shell navigation', () => {
  describe('Public routes', () => {
    it('renders landing page title, tagline, and primary links', () => {
      cy.visit('/');

      cy.contains('h1', 'Habit Tracker').should('be.visible');
      cy.contains('Build better habits, one day at a time.').should('be.visible');

      cy.contains('a', 'Get started')
        .should('be.visible')
        .and('have.attr', 'href', '/app');

      cy.contains('a', 'Log In')
        .should('be.visible')
        .and('have.attr', 'href', '/auth/login');
    });

    it('navigates from landing page Get started to /app', () => {
      cy.visit('/');

      cy.contains('a', 'Get started').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app`);
      cy.contains('h1', 'Dashboard').should('be.visible');
      cy.contains('Welcome back! Use the navigation to manage your habits.').should(
        'be.visible',
      );
    });

    it('navigates from landing page Log In to /auth/login', () => {
      cy.visit('/');

      cy.contains('a', 'Log In').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/auth/login`);
      cy.contains('h1', 'Sign In').should('be.visible');
    });

    it('shows 404 page for an unknown route', () => {
      cy.visit('/does-not-exist', { failOnStatusCode: false });

      cy.contains('h1', '404 – Page not found').should('be.visible');
      cy.contains('The page you are looking for does not exist.').should('be.visible');
      cy.contains('a', 'Go home').should('be.visible');
    });

    it('returns to / when Go home is clicked on the 404 page', () => {
      cy.visit('/does-not-exist', { failOnStatusCode: false });

      cy.contains('a', 'Go home').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/`);
      cy.contains('h1', 'Habit Tracker').should('be.visible');
    });
  });

  describe('App shell and navigation', () => {
    const assertNavVisible = () => {
      cy.contains('a', 'Dashboard').should('be.visible');
      cy.contains('a', 'Habits').should('be.visible');
      cy.contains('a', 'Activities').should('be.visible');
      cy.contains('a', 'Goals').should('be.visible');
      cy.contains('a', 'Profile').should('be.visible');
    };

    it('/app loads dashboard by default', () => {
      cy.visit('/app');

      cy.url().should('eq', `${Cypress.config().baseUrl}/app`);
      cy.contains('h1', 'Dashboard').should('be.visible');
      cy.contains('Welcome back! Use the navigation to manage your habits.').should(
        'be.visible',
      );
    });

    it('shows app nav on /app', () => {
      cy.visit('/app');

      assertNavVisible();
    });

    it('shows app nav on /app/habits', () => {
      cy.visit('/app/habits');

      assertNavVisible();
      cy.contains('h1', 'Habits').should('be.visible');
    });

    it('shows app nav on /app/activities', () => {
      cy.visit('/app/activities');

      assertNavVisible();
      cy.contains('h1', 'Activities').should('be.visible');
    });

    it('shows app nav on /app/goals', () => {
      cy.visit('/app/goals');

      assertNavVisible();
      cy.contains('h1', 'Goals').should('be.visible');
    });

    it('shows app nav on /app/profile', () => {
      cy.visit('/app/profile');

      assertNavVisible();
      cy.contains('h1', 'Profile').should('be.visible');
    });

    it('navigates to /app when Dashboard nav link is clicked', () => {
      cy.visit('/app/profile');

      cy.contains('a', 'Dashboard').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app`);
      cy.contains('h1', 'Dashboard').should('be.visible');
    });

    it('navigates to /app/habits when Habits nav link is clicked', () => {
      cy.visit('/app');

      cy.contains('a', 'Habits').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/habits`);
      cy.contains('h1', 'Habits').should('be.visible');
    });

    it('navigates to /app/activities when Activities nav link is clicked', () => {
      cy.visit('/app');

      cy.contains('a', 'Activities').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/activities`);
      cy.contains('h1', 'Activities').should('be.visible');
    });

    it('navigates to /app/goals when Goals nav link is clicked', () => {
      cy.visit('/app');

      cy.contains('a', 'Goals').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/goals`);
      cy.contains('h1', 'Goals').should('be.visible');
    });

    it('navigates to /app/profile when Profile nav link is clicked', () => {
      cy.visit('/app');

      cy.contains('a', 'Profile').click();

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/profile`);
      cy.contains('h1', 'Profile').should('be.visible');
    });

    it('supports direct visit to /app without first loading /', () => {
      cy.visit('/app');

      cy.contains('h1', 'Dashboard').should('be.visible');
      assertNavVisible();
    });

    it('supports direct visit to /app/habits without first loading /', () => {
      cy.visit('/app/habits');

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/habits`);
      cy.contains('h1', 'Habits').should('be.visible');
      assertNavVisible();
    });

    it('supports direct visit to /app/activities without first loading /', () => {
      cy.visit('/app/activities');

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/activities`);
      cy.contains('h1', 'Activities').should('be.visible');
      assertNavVisible();
    });

    it('supports direct visit to /app/goals without first loading /', () => {
      cy.visit('/app/goals');

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/goals`);
      cy.contains('h1', 'Goals').should('be.visible');
      assertNavVisible();
    });

    it('supports direct visit to /app/profile without first loading /', () => {
      cy.visit('/app/profile');

      cy.url().should('eq', `${Cypress.config().baseUrl}/app/profile`);
      cy.contains('h1', 'Profile').should('be.visible');
      assertNavVisible();
    });
  });
});