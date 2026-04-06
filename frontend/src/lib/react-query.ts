import type { DefaultOptions } from '@tanstack/react-query';

/**
 * Global React Query defaults.
 *
 * Centralising these options means every query in the app shares the
 * same retry and staleness behaviour without repeating configuration.
 */
export const queryConfig: DefaultOptions = {
  queries: {
    // Avoid automatic refetching unless explicitly needed
    refetchOnWindowFocus: false,
    // Retry failed requests once before showing an error
    retry: 1,
    // Data is considered fresh for 5 minutes
    staleTime: 1000 * 60 * 5,
  },
};
