/**
 * Top-level error fallback rendered when the root ErrorBoundary catches
 * an unhandled error. Keep this component dependency-free so it can
 * render even if shared providers are broken.
 */
import type { FallbackProps } from 'react-error-boundary';

export function MainErrorFallback({ error }: FallbackProps) {
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '1rem',
        padding: '2rem',
        textAlign: 'center',
      }}
    >
      <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>
        Something went wrong
      </h2>
      <p style={{ color: '#666', maxWidth: '32rem' }}>{message}</p>
      <button
        onClick={() => window.location.assign(window.location.origin)}
        style={{
          padding: '0.5rem 1.5rem',
          borderRadius: '0.375rem',
          background: '#2563eb',
          color: '#fff',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        Refresh
      </button>
    </div>
  );
}
