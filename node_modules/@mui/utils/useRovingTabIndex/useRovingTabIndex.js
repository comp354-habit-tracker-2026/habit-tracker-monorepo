"use strict";
'use client';

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.isItemFocusable = isItemFocusable;
exports.useRovingTabIndexItem = useRovingTabIndexItem;
exports.useRovingTabIndexRoot = useRovingTabIndexRoot;
var React = _interopRequireWildcard(require("react"));
var _fastObjectShallowCompare = _interopRequireDefault(require("../fastObjectShallowCompare"));
var _getActiveElement = _interopRequireDefault(require("../getActiveElement"));
var _ownerDocument = _interopRequireDefault(require("../ownerDocument"));
var _setRef = _interopRequireDefault(require("../setRef"));
var _useEnhancedEffect = _interopRequireDefault(require("../useEnhancedEffect"));
var _useEventCallback = _interopRequireDefault(require("../useEventCallback"));
var _useForkRef = _interopRequireDefault(require("../useForkRef"));
var _RovingTabIndexContext = require("./RovingTabIndexContext");
const SUPPORTED_KEYS = ['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'Home', 'End'];

/**
 * Provides roving tab index behavior for a composite container and its focusable children.
 * This is useful for implementing keyboard navigation in components like menus, tabs, and lists.
 * The hook manages the focus state of child elements and provides props to be spread on both the container and the items.
 * The container will handle keyboard events to move focus between items based on the specified orientation and wrapping behavior.
 */
function useRovingTabIndexRoot(params) {
  const {
    activeItemId: activeItemIdProp,
    getDefaultActiveItemId,
    orientation,
    isRtl = false,
    isItemFocusable: itemFilter = isItemFocusable,
    wrap = true
  } = params;
  const [activeItemIdState, setActiveItemIdState] = React.useState(activeItemIdProp);
  const previousActiveItemIdPropRef = React.useRef(activeItemIdProp);
  let activeItemIdCandidate = activeItemIdState;
  if (activeItemIdProp !== previousActiveItemIdPropRef.current) {
    previousActiveItemIdPropRef.current = activeItemIdProp;
    if (activeItemIdProp !== undefined && activeItemIdProp !== activeItemIdState) {
      activeItemIdCandidate = activeItemIdProp;
      setActiveItemIdState(activeItemIdProp);
    }
  }
  const containerRef = React.useRef(null);

  // based on https://github.com/mui/base-ui/blob/7392a928fca91fcc68b9fad3439ac61e10f3f7ba/packages/react/src/composite/list/CompositeList.tsx#L25-L35
  const itemMapRef = React.useRef(new Map());
  const [mapTick, setMapTick] = React.useState(0);
  const orderedItems = React.useMemo(() => {
    void mapTick;
    return getOrderedItems(itemMapRef.current);
  }, [mapTick]);
  const resolvedActiveItemId = resolveActiveItemId(activeItemIdCandidate, orderedItems, itemFilter, getDefaultActiveItemId);
  const activeItemIdRef = React.useRef(resolvedActiveItemId);
  activeItemIdRef.current = resolvedActiveItemId;
  const getActiveItem = React.useCallback(() => {
    const snapshot = getOrderedItems(itemMapRef.current);
    const resolvedItemId = resolveActiveItemId(activeItemIdRef.current, snapshot, itemFilter, getDefaultActiveItemId);
    return getItemById(snapshot, resolvedItemId);
  }, [getDefaultActiveItemId, itemFilter]);
  const getItemMap = React.useCallback(() => {
    return itemMapRef.current;
  }, []);
  const registerItem = (0, _useEventCallback.default)(item => {
    const previousItem = itemMapRef.current.get(item.id);
    if ((0, _fastObjectShallowCompare.default)(previousItem ?? null, item)) {
      return;
    }
    itemMapRef.current.set(item.id, item);
    setMapTick(value => value + 1);
  });
  const unregisterItem = (0, _useEventCallback.default)(itemId => {
    if (itemMapRef.current.delete(itemId)) {
      setMapTick(value => value + 1);
    }
  });
  const setActiveItemId = (0, _useEventCallback.default)(itemId => {
    setActiveItemIdState(itemId);
  });
  const isItemActive = React.useCallback(itemId => {
    return activeItemIdRef.current === itemId;
  }, []);

  // Moves focus relative to a starting index. This is the directional helper used by
  // keyboard navigation and `focusNext()`.
  const focusItem = React.useCallback((currentIndex, direction, wrap, isItemFocusableOverride) => {
    const snapshot = getNavigableItemsSnapshot(itemMapRef.current);
    const nextItem = getNextActiveItem(snapshot, currentIndex, direction, wrap, isItemFocusableOverride ?? itemFilter);
    if (!nextItem) {
      return null;
    }
    nextItem.element?.focus();
    setActiveItemIdState(nextItem.id);
    return nextItem;
  }, [itemFilter]);
  const getContainerProps = React.useCallback(ref => {
    const onFocus = event => {
      const snapshot = getNavigableItemsSnapshot(itemMapRef.current);
      const focusedIndex = findItemIndexByElement(snapshot, event.target);
      if (focusedIndex !== -1) {
        setActiveItemIdState(snapshot[focusedIndex].id);
      }
    };
    const onKeyDown = event => {
      if (event.altKey || event.shiftKey || event.ctrlKey || event.metaKey) {
        return;
      }
      if (!SUPPORTED_KEYS.includes(event.key)) {
        return;
      }
      let previousItemKey = orientation === 'horizontal' ? 'ArrowLeft' : 'ArrowUp';
      let nextItemKey = orientation === 'horizontal' ? 'ArrowRight' : 'ArrowDown';
      if (orientation === 'horizontal' && isRtl) {
        previousItemKey = 'ArrowRight';
        nextItemKey = 'ArrowLeft';
      }
      const snapshot = getNavigableItemsSnapshot(itemMapRef.current);
      const currentFocus = (0, _getActiveElement.default)((0, _ownerDocument.default)(containerRef.current));
      const isFocusOnContainer = currentFocus === containerRef.current;
      let currentIndex = getCurrentActiveItemIndex(snapshot, currentFocus, activeItemIdRef.current);
      let direction = 'next';
      switch (event.key) {
        case previousItemKey:
          direction = 'previous';
          event.preventDefault();
          if (isFocusOnContainer) {
            // Set to length, so that the previous focused element will be the last one.
            currentIndex = snapshot.length;
          }
          break;
        case nextItemKey:
          event.preventDefault();
          if (isFocusOnContainer) {
            currentIndex = -1;
          }
          break;
        case 'Home':
          event.preventDefault();
          currentIndex = -1;
          break;
        case 'End':
          event.preventDefault();
          direction = 'previous';
          currentIndex = snapshot.length;
          break;
        default:
          return;
      }
      focusItem(currentIndex, direction, wrap);
    };
    return {
      onFocus,
      onKeyDown,
      ref: handleRefs(ref, elementNode => {
        containerRef.current = elementNode;
      })
    };
  }, [focusItem, isRtl, orientation, wrap]);
  const focusNext = React.useCallback(isItemFocusableOverride => {
    const snapshot = getNavigableItemsSnapshot(itemMapRef.current);
    const currentFocus = (0, _getActiveElement.default)((0, _ownerDocument.default)(containerRef.current));
    const isFocusOnContainer = currentFocus === containerRef.current;
    const currentIndex = isFocusOnContainer ? -1 : getCurrentActiveItemIndex(snapshot, currentFocus, activeItemIdRef.current);
    return focusItem(currentIndex, 'next', true, isItemFocusableOverride)?.id ?? null;
  }, [focusItem]);
  return React.useMemo(() => ({
    activeItemId: resolvedActiveItemId,
    focusNext,
    getActiveItem,
    getContainerProps,
    getItemMap,
    isItemActive,
    registerItem,
    setActiveItemId,
    unregisterItem
  }), [resolvedActiveItemId, focusNext, getActiveItem, getContainerProps, getItemMap, isItemActive, registerItem, setActiveItemId, unregisterItem]);
}
function useRovingTabIndexItem(params) {
  const rootContext = (0, _RovingTabIndexContext.useRovingTabIndexContext)();
  const {
    activeItemId,
    registerItem,
    unregisterItem
  } = rootContext;
  const elementRef = React.useRef(null);
  const item = React.useMemo(() => ({
    disabled: params.disabled ?? false,
    element: null,
    focusableWhenDisabled: params.focusableWhenDisabled ?? false,
    id: params.id,
    selected: params.selected ?? false,
    textValue: params.textValue
  }), [params.disabled, params.focusableWhenDisabled, params.id, params.selected, params.textValue]);
  const latestItemRef = React.useRef(item);
  // Keep the ref callback stable across item prop changes. The callback reads the latest
  // item metadata from this ref so React does not have to detach and re-attach the ref
  // every time `disabled`, `selected`, or similar item state changes.
  latestItemRef.current = item;
  const handleElementRef = React.useCallback(element => {
    elementRef.current = element;
    if (element == null) {
      // Ref detachment runs during React's commit phase. Calling `unregisterItem()`
      // synchronously here can trigger a nested state update while React is still
      // finishing that commit. Unregister in a microtask so it runs after the
      // commit completes.
      queueMicrotask(() => {
        // null check prevents stale unregisters for a remove-then-re-add edge case
        if (elementRef.current == null) {
          unregisterItem(params.id);
        }
      });
      return;
    }
    registerItem({
      ...latestItemRef.current,
      element
    });
  }, [params.id, registerItem, unregisterItem]);

  // `UseRovingTabIndexItemReturnValue.ref` must always be a callback ref. `useForkRef()`
  // is typed to return `null` when every input ref is nullish, but this call always includes
  // `handleElementRef`, so the merged ref cannot be `null` here.
  const mergedRef = (0, _useForkRef.default)(params.ref, handleElementRef);
  (0, _useEnhancedEffect.default)(() => {
    if (!elementRef.current) {
      return;
    }
    registerItem({
      ...item,
      element: elementRef.current
    });
  }, [item, registerItem]);
  (0, _useEnhancedEffect.default)(() => {
    const itemId = params.id;

    // Keep unmount cleanup separate from the effect above. The effect above re-runs when
    // item metadata changes, but we only want to unregister on unmount or when the item id changes.
    return () => {
      unregisterItem(itemId);
    };
  }, [params.id, unregisterItem]);
  return {
    ref: mergedRef,
    tabIndex: activeItemId === params.id ? 0 : -1
  };
}

/**
 * Resolves which item id should own the roving tab stop for the current render.
 *
 * This is the top-level decision point for "who gets `tabIndex=0` right now?".
 * For example:
 * - `Tabs` sometimes passes `selectedValue` as `activeItemId` so the selected tab becomes
 *   the tab stop when focus enters the list from outside.
 * - `MenuList` leaves `activeItemId` undefined and relies on the default-item logic below
 *   so that menu-specific rules decide which menu item should initially own the tab stop.
 *
 * @param activeItemId The item id supplied through the root hook's `activeItemId` option.
 *   `undefined` means "the caller did not ask for a specific item, use the default-item
 *   logic instead". `null` means "there is intentionally no preferred item, so also fall
 *   back to the default-item logic".
 * @param items The ordered registered items currently in the roving set.
 * @param isFocusable A predicate that decides whether an item may receive roving focus.
 * @param getDefaultActiveItemId Optional caller-provided function that picks the preferred
 *   default item when `activeItemId` is not driving the tab stop directly.
 * @returns The id of the item that should own `tabIndex=0`, or `null` if no item is focusable.
 */
function resolveActiveItemId(activeItemId, items, isFocusable, getDefaultActiveItemId) {
  if (activeItemId != null) {
    return resolveRequestedItemId(activeItemId, items, isFocusable);
  }
  return resolveDefaultItemId(items, isFocusable, getDefaultActiveItemId);
}

/**
 * Resolves the item id supplied through the root hook's `activeItemId` option.
 *
 * This path is used when a component such as `Tabs` or `MenuList` wants roving focus to
 * follow a specific logical item. For example, `Tabs` can pass the selected tab's value as
 * `activeItemId` so that the selected tab owns `tabIndex=0` when focus enters the list.
 *
 * @param requestedItemId The item id passed to the root hook's `activeItemId` option.
 * @param items The ordered registered items currently in the roving set.
 * @param isFocusable A predicate that decides whether an item may receive roving focus.
 * @returns The same id when it still points to a focusable item. If that id no longer exists,
 *   returns the first focusable item. If the id still exists but the item is not focusable,
 *   returns the next focusable item after it without wrapping.
 */
function resolveRequestedItemId(requestedItemId, items, isFocusable) {
  const requestedItemIndex = findItemIndexById(items, requestedItemId);
  if (requestedItemIndex === -1) {
    return getFirstFocusableItemId(items, isFocusable);
  }
  if (isFocusable(items[requestedItemIndex])) {
    return items[requestedItemIndex].id;
  }
  return getNextActiveItem(items, requestedItemIndex, 'next', false, isFocusable)?.id ?? null;
}

/**
 * Resolves the default active item when the caller is not driving roving focus with
 * `activeItemId`.
 *
 * This path is used on the initial render and whenever the caller leaves the choice of tab
 * stop to the hook. `getDefaultActiveItemId` lets a component prefer a specific logical item
 * before falling back to the first focusable item.
 *
 * For example:
 * - `MenuList` uses this path all the time. When `variant="selectedMenu"`, it prefers the
 *   selected menu item; otherwise it prefers the first focusable menu item.
 * - `Tabs` uses this path while focus is already inside the tab list, because at that point
 *   the current roving position should be driven by actual focus movement rather than by the
 *   selected tab value.
 *
 * @param items The ordered registered items currently in the roving set.
 * @param isFocusable A predicate that decides whether an item may receive roving focus.
 * @param getDefaultActiveItemId Optional caller-provided function that chooses which item
 *   should own the tab stop before the generic "first focusable item" fallback runs.
 * @returns The default item id when it points to a focusable item, otherwise the first
 *   focusable item in the snapshot, or `null` when none are focusable.
 */
function resolveDefaultItemId(items, isFocusable, getDefaultActiveItemId) {
  const defaultItemId = getDefaultActiveItemId?.(items);
  if (defaultItemId != null) {
    const defaultItem = getItemById(items, defaultItemId);
    if (defaultItem && isFocusable(defaultItem)) {
      return defaultItem.id;
    }
  }
  return getFirstFocusableItemId(items, isFocusable);
}

/**
 * Finds the best starting index for keyboard navigation.
 *
 * This is used immediately before keyboard navigation and `focusNext()` navigation. It prefers
 * the item that currently holds DOM focus, but if focus is on the container or outside the item
 * set it falls back to the last known active item id.
 *
 * @param items The navigable item snapshot used for the current keyboard interaction.
 * @param currentFocus The element that currently has DOM focus, if any.
 * @param fallbackActiveItemId The last known active item id when focus is not on an item.
 * @returns The focused item's index when focus is currently on an item. Otherwise, the index
 *   of the fallback active item id, or `-1` when no matching item exists.
 */
function getCurrentActiveItemIndex(items, currentFocus, fallbackActiveItemId) {
  if (currentFocus) {
    const focusedIndex = findItemIndexByElement(items, currentFocus);
    if (focusedIndex !== -1) {
      return focusedIndex;
    }
  }
  return findItemIndexById(items, fallbackActiveItemId);
}

/**
 * Walks the item snapshot to find the next focusable item in the requested direction.
 *
 * This is the shared navigation primitive used by keyboard handling and imperative helpers
 * such as `focusNext()`. It starts from the supplied index, advances through the snapshot in
 * the requested direction, and skips over items that fail the `isFocusable` predicate.
 *
 * @param items The ordered navigable item snapshot.
 * @param currentIndex The index to start from. Use `-1` to start before the first item or
 *   `items.length` to start after the last item.
 * @param direction The direction to move through the snapshot.
 * @param wrap Whether navigation should wrap around at the ends of the list.
 * @param isFocusable A predicate that decides whether an item may receive roving focus.
 * @returns The next focusable item record, or `null` when no focusable item can be reached.
 */
function getNextActiveItem(items, currentIndex, direction, wrap, isFocusable) {
  const lastIndex = items.length - 1;
  if (lastIndex === -1) {
    return null;
  }
  let wrappedOnce = false;
  let nextIndex = getNextIndex(currentIndex, lastIndex, direction, wrap);
  const startIndex = nextIndex;
  while (nextIndex !== -1) {
    if (nextIndex === startIndex) {
      if (wrappedOnce) {
        return null;
      }
      wrappedOnce = true;
    }
    const nextItem = items[nextIndex];
    if (!nextItem || !isFocusable(nextItem)) {
      nextIndex = getNextIndex(nextIndex, lastIndex, direction, wrap);
    } else {
      return nextItem;
    }
  }
  return null;
}
function getFirstFocusableItemId(items, isFocusable) {
  return items.find(item => isFocusable(item))?.id ?? null;
}
function getItemById(items, itemId) {
  return itemId == null ? null : items.find(item => item.id === itemId) ?? null;
}
function findItemIndexById(items, itemId) {
  return itemId == null ? -1 : items.findIndex(item => item.id === itemId);
}
function findItemIndexByElement(items, element) {
  if (!element) {
    return -1;
  }
  return items.findIndex(item => item.element === element || item.element?.contains(element));
}
function getOrderedItems(itemMap) {
  const items = Array.from(itemMap.values());
  if (items.every(item => item.element == null)) {
    return items;
  }
  const connectedItems = items.filter(isConnectedItem).sort((itemA, itemB) => sortByDocumentPosition(itemA.element, itemB.element));
  const disconnectedItems = items.filter(item => !isConnectedItem(item));
  return [...connectedItems, ...disconnectedItems];
}
function getNavigableItemsSnapshot(itemMap) {
  return getOrderedItems(itemMap).filter(isConnectedItem);
}
function getNextIndex(currentIndex, lastIndex, direction, wrap = true) {
  if (direction === 'next') {
    if (currentIndex === lastIndex) {
      return wrap ? 0 : -1;
    }
    return currentIndex + 1;
  }
  if (currentIndex === 0) {
    return wrap ? lastIndex : -1;
  }
  return currentIndex - 1;
}
function isItemFocusable(item) {
  if (!item.element) {
    return false;
  }
  if (item.focusableWhenDisabled) {
    return true;
  }
  return !item.disabled && !item.element.hasAttribute('disabled') && item.element.getAttribute('aria-disabled') !== 'true' && item.element.hasAttribute('tabindex');
}
function isConnectedItem(item) {
  return item.element != null && item.element.isConnected;
}

/* eslint-disable no-bitwise */
function sortByDocumentPosition(a, b) {
  if (a === b) {
    return 0;
  }
  const position = a.compareDocumentPosition(b);
  if (position & Node.DOCUMENT_POSITION_FOLLOWING || position & Node.DOCUMENT_POSITION_CONTAINED_BY) {
    return -1;
  }
  if (position & Node.DOCUMENT_POSITION_PRECEDING || position & Node.DOCUMENT_POSITION_CONTAINS) {
    return 1;
  }
  return 0;
}
/* eslint-enable no-bitwise */

function handleRefs(...refs) {
  return node => {
    refs.forEach(ref => {
      (0, _setRef.default)(ref ?? null, node);
    });
  };
}