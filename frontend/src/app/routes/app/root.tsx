import { Outlet } from 'react-router';

/**
 * Root layout for all authenticated /app/* routes.
 *
 * Add global navigation, sidebar, or auth guards here.
 * Each child route is rendered via <Outlet />.
 */
function AppRoot() {
  return (
    <div className="app-root">
      <nav className="app-root__nav">
        <a href="/app">Dashboard</a>
        {' · '}
        <a href="/app/habits">Habits</a>
        {' · '}
        <a href="/app/profile">Profile</a>
      </nav>
      <main className="app-root__main">
        <Outlet />
      </main>
    </div>
  );
}

export default AppRoot;
