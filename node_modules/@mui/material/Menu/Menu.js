"use strict";
'use client';

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = exports.MenuPaper = void 0;
var React = _interopRequireWildcard(require("react"));
var _propTypes = _interopRequireDefault(require("prop-types"));
var _composeClasses = _interopRequireDefault(require("@mui/utils/composeClasses"));
var _HTMLElementType = _interopRequireDefault(require("@mui/utils/HTMLElementType"));
var _RtlProvider = require("@mui/system/RtlProvider");
var _useSlotProps = _interopRequireDefault(require("@mui/utils/useSlotProps"));
var _MenuList = _interopRequireDefault(require("../MenuList"));
var _Popover = _interopRequireWildcard(require("../Popover"));
var _rootShouldForwardProp = _interopRequireDefault(require("../styles/rootShouldForwardProp"));
var _zeroStyled = require("../zero-styled");
var _DefaultPropsProvider = require("../DefaultPropsProvider");
var _menuClasses = require("./menuClasses");
var _useSlot = _interopRequireDefault(require("../utils/useSlot"));
var _jsxRuntime = require("react/jsx-runtime");
const RTL_ORIGIN = {
  vertical: 'top',
  horizontal: 'right'
};
const LTR_ORIGIN = {
  vertical: 'top',
  horizontal: 'left'
};
const useUtilityClasses = ownerState => {
  const {
    classes
  } = ownerState;
  const slots = {
    root: ['root'],
    paper: ['paper'],
    list: ['list']
  };
  return (0, _composeClasses.default)(slots, _menuClasses.getMenuUtilityClass, classes);
};
const MenuRoot = (0, _zeroStyled.styled)(_Popover.default, {
  shouldForwardProp: prop => (0, _rootShouldForwardProp.default)(prop) || prop === 'classes',
  name: 'MuiMenu',
  slot: 'Root'
})({});
const MenuPaper = exports.MenuPaper = (0, _zeroStyled.styled)(_Popover.PopoverPaper, {
  name: 'MuiMenu',
  slot: 'Paper'
})({
  // specZ: The maximum height of a simple menu should be one or more rows less than the view
  // height. This ensures a tappable area outside of the simple menu with which to dismiss
  // the menu.
  maxHeight: 'calc(100% - 96px)',
  // Add iOS momentum scrolling for iOS < 13.0
  WebkitOverflowScrolling: 'touch'
});
const MenuMenuList = (0, _zeroStyled.styled)(_MenuList.default, {
  name: 'MuiMenu',
  slot: 'List'
})({
  // We disable the focus ring for mouse, touch and keyboard users.
  outline: 0
});
const Menu = /*#__PURE__*/React.forwardRef(function Menu(inProps, ref) {
  const props = (0, _DefaultPropsProvider.useDefaultProps)({
    props: inProps,
    name: 'MuiMenu'
  });
  const {
    autoFocus = true,
    children,
    className,
    disableAutoFocusItem = false,
    onClose,
    open,
    PopoverClasses,
    transitionDuration = 'auto',
    variant = 'selectedMenu',
    slots = {},
    slotProps = {},
    ...other
  } = props;
  const isRtl = (0, _RtlProvider.useRtl)();
  const ownerState = {
    ...props,
    autoFocus,
    disableAutoFocusItem,
    transitionDuration,
    variant
  };
  const classes = useUtilityClasses(ownerState);
  const shouldManageInitialFocus = autoFocus && open; // `&& open` prevents a Menu with `keepMounted={true}` from accidentally stealing focus
  const shouldAutoFocusActiveItem = shouldManageInitialFocus && !disableAutoFocusItem;
  const menuListActionsRef = React.useRef(null);
  const handleEntering = (element, _isAppearing) => {
    if (menuListActionsRef.current) {
      menuListActionsRef.current.adjustStyleForScrollbar(element, {
        direction: isRtl ? 'rtl' : 'ltr'
      });
      if (shouldManageInitialFocus) {
        menuListActionsRef.current.focusInitialTarget?.();
      }
    }
  };
  const handleListKeyDown = event => {
    if (event.key === 'Tab') {
      event.preventDefault();
      if (onClose) {
        onClose(event, 'tabKeyDown');
      }
    }
  };
  const externalForwardedProps = {
    slots,
    slotProps
  };
  const rootSlotProps = (0, _useSlotProps.default)({
    elementType: slots.root,
    externalSlotProps: slotProps.root,
    ownerState,
    className: [classes.root, className]
  });
  const [PaperSlot, paperSlotProps] = (0, _useSlot.default)('paper', {
    className: classes.paper,
    elementType: MenuPaper,
    externalForwardedProps,
    shouldForwardComponentProp: true,
    ownerState
  });
  const [ListSlot, listSlotProps] = (0, _useSlot.default)('list', {
    className: classes.list,
    elementType: MenuMenuList,
    shouldForwardComponentProp: true,
    externalForwardedProps,
    getSlotProps: handlers => ({
      ...handlers,
      onKeyDown: event => {
        handleListKeyDown(event);
        handlers.onKeyDown?.(event);
      }
    }),
    ownerState
  });
  const resolvedTransitionProps = typeof slotProps.transition === 'function' ? slotProps.transition(ownerState) : slotProps.transition;
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(MenuRoot
  // `disableAutoFocus={autoFocus}` is NOT a mistake
  //   - `autoFocus` means `Menu` will control focus and move it into `MenuList` or an active `MenuItem`
  //   - `disableAutoFocus` means disable `MenuRoot`s underlying `Popover`'s autoFocus handling
  // This prevents `MenuList` and `Popover` from fighting each other to control focus.
  // (This has nothing to do with DOM `autoFocus`)
  , {
    disableAutoFocus: autoFocus,
    onClose: onClose,
    anchorOrigin: {
      vertical: 'bottom',
      horizontal: isRtl ? 'right' : 'left'
    },
    transformOrigin: isRtl ? RTL_ORIGIN : LTR_ORIGIN,
    slots: {
      root: slots.root,
      paper: PaperSlot,
      backdrop: slots.backdrop,
      transition: slots.transition
    },
    slotProps: {
      root: rootSlotProps,
      paper: paperSlotProps,
      backdrop: typeof slotProps.backdrop === 'function' ? slotProps.backdrop(ownerState) : slotProps.backdrop,
      transition: {
        ...resolvedTransitionProps,
        onEntering: (...args) => {
          handleEntering(...args);
          resolvedTransitionProps?.onEntering?.(...args);
        }
      }
    },
    open: open,
    ref: ref,
    transitionDuration: transitionDuration,
    ownerState: ownerState,
    ...other,
    classes: PopoverClasses,
    children: /*#__PURE__*/(0, _jsxRuntime.jsx)(ListSlot, {
      actions: menuListActionsRef,
      autoFocus: shouldManageInitialFocus,
      autoFocusItem: shouldAutoFocusActiveItem,
      variant: variant,
      ...listSlotProps,
      children: children
    })
  });
});
process.env.NODE_ENV !== "production" ? Menu.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * An HTML element, or a function that returns one.
   * It's used to set the position of the menu.
   */
  anchorEl: _propTypes.default /* @typescript-to-proptypes-ignore */.oneOfType([_HTMLElementType.default, _propTypes.default.func]),
  /**
   * If `true` (Default) will focus the `[role="menu"]` if no focusable child is found. Disabled
   * children are not focusable. If you set this prop to `false` focus will be placed
   * on the parent modal container. This has severe accessibility implications
   * and should only be considered if you manage focus otherwise.
   * @default true
   */
  autoFocus: _propTypes.default.bool,
  /**
   * Menu contents, normally `MenuItem`s.
   */
  children: _propTypes.default.node,
  /**
   * Override or extend the styles applied to the component.
   */
  classes: _propTypes.default.object,
  /**
   * @ignore
   */
  className: _propTypes.default.string,
  /**
   * When opening the menu will not focus the active item but the `[role="menu"]`
   * unless `autoFocus` is also set to `false`. Not using the default means not
   * following WAI-ARIA authoring practices. Please be considerate about possible
   * accessibility implications.
   * @default false
   */
  disableAutoFocusItem: _propTypes.default.bool,
  /**
   * Callback fired when the component requests to be closed.
   *
   * @param {object} event The event source of the callback.
   * @param {string} reason Can be: `"escapeKeyDown"`, `"backdropClick"`, `"tabKeyDown"`.
   */
  onClose: _propTypes.default.func,
  /**
   * If `true`, the component is shown.
   */
  open: _propTypes.default.bool.isRequired,
  /**
   * `classes` prop applied to the [`Popover`](https://mui.com/material-ui/api/popover/) element.
   */
  PopoverClasses: _propTypes.default.object,
  /**
   * The props used for each slot inside.
   * @default {}
   */
  slotProps: _propTypes.default.shape({
    backdrop: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
    list: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
    paper: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
    root: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
    transition: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object])
  }),
  /**
   * The components used for each slot inside.
   * @default {}
   */
  slots: _propTypes.default.shape({
    backdrop: _propTypes.default.elementType,
    list: _propTypes.default.elementType,
    paper: _propTypes.default.elementType,
    root: _propTypes.default.elementType,
    transition: _propTypes.default.elementType
  }),
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: _propTypes.default.oneOfType([_propTypes.default.arrayOf(_propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object, _propTypes.default.bool])), _propTypes.default.func, _propTypes.default.object]),
  /**
   * The length of the transition in `ms`, or 'auto'
   * @default 'auto'
   */
  transitionDuration: _propTypes.default.oneOfType([_propTypes.default.oneOf(['auto']), _propTypes.default.number, _propTypes.default.shape({
    appear: _propTypes.default.number,
    enter: _propTypes.default.number,
    exit: _propTypes.default.number
  })]),
  /**
   * The variant to use. Use `menu` to prevent selected items from impacting the initial focus.
   * @default 'selectedMenu'
   */
  variant: _propTypes.default.oneOf(['menu', 'selectedMenu'])
} : void 0;
var _default = exports.default = Menu;