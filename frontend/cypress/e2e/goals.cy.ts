
describe('Goals page', () => {
  it('should render heading and introductory copy', () => {
    cy.visit('/app/goals');
    cy.contains('Goals').should('be.visible');
  });

  it('should show + Create Goal button', () => {
    cy.visit('/app/goals');
    cy.contains('Create Goal').should('be.visible');
  });

  it('should show empty active-goals section', () => {
    cy.visit('/app/goals');
    cy.contains('Active').should('be.visible');
  });

  it('should show empty completed-goals section', () => {
    cy.visit('/app/goals');
    cy.contains('Completed').should('be.visible');
  });

  it('should load on direct visit to /app/goals', () => {
    cy.visit('/app/goals');
    cy.url().should('include', '/app/goals');
  });

  it('should navigate to Goals from app shell', () => {
    cy.visit('/app');
    cy.contains('Goals').click();
    cy.url().should('include', '/app/goals');
  });
});
