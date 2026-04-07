import { Link, Outlet } from 'react-router';

import { paths } from '@/config/paths';

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
        <Link to={paths.app.dashboard.getHref()}>Dashboard</Link>
        {' · '}
        <Link to={paths.app.habits.getHref()}>Habits</Link>
        {' · '}
        <Link to={paths.app.activities.getHref()}>Activities</Link> 
        {' · '}
        <Link to={paths.app.profile.getHref()}>Profile</Link>
      </nav>
      <main className="app-root__main">
        <Outlet />
      </main>
    </div>
  );
}
//added Activities link - code developed from chatGPT
export default AppRoot;

//TODO: Add auth guard once frontend auth context/service is implemented
// All /app/* routes are intended to be protected