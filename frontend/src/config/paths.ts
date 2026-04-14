/**
 * Centralised route path definitions.
 *
 * Use these helpers everywhere instead of hard-coded strings so that
 * renaming a route only requires a change in one place.
 */
export const paths = {
  home: {
    path: '/',
    getHref: () => '/',
  },

  auth: {
    login: {
      path: '/auth/login',
      getHref: () => '/auth/login'
    },
    register: {
      path: '/auth/register',
      getHref: (redirectTo?: string | null) =>
        `/auth/register${redirectTo ? `?redirectTo=${encodeURIComponent(redirectTo)}` : ''}`,
    },
  },

  app: {
    root: {
      path: '/app',
      getHref: () => '/app',
    },
    dashboard: {
      path: '',
      getHref: () => '/app',
    },
    habits: {
      path: 'habits',
      getHref: () => '/app/habits',
    },
    habit: {
      path: 'habits/:habitId',
      getHref: (id: string) => `/app/habits/${id}`,
    },
    profile: {
      path: 'profile',
      getHref: () => '/app/profile',
    },
    activities: { //added this code developed from chatGPT (by lauren)
      path: 'activities',
    consentTest: {
      path: 'consent-test',
      getHref: () => '/app/consent-test',
    },
    activities: {
      path: 'activities',
      getHref: () => '/app/activities',
    },
    goals: { //Goals page route
      path:'goals',
      getHref: ()=>'/app/goals'
    },
  },
} as const }