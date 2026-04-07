/// <reference types="cypress" />

describe('Profile page', () => {
  it('opens the profile page', () => {
    cy.visit('/app/profile');
    cy.contains('Profile').should('be.visible');
    cy.contains('Manage your account settings here.').should('be.visible');
  });
});