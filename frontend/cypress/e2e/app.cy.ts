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
});