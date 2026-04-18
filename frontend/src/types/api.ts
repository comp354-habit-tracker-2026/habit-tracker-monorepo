/**
 * Shared TypeScript types for API responses.
 *
 * These types should match the shapes returned by the backend.
 * Feature-specific types should live inside `src/features/<feature>/types/`.
 */

// ---------------------------------------------------------------------------
// Generic wrapper types
// ---------------------------------------------------------------------------

export type ApiResponse<T> = {
  data: T;
  message?: string;
};

export type PaginatedResponse<T> = {
  data: T[];
  total: number;
  page: number;
  limit: number;
};

// ---------------------------------------------------------------------------
// Shared domain types
// ---------------------------------------------------------------------------

export type User = {
  id: string;
  password: string; //add password var
  email: string;
  firstName: string;
  lastName: string;
  role: 'USER' | 'ADMIN';
  createdAt: string;
};

export type AuthResponse = {
  user: User;
  token: string;
};
