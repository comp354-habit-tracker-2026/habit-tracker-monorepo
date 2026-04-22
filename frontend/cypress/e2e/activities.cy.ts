/// <reference types="cypress" />

describe('Activities page', () => {
  it('opens the activities page', () => {
    cy.visit('/app/activities');
    cy.url().should('include', '/app/activities');
    cy.contains('Activities').should('be.visible');
  });

  it('should render the Activities heading', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 200, body: { results: [] } }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.contains('h1', 'Activities').should('be.visible');
  });

  it('should show loading skeleton while request is pending', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      (req) => {
        req.reply({
          statusCode: 200,
          body: { results: [] },
          delay: 1500,
        });
      }
    ).as('getActivitiesDelayed');

    cy.visit('/app/activities');
    cy.get('[aria-label="Loading activities"]').should('be.visible');
    cy.wait('@getActivitiesDelayed');
  });

  it('should show empty state when API returns no activities', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 200, body: { results: [] } }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('No activities yet').should('be.visible');
  });

  it('should show error state when API fails', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 500, body: { message: 'Internal Server Error' } }
    ).as('getActivitiesError');

    cy.visit('/app/activities');
    cy.wait('@getActivitiesError');
    cy.get('[role="alert"]').should('be.visible');
    cy.contains('Failed to load activities').should('be.visible');
  });

  it('should re-trigger activities request when Retry is clicked', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 500, body: { message: 'Internal Server Error' } }
    ).as('getActivitiesError');

    cy.visit('/app/activities');

    cy.contains('Failed to load activities', { timeout: 10000 }).should('be.visible');

    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 200, body: { results: [] } }
    ).as('retryRequest');

    cy.contains('button', 'Retry').click();
    cy.wait('@retryRequest');
  });

  it('should re-trigger activities request when Sync Activities is clicked', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 200, body: { results: [] } }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');

    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      { statusCode: 200, body: { results: [] } }
    ).as('syncRequest');

    cy.contains('button', 'Sync Activities').click();
    cy.wait('@syncRequest');
  });

  it('should render activity cards from API response', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200,
        body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: 5.0,
              calories: 300,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z',
            },
          ],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.get('.activity-card').should('have.length', 1);
  });

  it('should show activity type on card', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200,
        body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.get('.activity-card__title').should('contain', 'Running');
  });

  it('should show formatted date on card', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200,
        body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.get('.activity-card__date').should('contain', 'Jan');
  });

  it('should show duration formatting for less than 60 minutes', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 45,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('45 min').should('be.visible');
  });

  it('should show duration formatting for exact hours', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 120,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('2h').should('be.visible');
  });

  it('should show duration formatting for mixed hours and minutes', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 90,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('1h 30m').should('be.visible');
  });

  it('should show distance only when non-null', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: 5.0,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('5 km').should('be.visible');
  });

  it('should not show distance when null', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('Distance').should('not.exist');
  });

  it('should show calories only when non-null', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: 300,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('300').should('be.visible');
  });

  it('should not show calories when null', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }],
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');
    cy.contains('Calories').should('not.exist');
  });

  it('should re-fetch data when Sync button is clicked in success state', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }]
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');

    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }]
        }
      }
    ).as('syncRequest');

    cy.contains('button', 'Sync').click();
    cy.wait('@syncRequest');
  });

  it('should show Syncing label while refetch is in flight', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      {
        statusCode: 200, body: {
          results: [
            {
              id: '1',
              activity_type: 'Running',
              duration: 30,
              date: '2024-01-15',
              provider: 'manual',
              external_id: null,
              distance: null,
              calories: null,
              created_at: '2024-01-15T10:00:00Z',
              updated_at: '2024-01-15T10:00:00Z'
            }]
        }
      }
    ).as('getActivities');

    cy.visit('/app/activities');
    cy.wait('@getActivities');

    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      (req) => {
        req.reply({
          statusCode: 200,
          body: { results: [] },
          delay: 1500,
        });
      }
    ).as('slowSync');

    cy.contains('button', 'Sync').click();
    cy.contains('Syncing...').should('be.visible');
    cy.wait('@slowSync');
  });

  it('should send auth header when access_token exists in localStorage', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      (req) => {
        expect(req.headers.authorization).to.eq('Bearer test-token-123');
        req.reply({
          statusCode: 200,
          body: { results: [] },
        });
      }
    ).as('getActivities');

    cy.visit('/app/activities', {
      onBeforeLoad: (win) => {
        win.localStorage.setItem('access_token', 'test-token-123');
      }
    });

    cy.wait('@getActivities');
  });

  it('omits auth header when access_token does not exist in localStorage', () => {
    cy.intercept(
      { method: 'GET', pathname: '/api/v1/activities/' },
      (req) => {
        expect(req.headers.authorization).to.be.undefined;
        
        req.reply({
          statusCode: 200,
          body: { results: [] },
        });
      }
    ).as('getActivitiesWithoutAuth');

    cy.visit('/app/activities', {
      onBeforeLoad: (win) => {
        win.localStorage.removeItem('access_token'); 
      }
    });

    cy.wait('@getActivitiesWithoutAuth');
  });
});
