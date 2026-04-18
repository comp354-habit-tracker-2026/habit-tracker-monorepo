import * as React from 'react';
import { useMemo } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router';

import { paths } from '@/config/paths';

/**
 * All routes use lazy() so that each page is only loaded when visited.
 * This keeps the initial bundle small regardless of how many features
 * are added over time.
 *
 * To add a new route:
 * 1. Create the file under src/app/routes/
 * 2. Add an entry in createAppRouter below
 * 3. Add a corresponding path helper in src/config/paths.ts
 */
// react-router v7 lazy() must return an object with route properties
// (Component, loader, etc.), not a raw module. Unwrap the default export here.
async function lazyRoute(
  loader: () => Promise<{ default: React.ComponentType }>,
) {
  const mod = await loader();
  return { Component: mod.default };
}

function createAppRouter() {
  return createBrowserRouter([
    {
      path: paths.home.path,
      lazy: () => lazyRoute(() => import('./routes/landing')),
    },
    {
      path: paths.auth.login.path,
      lazy: () => lazyRoute(() => import('./routes/authentication/login')),
    },
    {
      path: paths.auth.register.path,
      lazy: () => lazyRoute(() => import('./routes/authentication/register')),
    },
    {
      path: paths.app.root.path,
      lazy: () => lazyRoute(() => import('./routes/app/root')),
      children: [
        {
          index: true,
          lazy: () => lazyRoute(() => import('./routes/app/dashboard')),
        },
        {
          path: paths.app.habits.path,
          lazy: () => lazyRoute(() => import('./routes/app/habits')),
        },
        {
          path: paths.app.habit.path,
          lazy: () => lazyRoute(() => import('./routes/app/habit-detail')),
        },
        {
        path: paths.app.activities.path,//added this code derived from chatGPT
        lazy: () => lazyRoute(() => import('./routes/app/activities')),
        },
        {
        path: paths.app.goals.path,//added for goals
        lazy: () => lazyRoute(()=> import('./routes/app/goals')),
        },
        {
          path: paths.app.profile.path,
          lazy: () => lazyRoute(() => import('./routes/app/profile')),
        },
      ],
    },
    {
      path: '*',
      lazy: () => lazyRoute(() => import('./routes/not-found')),
    },
  ]);
}

export function AppRouter() {
  const router = useMemo(() => createAppRouter(), []);
  return <RouterProvider router={router} />;
}
