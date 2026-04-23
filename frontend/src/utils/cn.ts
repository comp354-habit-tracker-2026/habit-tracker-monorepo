/**
 * Combines class names, filtering out falsy values.
 *
 * Usage:
 *   cn('base-class', isActive && 'active', className)
 */
export function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(' ');
}
