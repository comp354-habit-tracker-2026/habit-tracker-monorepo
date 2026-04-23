/// <reference types="cypress" />

describe('Activities page', () => {
  beforeEach(() => {
    cy.visit('/app/activities');
  });

  it('renders the activities dashboard shell', () => {
    cy.url().should('include', '/app/activities');
    cy.contains('h1', 'Activities').should('be.visible');
    cy.contains('h2', 'Overview').should('be.visible');
    cy.contains('h2', 'Your Activities').should('be.visible');
    cy.contains('Activities over time').should('be.visible');
    cy.contains('Activity breakdown').should('be.visible');
    cy.contains('Distance by activity').should('be.visible');
  });

  it('shows aggregate totals from the mock activity data', () => {
    cy.get('[aria-label="All-time totals"] .activities-route__agg-stat').should(
      'have.length',
      3,
    );

    cy.get('[aria-label="All-time totals"] .activities-route__agg-stat')
      .eq(0)
      .should('contain.text', '86')
      .and('contain.text', 'Sessions');

    cy.get('[aria-label="All-time totals"] .activities-route__agg-stat')
      .eq(1)
      .should('contain.text', '757.1')
      .and('contain.text', 'km')
      .and('contain.text', 'Distance');

    cy.get('[aria-label="All-time totals"] .activities-route__agg-stat')
      .eq(2)
      .should('contain.text', '31,330')
      .and('contain.text', 'Calories');
  });

  it('renders the three mock activity cards with summary content', () => {
    cy.get('.activity-detail-card').should('have.length', 3);

    cy.contains('.activity-detail-card__title', 'Sommet Saint-Sauveur').should(
      'be.visible',
    );
    cy.contains(
      '.activity-detail-card__compact-stats',
      '1h 38m · 18.6 km · 11.4 km/h avg',
    ).should('be.visible');

    cy.contains('.activity-detail-card__title', 'Bike Ride').should(
      'be.visible',
    );
    cy.contains(
      '.activity-detail-card__compact-stats',
      '2h 28m · 61.7 km · 25.0 km/h avg',
    ).should('be.visible');

    cy.contains('.activity-detail-card__title', 'Indoor Ride').should(
      'be.visible',
    );
    cy.contains(
      '.activity-detail-card__compact-stats',
      '1h 12m · 34.8 km · 214 W avg',
    ).should('be.visible');
  });

  it('expands the WeSki activity card to show detailed stats', () => {
    cy.contains(
      'button.activity-detail-card__trigger',
      'Sommet Saint-Sauveur',
    ).as('weskiTrigger');

    cy.get('@weskiTrigger')
      .should('have.attr', 'aria-expanded', 'false')
      .click()
      .should('have.attr', 'aria-expanded', 'true');

    cy.get('@weskiTrigger')
      .closest('.activity-detail-card')
      .within(() => {
        cy.get('[aria-label="Activity stats"]').should('be.visible');
        cy.contains('Distance').should('be.visible');
        cy.contains('18.60').should('be.visible');
        cy.contains('Moving Time').should('be.visible');
        cy.contains('1h 38m').should('be.visible');
        cy.contains('Elevation').should('be.visible');
        cy.contains('↑742').should('be.visible');
      });
  });

  it('shows the external source link for the MapMyRun activity', () => {
    cy.contains('button.activity-detail-card__trigger', 'Bike Ride').as(
      'bikeRideTrigger',
    );

    cy.get('@bikeRideTrigger').click();

    cy.get('@bikeRideTrigger')
      .closest('.activity-detail-card')
      .within(() => {
        cy.contains('a', 'View on source')
          .should(
            'have.attr',
            'href',
            'http://www.mapmyfitness.com/workout/8700883871',
          )
          .and('have.attr', 'target', '_blank');
      });
  });

  it('shows the embedded MyWhoosh dashboard when the indoor ride is expanded', () => {
    cy.contains('button.activity-detail-card__trigger', 'Indoor Ride').as(
      'indoorRideTrigger',
    );

    cy.get('@indoorRideTrigger')
      .click()
      .should('have.attr', 'aria-expanded', 'true');

    cy.get('@indoorRideTrigger')
      .closest('.activity-detail-card')
      .within(() => {
        cy.get('[aria-label="Session headline stats"]').should('be.visible');
        cy.contains('Moving Time').should('be.visible');
        cy.contains('Avg Speed').should('be.visible');
        cy.contains('Avg Power').should('be.visible');
        cy.contains('Heart Rate').should('be.visible');
        cy.contains('Power').should('be.visible');
      });
  });
});
