/// <reference types="cypress" />

describe('Login route', () => {
  beforeEach(() => {
    cy.visit('/auth/login');
  });

  it('renders username, password, sign-in button, and navigation links', () => {
    cy.contains('h1', 'Sign In').should('be.visible');

    cy.get('#username').should('be.visible');
    cy.get('#passwword').should('be.visible');
    cy.contains('button', 'Sign In').should('be.visible');

    cy.contains('a', 'Turn Back')
      .should('be.visible')
      .and('have.attr', 'href', '/');

    cy.contains('a', 'To Dashboard')
      .should('be.visible')
      .and('have.attr', 'href', '/app');
  });

  it('auto-focuses the username field on page load', () => {
    cy.focused().should('have.id', 'username');
  });

  it('navigates back home when Turn Back is clicked', () => {
    cy.contains('a', 'Turn Back').click();

    cy.url().should('eq', `${Cypress.config().baseUrl}/`);
    cy.contains('h1', 'Habit Tracker').should('be.visible');
  });

  it('navigates to /app when To Dashboard is clicked', () => {
    cy.contains('a', 'To Dashboard').click();

    cy.url().should('eq', `${Cypress.config().baseUrl}/app`);
    cy.contains('h1', 'Dashboard').should('be.visible');
  });

  it('blocks submit when required fields are empty', () => {
    cy.contains('button', 'Sign In').click();

    cy.url().should('eq', `${Cypress.config().baseUrl}/auth/login`);
    cy.contains('h1', 'Sign In').should('be.visible');
    cy.get('#username:invalid').should('exist');
  });

  it('shows success state after a valid submit', () => {
    cy.get('#username').type('testuser');
    cy.get('#passwword').type('password123');
    cy.contains('button', 'Sign In').click();

    cy.contains('h1', 'You are logged in!').should('be.visible');
  });

  it('shows Go to Home in the success state after submit', () => {
    cy.get('#username').type('testuser');
    cy.get('#passwword').type('password123');
    cy.contains('button', 'Sign In').click();

    cy.contains('a', 'Go to Home')
      .should('be.visible')
      .and('have.attr', 'href', '/');
  });

  it('shows To Dashboard in the success state after submit', () => {
    cy.get('#username').type('testuser');
    cy.get('#passwword').type('password123');
    cy.contains('button', 'Sign In').click();

    cy.contains('a', 'To Dashboard')
      .should('be.visible')
      .and('have.attr', 'href', '/app');
  });

  it('navigates to home from success state when Go to Home is clicked', () => {
    cy.get('#username').type('testuser');
    cy.get('#passwword').type('password123');
    cy.contains('button', 'Sign In').click();

    cy.contains('a', 'Go to Home').click();

    cy.url().should('eq', `${Cypress.config().baseUrl}/`);
    cy.contains('h1', 'Habit Tracker').should('be.visible');
  });

  it('navigates to dashboard from success state when To Dashboard is clicked', () => {
    cy.get('#username').type('testuser');
    cy.get('#passwword').type('password123');
    cy.contains('button', 'Sign In').click();

    cy.contains('a', 'To Dashboard').click();

    cy.url().should('eq', `${Cypress.config().baseUrl}/app`);
    cy.contains('h1', 'Dashboard').should('be.visible');
  });

  it('clears any visible error state when typing after an error is later set', () => {
    cy.get('p[aria-live="assertive"]').should('have.class', 'offscreen');

    cy.get('#username').type('a');
    cy.get('#passwword').type('b');

    cy.get('p[aria-live="assertive"]').should('have.class', 'offscreen');
  });
});