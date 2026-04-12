import { Link } from 'react-router';
import { paths } from '@/config/paths';

/**
 * Account Registration Page
 */

function RegisterRoute() {
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
      <h1>Register</h1>
      <p>Please enter a username and password.</p>
      <Link to={paths.app.root.getHref()}>Get started</Link>
      <Link to={paths.home.getHref()}>To Home</Link>
    </div>
  );
}

// react-router lazy() requires a default export
export default RegisterRoute;