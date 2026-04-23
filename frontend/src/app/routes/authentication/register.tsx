import { Registration } from '@/features/authentication/components/registration';
/**
 * Account Registration Page
 */

{/*  */}

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
      
      <Registration />
    </div>
  );
}

// react-router lazy() requires a default export
export default RegisterRoute;