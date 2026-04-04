/**
 * 404 – Not Found route.
 * Rendered when no other route matches.
 */
import { Link } from 'react-router';

import { paths } from '@/config/paths';

function NotFoundRoute() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '1rem',
      }}
    >
      <h1>404 – Page not found</h1>
      <p>The page you are looking for does not exist.</p>
      <Link to={paths.home.getHref()}>Go home</Link>
    </div>
  );
}

export default NotFoundRoute;
