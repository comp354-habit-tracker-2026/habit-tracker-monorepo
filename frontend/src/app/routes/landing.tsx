import { Link } from 'react-router';

import { paths } from '@/config/paths';

/**
 * Public landing page – visible to everyone, no auth required.
 */
function LandingRoute() {
  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <h1>Habit Tracker</h1>
      <p>Build better habits, one day at a time.</p>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <Link to={paths.app.root.getHref()}>Get started</Link>
        <Link to={paths.auth.login.getHref()}>Login</Link>
        <Link to={paths.auth.register.getHref()}>Register</Link>
      </div>
    </div>
  );
}

// react-router lazy() requires a default export
export default LandingRoute;
