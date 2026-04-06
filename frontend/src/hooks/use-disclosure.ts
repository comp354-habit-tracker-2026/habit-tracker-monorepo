import { useCallback, useState } from 'react';

/**
 * Manages simple open/closed boolean state (modals, drawers, menus).
 *
 * @example
 * const { isOpen, open, close, toggle } = useDisclosure();
 */
export function useDisclosure(initial = false) {
  const [isOpen, setIsOpen] = useState(initial);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);

  return { isOpen, open, close, toggle };
}
