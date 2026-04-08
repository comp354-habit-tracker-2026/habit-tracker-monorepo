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
      getHref: (redirectTo?: string | null) =>
        `/auth/login${redirectTo ? `?redirectTo=${encodeURIComponent(redirectTo)}` : ''}`,
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
    achievements: {
      path: 'achievements',
      getHref: () => '/app/achievements',
    },
    profile: {
      path: 'profile',
      getHref: () => '/app/profile',
    },
  },
} as const;
