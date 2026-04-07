import * as React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import { apiClient } from '@/lib/api-client';
import { paths } from '@/config/paths';
import { setAuthTokens } from '@/lib/auth';

function LoginRoute() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      const response = (await apiClient.post('/auth/login/', {
        username,
        password,
      })) as { access: string; refresh: string };

      setAuthTokens(response.access, response.refresh);
      navigate(paths.app.root.getHref());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  }

  return (
    <div className="auth-page" style={{ padding: '2rem' }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem', maxWidth: '320px' }}>
        <label>
          Username
          <input
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      <p>
        Don&apos;t have an account? <a href={paths.auth.register.getHref()}>Register</a>
      </p>
    </div>
  );
}

export default LoginRoute;
