import * as React from 'react';
export interface Item<Key = unknown> {
  /**
   * The logical id used to track the item across reorders and re-renders.
   * Components such as `Tabs` use the tab value here, while `MenuItem` generates an internal id.
   */
  id: Key;
  /**
   * The item's current DOM element.
   */
  element: HTMLElement | null;
  /**
   * Whether the item ignores user interaction.
   */
  disabled: boolean;
  /**
   * Whether a disabled item should still be allowed to receive roving focus.
   * `MenuList` uses this for its `disabledItemsFocusable` behavior.
   */
  focusableWhenDisabled: boolean;
  /**
   * An optional text string used for typeahead matching.
   */
  textValue?: string | undefined;
  /**
   * Whether the item is currently selected in the consumer component's own state model.
   * `MenuList` uses this when `variant="selectedMenu"` to prefer the selected item by default,
   * and `Tabs` sets this on the selected tab.
   */
  selected: boolean;
}
export interface UseRovingTabIndexParams<Key = unknown> {
  /**
   * The logical item id that should own `tabIndex=0`.
   *
   * Pass a concrete id when the consumer wants to drive roving focus explicitly.
   * For example, `Tabs` uses the selected tab value here when focus is outside the list so
   * that keyboard focus re-enters on the selected tab.
   *
   * `undefined` means "the hook should choose the active item using its default-item logic".
   * `null` means "there is intentionally no preferred item", which also falls back to the
   * default-item logic.
   */
  activeItemId?: Key | null | undefined;
  /**
   * Chooses the default item when `activeItemId` is not driving the tab stop directly.
   *
   * `MenuList` uses this to prefer the selected item when `variant="selectedMenu"`, then
   * falls back to the first focusable item.
   */
  getDefaultActiveItemId?: ((items: Item<Key>[]) => Key | null) | undefined;
  /**
   * The axis used by arrow-key navigation.
   */
  orientation: 'horizontal' | 'vertical';
  /**
   * Whether horizontal keyboard navigation should follow right-to-left semantics.
   * Only affects horizontal lists.
   * @default false
   */
  isRtl?: boolean | undefined;
  /**
   * Filters items out of roving navigation without removing them from the registry.
   * For example, `MenuList` uses this so disabled menu items can stay registered while still
   * being skipped for roving focus unless `disabledItemsFocusable` is enabled.
   */
  isItemFocusable?: ((item: Item<Key>) => boolean) | undefined;
  /**
   * Whether keyboard navigation should wrap from the last item back to the first, and vice versa.
   * @default true
   */
  wrap?: boolean | undefined;
}
export interface UseRovingTabIndexReturnValue<Key = unknown> {
  /**
   * The item id that currently owns `tabIndex=0` for this render.
   */
  activeItemId: Key | null;
  /**
   * Imperatively moves focus to the next matching item.
   * Consumers such as `MenuList` use this for typeahead and other non-arrow-key navigation.
   */
  focusNext: (isItemFocusableOverride?: (item: Item<Key>) => boolean) => Key | null;
  /**
   * Returns the current active item record from a fresh registry snapshot.
   */
  getActiveItem: () => Item<Key> | null;
  /**
   * Returns the props that enable roving behavior on the container element.
   *
   * Spread these props onto the list or composite root element that should listen for focus
   * and keyboard events.
   */
  getContainerProps: (ref?: React.Ref<HTMLElement>) => {
    /**
     * Keeps the active item in sync when focus moves onto one of the registered items.
     */
    onFocus: (event: React.FocusEvent<HTMLElement>) => void;
    /**
     * Handles arrow-key, Home, and End navigation for the roving set.
     */
    onKeyDown: (event: React.KeyboardEvent<HTMLElement>) => void;
    /**
     * Merges the consumer ref with the internal container ref used by the hook.
     */
    ref: (element: HTMLElement | null) => void;
  };
  /**
   * Returns the current item registry.
   * The map is keyed by item id and stores normalized item records.
   */
  getItemMap: () => Map<Key, Item<Key>>;
  /**
   * Reports whether the supplied item id currently owns `tabIndex=0`.
   */
  isItemActive: (itemId: Key) => boolean;
  /**
   * Registers or updates an item in the roving registry.
   */
  registerItem: (item: Item<Key>) => void;
  /**
   * Updates the current active item id.
   */
  setActiveItemId: (itemId: Key | null) => void;
  /**
   * Removes an item from the roving registry.
   */
  unregisterItem: (itemId: Key) => void;
}
export interface UseRovingTabIndexItemParams<Key = unknown> {
  /**
   * The logical id that will be used as the item's registry key.
   */
  id: Key;
  /**
   * The consumer's ref for the item's DOM element.
   * The item hook merges this with its own registration ref callback.
   */
  ref?: React.Ref<HTMLElement> | undefined;
  /**
   * Whether the item ignores user interaction.
   * @default false
   */
  disabled?: boolean | undefined;
  /**
   * Whether the item should still be focusable even when `disabled` is true.
   * @default false
   */
  focusableWhenDisabled?: boolean | undefined;
  /**
   * An optional text string used for typeahead matching.
   */
  textValue?: string | undefined;
  /**
   * Whether the item is selected in the consumer component's state model.
   * @default false
   */
  selected?: boolean | undefined;
}
export interface UseRovingTabIndexItemReturnValue {
  /**
   * The merged ref callback that registers the item element with the root registry.
   */
  ref: React.RefCallback<HTMLElement | null>;
  /**
   * The `tabIndex` that should be applied to the item element.
   * The active item receives `0`; every other item receives `-1`.
   */
  tabIndex: number;
}
/**
 * Provides roving tab index behavior for a composite container and its focusable children.
 * This is useful for implementing keyboard navigation in components like menus, tabs, and lists.
 * The hook manages the focus state of child elements and provides props to be spread on both the container and the items.
 * The container will handle keyboard events to move focus between items based on the specified orientation and wrapping behavior.
 */
export declare function useRovingTabIndexRoot<Key = unknown>(params: UseRovingTabIndexParams<Key>): UseRovingTabIndexReturnValue<Key>;
export declare function useRovingTabIndexItem<Key = unknown>(params: UseRovingTabIndexItemParams<Key>): UseRovingTabIndexItemReturnValue;
export declare function isItemFocusable(item: Item<unknown>): boolean;