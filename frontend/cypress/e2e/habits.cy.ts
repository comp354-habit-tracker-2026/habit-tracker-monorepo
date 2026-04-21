/// <reference types="cypress" />

describe('Habits page', () => {
  it('renders the habits heading', () => {
    cy.intercept(
    {
      method: 'GET',
      pathname: '/habits',
    },
    {
      statusCode: 200,
      body: [],
    }
    ).as('getHabits');

    cy.visit('/app/habits');
    cy.wait('@getHabits');

    cy.contains('My Habits').should('be.visible');
  });

  it('shows loading state while habits request is pending', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: [],
          delay: 1500,
        });
      }
    ).as('getHabitsDelayed');

    cy.visit('/app/habits');
    cy.contains(/Loading habits/i).should('be.visible');
    cy.wait('@getHabitsDelayed');
  });

  it('navigates to habits page from dashboard navigation', () => {
    cy.visit('/');
    cy.contains('Get started').click();
    cy.url().should('include', '/app');
    cy.contains('Habits').click();
    cy.url().should('include', '/app/habits');
    cy.contains('My Habits').should('be.visible');
  });

  it('shows empty state when habits API returns no habits', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: [],
        });
      }
    ).as('getHabitsEmpty');

    cy.visit('/app/habits');

    cy.wait('@getHabitsEmpty');
    cy.contains('My Habits').should('be.visible');
    cy.contains('No habits yet. Create your first one!').should('be.visible');
  });

  it('shows error state when habits API fails', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 500,
          body: { message: 'Internal Server Error' },
        });
      }
    ).as('getHabitsError');

    cy.visit('/app/habits');

    cy.wait('@getHabitsError');
    cy.contains('My Habits').should('be.visible');
    cy.contains('Failed to load habits.').should('be.visible');
  });

  it('renders returned habit names and descriptions correctly', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: [
            {
              id: 'habit-1',
              name: 'Drink Water',
              description: '8 glasses per day',
              frequency: 'daily',
            },
            {
              id: 'habit-2',
              name: 'Stretch',
              description: '',
              frequency: 'daily',
            },
          ],
        });
      }
    ).as('getHabitsSuccess');

    cy.visit('/app/habits');
    cy.wait('@getHabitsSuccess');

    cy.contains('Drink Water').should('be.visible');
    cy.contains('8 glasses per day').should('be.visible');
    cy.contains('Stretch').should('be.visible');
    cy.contains('Stretch')
      .parent()
      .should('not.contain', '8 glasses per day');
  });

  it('navigates to habit detail when a habit is clicked', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits/habit-1')) {
          req.continue();
          return;
        }

        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: [
            {
              id: 'habit-1',
              name: 'Drink Water',
              description: '8 glasses per day',
              frequency: 'daily',
            },
          ],
        });
      }
    ).as('getHabits');

    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-1',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits/habit-1')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: {
            id: 'habit-1',
            name: 'Drink Water',
            description: '8 glasses per day',
            frequency: 'daily',
          },
        });
      }
    ).as('getHabitDetail');

    cy.visit('/app/habits');
    cy.wait('@getHabits');

    cy.contains('Drink Water').click();

    cy.url().should('include', '/app/habits/habit-1');
    cy.wait('@getHabitDetail');
    cy.contains('Drink Water').should('be.visible');
    cy.contains('8 glasses per day').should('be.visible');
  });

  it('loads habit detail on deep link visit', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-99',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits/habit-99')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: {
            id: 'habit-99',
            name: 'Read Books',
            description: 'Read 20 pages daily',
            frequency: 'daily',
          },
        });
      }
    ).as('getHabitDetail');

    cy.visit('/app/habits/habit-99');

    cy.wait('@getHabitDetail');
    cy.contains('Read Books').should('be.visible');
    cy.contains('Read 20 pages daily').should('be.visible');
  });

  it('shows habit detail loading state while request is pending', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-loading',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 200,
          body: {
            id: 'habit-loading',
            name: 'Meditate',
            description: '10 minutes daily',
            frequency: 'daily',
          },
          delay: 1500,
        });
      }
    ).as('getHabitLoading');

    cy.visit('/app/habits/habit-loading');

    cy.contains(/Loading/i).should('be.visible');
    cy.wait('@getHabitLoading');
  });

  it('shows habit detail error state when fetch fails', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-error',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        req.reply({
          statusCode: 500,
          body: { message: 'Internal Server Error' },
        });
      }
    ).as('getHabitError');

    cy.visit('/app/habits/habit-error');

    cy.wait('@getHabitError');
    cy.contains('Failed to load habit.').should('be.visible');
  });

  it('sends auth header for habits list when access_token exists', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }

        expect(req.headers.authorization).to.eq('Bearer test-token');

        req.reply({
          statusCode: 200,
          body: [],
        });
      }
    ).as('getHabitsWithAuth');

    cy.visit('/app/habits', {
      onBeforeLoad(win) {
        win.localStorage.setItem('access_token', 'test-token');
      },
    });

    cy.wait('@getHabitsWithAuth');
  });

  it('omits auth header for habits list when access_token does not exist', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits')) {
          req.continue();
          return;
        }
        expect(req.headers.authorization).to.be.undefined;

        req.reply({
          statusCode: 200,
          body: [],
        });
      }
    ).as('getHabitsWithoutAuth');

    cy.visit('/app/habits', {
      onBeforeLoad(win) {
        win.localStorage.removeItem('access_token');
      },
    });

    cy.wait('@getHabitsWithoutAuth');
  });

  it('sends auth header for habit detail when access_token exists', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-auth',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits/habit-auth')) {
          req.continue();
          return;
        }

        expect(req.headers.authorization).to.eq('Bearer test-token');

        req.reply({
          statusCode: 200,
          body: {
            id: 'habit-auth',
            name: 'Journal',
            description: 'Write one entry',
            frequency: 'daily',
          },
        });
      }
    ).as('getHabitDetailWithAuth');

    cy.visit('/app/habits/habit-auth', {
      onBeforeLoad(win) {
        win.localStorage.setItem('access_token', 'test-token');
      },
    });

    cy.wait('@getHabitDetailWithAuth');
  });

  it('omits auth header for habit detail when access_token does not exist', () => {
    cy.intercept(
      {
        method: 'GET',
        url: '**/habits/habit-no-auth',
        middleware: true,
      },
      (req) => {
        if (req.url.includes('/app/habits/habit-no-auth')) {
          req.continue();
          return;
        }
        expect(req.headers.authorization).to.be.undefined;

        req.reply({
          statusCode: 200,
          body: {
            id: 'habit-no-auth',
            name: 'Walk',
            description: '30 minutes daily',
            frequency: 'daily',
          },
        });
      }
    ).as('getHabitDetailWithoutAuth');

    cy.visit('/app/habits/habit-no-auth', {
      onBeforeLoad(win) {
        win.localStorage.removeItem('access_token');
      },
    });

    cy.wait('@getHabitDetailWithoutAuth');
  });
});