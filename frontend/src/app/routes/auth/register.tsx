import * as React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { apiClient } from '@/lib/api-client';
import { paths } from '@/config/paths';

function RegisterRoute() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      await apiClient.post('/auth/register/', {
        username,
        email,
        password,
        password2,
      });
      setSuccess(true);
      setTimeout(() => navigate(paths.auth.login.getHref()), 500);
    } catch (err: any) {
      // Try to extract detailed error messages from backend response
      if (err.response && err.response.data) {
        const data = err.response.data;
        if (typeof data === 'string') {
          setError(data);
        } else if (typeof data === 'object') {
          // Join all error messages into a single string
          const messages = Object.entries(data)
            .map(([field, msgs]) => `${field}: ${(Array.isArray(msgs) ? msgs.join(', ') : msgs)}`)
            .join(' | ');
          setError(messages);
        } else {
          setError('Registration failed.');
        }
      } else {
        setError(err instanceof Error ? err.message : 'Registration failed');
      }
    }
  }

  return (
    <div className="auth-page" style={{ padding: '2rem' }}>
      <h1>Register</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem', maxWidth: '320px' }}>
        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        <label>
          Confirm Password
          <input type="password" value={password2} onChange={(event) => setPassword2(event.target.value)} required />
        </label>
        <button type="submit">Register</button>
      </form>
      {success && <p style={{ color: 'green' }}>Registered successfully. Redirecting to login…</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      <p>
        Already have an account? <a href={paths.auth.login.getHref()}>Login</a>
      </p>
    </div>
  );
}

export default RegisterRoute;
