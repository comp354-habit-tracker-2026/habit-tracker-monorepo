import * as React from 'react';
/**
 * @ignore - internal component.
 */
export interface MenuListContextValue {
  itemsFocusableWhenDisabled: boolean;
  suppressInitialFocusVisible: boolean;
  variant: 'menu' | 'selectedMenu';
}
export declare const MenuListContext: React.Context<MenuListContextValue | undefined>;
export declare function useMenuListContext(): MenuListContextValue;