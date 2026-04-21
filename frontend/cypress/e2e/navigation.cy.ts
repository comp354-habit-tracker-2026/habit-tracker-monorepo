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
    cy.contains(
      'Welcome back! Use the navigation to manage your habits.',
    ).should('be.visible');
  });

  it('renders dashboard content on direct /app visit', () => {
    cy.visit('/app');

    cy.contains('Dashboard').should('be.visible');
    cy.contains(
      'Welcome back! Use the navigation to manage your habits.',
    ).should('be.visible');
  });

  it('keeps app navigation usable after direct /app visit', () => {
    cy.intercept('GET', '**/habits', {
      statusCode: 200,
      body: [],
    }).as('getHabits');

    cy.visit('/app');

    cy.contains('Habits').click();
    cy.url().should('include', '/app/habits');
    cy.wait('@getHabits');
    cy.contains('My Habits').should('be.visible');

    cy.contains('Profile').click();
    cy.url().should('include', '/app/profile');
    cy.contains('Profile').should('be.visible');
    cy.contains('Manage your account settings here.').should('be.visible');
  });
  
  it('shows 404 page for unknown route and can go back home', () => {
    cy.visit('/does-not-exist', { failOnStatusCode: false });
    cy.contains('404').should('be.visible');
    cy.contains('Go home').click();
    cy.url().should('eq', Cypress.config().baseUrl + '/');
  });
});