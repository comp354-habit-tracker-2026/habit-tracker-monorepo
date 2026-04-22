import { Login } from '@/features/authentication/components/login';
/**
 * Account Registration Page
 */

function LoginRoute() {
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
      <h1>Sign In</h1>
      <Login />
    </div>
  );
}

// react-router lazy() requires a default export
export default LoginRoute;