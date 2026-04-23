/// <reference types="cypress" />

describe('Profile page', () => {
  it('renders heading and body copy on direct visit', () => {
    cy.visit('/app/profile');
    cy.contains('Profile').should('be.visible');
    cy.contains('Manage your account settings here.').should('be.visible');
  });

  it('navigates to profile from the app shell', () => {
    cy.visit('/app');

    cy.contains('Profile').click();

    cy.url().should('include', '/app/profile');
    cy.contains('Profile').should('be.visible');
    cy.contains('Manage your account settings here.').should('be.visible');
  });
});