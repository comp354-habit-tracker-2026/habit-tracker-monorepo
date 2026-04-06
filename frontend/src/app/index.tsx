import { AppProvider } from './provider';
import { AppRouter } from './router';

/**
 * Root application component.
 *
 * Only two responsibilities:
 *   1. Wrap children with all global providers (AppProvider)
 *   2. Render the router (AppRouter)
 *
 * Keep this file small – business logic belongs in features or routes.
 */
export function App() {
  return (
    <AppProvider>
      <AppRouter />
    </AppProvider>
  );
}
