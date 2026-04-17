"use strict";
'use client';

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var React = _interopRequireWildcard(require("react"));
var _propTypes = _interopRequireDefault(require("prop-types"));
var _useRovingTabIndex = require("@mui/utils/useRovingTabIndex");
var _ownerDocument = _interopRequireDefault(require("../utils/ownerDocument"));
var _getActiveElement = _interopRequireDefault(require("../utils/getActiveElement"));
var _getScrollbarSize = _interopRequireDefault(require("../utils/getScrollbarSize"));
var _focusWithVisible = _interopRequireDefault(require("../utils/focusWithVisible"));
var _useEventCallback = _interopRequireDefault(require("../utils/useEventCallback"));
var _useForkRef = _interopRequireDefault(require("../utils/useForkRef"));
var _useEnhancedEffect = _interopRequireDefault(require("../utils/useEnhancedEffect"));
var _useRovingTabIndex2 = require("../utils/useRovingTabIndex");
var _ownerWindow = _interopRequireDefault(require("../utils/ownerWindow"));
var _List = _interopRequireDefault(require("../List"));
var _utils = require("../Select/utils");
var _MenuListContext = require("./MenuListContext");
var _jsxRuntime = require("react/jsx-runtime");
function getItemText(itemOrElement) {
  const element = itemOrElement?.element ?? itemOrElement;
  if (!element) {
    return '';
  }
  if (itemOrElement?.textValue !== undefined) {
    return itemOrElement.textValue;
  }
  let text = element.innerText;
  if (text === undefined) {
    // jsdom doesn't support innerText
    text = element.textContent;
  }
  return text ?? '';
}
function textCriteriaMatches(itemOrElement, textCriteria) {
  if (textCriteria === undefined) {
    return true;
  }
  let text = getItemText(itemOrElement);
  text = text.trim().toLowerCase();
  if (text.length === 0) {
    return false;
  }
  if (textCriteria.repeating) {
    return text[0] === textCriteria.keys[0];
  }
  return text.startsWith(textCriteria.keys.join(''));
}
function isItemFocusableWithTextCriteria(item, criteria) {
  if (!textCriteriaMatches(item, criteria)) {
    return false;
  }
  return (0, _useRovingTabIndex.isItemFocusable)(item);
}

// Menu auto-focus is not always keyboard-driven. On open we often move focus to the
// active item programmatically so arrow-key navigation starts from the right place.
function focusInitialItem(element, focusSource) {
  (0, _focusWithVisible.default)(element, focusSource);
}

/**
 * A permanently displayed menu following https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/.
 * It's exposed to help customization of the [`Menu`](/material-ui/api/menu/) component if you
 * use it separately you need to move focus into the component manually. Once
 * the focus is placed inside the component it is fully keyboard accessible.
 */
