/// <reference types="cypress" />

describe('Activities page', () => {
  it('opens the activities page', () => {
    cy.visit('/app/activities');
    cy.url().should('include', '/app/activities');
    cy.contains('Activities').should('be.visible');
  });
});