const MenuList = /*#__PURE__*/React.forwardRef(function MenuList(props, ref) {
  const {
    // private
    // eslint-disable-next-line react/prop-types
    actions,
    autoFocus: autoFocusList = false,
    autoFocusItem: autoFocusActiveItem = false,
    children,
    className,
    disabledItemsFocusable = false,
    disableListWrap = false,
    onKeyDown,
    variant = 'selectedMenu',
    ...other
  } = props;
  const listRef = React.useRef(null);
  const hasFocusedInitialTargetRef = React.useRef(false);
  // Escape hatch for <Menu variant="menu"> (items have no selection state). When opened with
  // mouse/pointer, the initial focused item should still receive DOM focus, but ButtonBase
  // should suppress its focus-visible state for that one initial handoff.
  const [suppressInitialFocusVisible, setSuppressInitialFocusVisible] = React.useState(false);
  // Current anchored <Menu>s cannot receive a `openInteractionType` signal from a trigger
  // the API only receives `open` and `anchorEl`. When <MenuList> is used in <Select>, the
  // internal <SelectInput> is able to achieve this via `useSelectFocusSource`.
  const focusSource = (0, _utils.useSelectFocusSource)();
  const textCriteriaRef = React.useRef({
    keys: [],
    repeating: true,
    previousKeyMatched: true,
    lastTime: null
  });
  const getDefaultActiveItemId = React.useCallback(items => {
    if (variant === 'selectedMenu') {
      return items.find(item => item.selected && (0, _useRovingTabIndex.isItemFocusable)(item))?.id ?? items.find(item => (0, _useRovingTabIndex.isItemFocusable)(item))?.id ?? null;
    }
    return items.find(item => (0, _useRovingTabIndex.isItemFocusable)(item))?.id ?? null;
  }, [variant]);
  const rovingContainer = (0, _useRovingTabIndex2.useRovingTabIndexRoot)({
    activeItemId: undefined,
    getDefaultActiveItemId,
    orientation: 'vertical',
    wrap: !disableListWrap
  });
  const {
    activeItemId,
    focusNext,
    getActiveItem,
    getContainerProps,
    getItemMap
  } = rovingContainer;
  const focusInitialTarget = (0, _useEventCallback.default)((force = false) => {
    // `force` is used by the imperative action when `Menu` asks `MenuList` to restore its
    // initial focus target after the popover finishes entering, even if this list already
    // completed its normal one-time initial-focus path on an earlier render.
    if (!listRef.current || !force && hasFocusedInitialTargetRef.current) {
      return null;
    }
    if (autoFocusActiveItem) {
      const activeItem = getActiveItem();
      if (activeItem?.element) {
        const hasSelectedItem = Array.from(getItemMap().values()).some(item => item.selected);
        const shouldSuppressInitialFocusVisible = variant === 'menu' && hasSelectedItem && !activeItem.selected && focusSource == null;
        setSuppressInitialFocusVisible(shouldSuppressInitialFocusVisible);
        focusInitialItem(activeItem.element, focusSource);
        hasFocusedInitialTargetRef.current = true;
        return activeItem.element;
      }
      if (!autoFocusList) {
        return null;
      }

      // Keep the list container focusable while waiting for items to register,
      // or when there is no focusable item to move to.
      setSuppressInitialFocusVisible(false);
      listRef.current.focus();
      return listRef.current;
    }
    if (!autoFocusList) {
      setSuppressInitialFocusVisible(false);
      return null;
    }
    setSuppressInitialFocusVisible(false);
    listRef.current.focus();
    hasFocusedInitialTargetRef.current = true;
    return listRef.current;
  });
  (0, _useEnhancedEffect.default)(() => {
    if (!autoFocusList && !autoFocusActiveItem) {
      hasFocusedInitialTargetRef.current = false;
      setSuppressInitialFocusVisible(false);
      return undefined;
    }
    focusInitialTarget();
    return undefined;
  }, [activeItemId, autoFocusActiveItem, autoFocusList, focusInitialTarget]);
  React.useImperativeHandle(actions, () => ({
    adjustStyleForScrollbar: (containerElement, {
      direction
    }) => {
      // Let's ignore that piece of logic if users are already overriding the width
      // of the menu.
      const noExplicitWidth = !listRef.current.style.width;
      if (containerElement.clientHeight < listRef.current.clientHeight && noExplicitWidth) {
        const scrollbarSize = `${(0, _getScrollbarSize.default)((0, _ownerWindow.default)(containerElement))}px`;
        listRef.current.style[direction === 'rtl' ? 'paddingLeft' : 'paddingRight'] = scrollbarSize;
        listRef.current.style.width = `calc(100% + ${scrollbarSize})`;
      }
      return listRef.current;
    },
    focusInitialTarget: () => {
      if (!listRef.current) {
        return null;
      }
      const currentFocus = (0, _getActiveElement.default)((0, _ownerDocument.default)(listRef.current));
      if (currentFocus && listRef.current.contains(currentFocus)) {
        return currentFocus;
      }
      return focusInitialTarget(true);
    }
  }), [focusInitialTarget]);
  const rovingContainerProps = getContainerProps();
  const handleRef = (0, _useForkRef.default)(listRef, rovingContainerProps.ref, ref);
  const menuListContextValue = React.useMemo(() => ({
    itemsFocusableWhenDisabled: disabledItemsFocusable,
    suppressInitialFocusVisible,
    variant
  }), [disabledItemsFocusable, suppressInitialFocusVisible, variant]);
  const handleKeyDown = (0, _useEventCallback.default)(event => {
    if (suppressInitialFocusVisible) {
      setSuppressInitialFocusVisible(false);
    }
    const isModifierKeyPressed = event.ctrlKey || event.metaKey || event.altKey;
    if (isModifierKeyPressed && onKeyDown) {
      onKeyDown(event);
      return;
    }
    rovingContainerProps.onKeyDown(event);
    if (event.key.length === 1) {
      const criteria = textCriteriaRef.current;
      const lowerKey = event.key.toLowerCase();
      const currTime = performance.now();
      if (criteria.keys.length > 0) {
        // Reset
        if (currTime - criteria.lastTime > 500) {
          criteria.keys = [];
          criteria.repeating = true;
          criteria.previousKeyMatched = true;
        } else if (criteria.repeating && lowerKey !== criteria.keys[0]) {
          criteria.repeating = false;
        }
      }
      criteria.lastTime = currTime;
      criteria.keys.push(lowerKey);
      const currentFocus = (0, _getActiveElement.default)((0, _ownerDocument.default)(listRef.current));
      const keepFocusOnCurrent = currentFocus && !criteria.repeating && textCriteriaMatches(currentFocus, criteria);
      if (criteria.previousKeyMatched && (keepFocusOnCurrent || focusNext(item => isItemFocusableWithTextCriteria(item, criteria)) != null)) {
        event.preventDefault();
      } else {
        criteria.previousKeyMatched = false;
      }
    }
    if (onKeyDown) {
      onKeyDown(event);
    }
  });
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(_List.default, {
    role: "menu",
    ref: handleRef,
    className: className,
    onKeyDown: handleKeyDown,
    onFocus: rovingContainerProps.onFocus,
    tabIndex: -1,
    ...other,
    children: /*#__PURE__*/(0, _jsxRuntime.jsx)(_MenuListContext.MenuListContext.Provider, {
      value: menuListContextValue,
      children: /*#__PURE__*/(0, _jsxRuntime.jsx)(_useRovingTabIndex2.RovingTabIndexContext.Provider, {
        value: rovingContainer,
        children: children
      })
    })
  });
});
process.env.NODE_ENV !== "production" ? MenuList.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * If `true`, will focus the `[role="menu"]` container and move into tab order.
   * @default false
   */
  autoFocus: _propTypes.default.bool,
  /**
   * If `true`, will focus the first menuitem if `variant="menu"` or selected item
   * if `variant="selectedMenu"`.
   * @default false
   */
  autoFocusItem: _propTypes.default.bool,
  /**
   * MenuList contents, normally `MenuItem`s.
   */
  children: _propTypes.default.node,
  /**
   * @ignore
   */
  className: _propTypes.default.string,
  /**
   * If `true`, will allow focus on disabled items.
   * @default false
   */
  disabledItemsFocusable: _propTypes.default.bool,
  /**
   * If `true`, the menu items will not wrap focus.
   * @default false
   */
  disableListWrap: _propTypes.default.bool,
  /**
   * @ignore
   */
  onKeyDown: _propTypes.default.func,
  /**
   * The variant to use. Use `menu` to prevent selected items from impacting the initial focus
   * and the vertical alignment relative to the anchor element.
   * @default 'selectedMenu'
   */
  variant: _propTypes.default.oneOf(['menu', 'selectedMenu'])
} : void 0;
var _default = exports.default = MenuList;