"use strict";
'use client';

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.overridesResolver = exports.default = exports.ListItemRoot = void 0;
var React = _interopRequireWildcard(require("react"));
var _propTypes = _interopRequireDefault(require("prop-types"));
var _clsx = _interopRequireDefault(require("clsx"));
var _composeClasses = _interopRequireDefault(require("@mui/utils/composeClasses"));
var _zeroStyled = require("../zero-styled");
var _memoTheme = _interopRequireDefault(require("../utils/memoTheme"));
var _DefaultPropsProvider = require("../DefaultPropsProvider");
var _useSlot = _interopRequireDefault(require("../utils/useSlot"));
var _ListContext = _interopRequireDefault(require("../List/ListContext"));
var _listItemClasses = require("./listItemClasses");
var _ListItemButton = require("../ListItemButton");
var _ListItemSecondaryAction = _interopRequireDefault(require("../ListItemSecondaryAction"));
var _jsxRuntime = require("react/jsx-runtime");
const overridesResolver = (props, styles) => {
  const {
    ownerState
  } = props;
  return [styles.root, ownerState.dense && styles.dense, ownerState.alignItems === 'flex-start' && styles.alignItemsFlexStart, ownerState.divider && styles.divider, !ownerState.disableGutters && styles.gutters, !ownerState.disablePadding && styles.padding];
};
exports.overridesResolver = overridesResolver;
const useUtilityClasses = ownerState => {
  const {
    alignItems,
    classes,
    dense,
    disableGutters,
    disablePadding,
    divider
  } = ownerState;
  const slots = {
    root: ['root', dense && 'dense', !disableGutters && 'gutters', !disablePadding && 'padding', divider && 'divider', alignItems === 'flex-start' && 'alignItemsFlexStart'],
    secondaryAction: ['secondaryAction']
  };
  return (0, _composeClasses.default)(slots, _listItemClasses.getListItemUtilityClass, classes);
};
const ListItemRoot = exports.ListItemRoot = (0, _zeroStyled.styled)('div', {
  name: 'MuiListItem',
  slot: 'Root',
  overridesResolver
})((0, _memoTheme.default)(({
  theme
}) => ({
  display: 'flex',
  justifyContent: 'flex-start',
  alignItems: 'center',
  position: 'relative',
  textDecoration: 'none',
  width: '100%',
  boxSizing: 'border-box',
  textAlign: 'left',
  variants: [{
    props: ({
      ownerState
    }) => !ownerState.disablePadding,
    style: {
      paddingTop: 8,
      paddingBottom: 8
    }
  }, {
    props: ({
      ownerState
    }) => !ownerState.disablePadding && ownerState.dense,
    style: {
      paddingTop: 4,
      paddingBottom: 4
    }
  }, {
    props: ({
      ownerState
    }) => !ownerState.disablePadding && !ownerState.disableGutters,
    style: {
      paddingLeft: 16,
      paddingRight: 16
    }
  }, {
    props: ({
      ownerState
    }) => !ownerState.disablePadding && !!ownerState.secondaryAction,
    style: {
      // Add some space to avoid collision as `ListItemSecondaryAction`
      // is absolutely positioned.
      paddingRight: 48
    }
  }, {
    props: ({
      ownerState
    }) => !!ownerState.secondaryAction,
    style: {
      [`& > .${_ListItemButton.listItemButtonClasses.root}`]: {
        paddingRight: 48
      }
    }
  }, {
    props: {
      alignItems: 'flex-start'
    },
    style: {
      alignItems: 'flex-start'
    }
  }, {
    props: ({
      ownerState
    }) => ownerState.divider,
    style: {
      borderBottom: `1px solid ${(theme.vars || theme).palette.divider}`,
      backgroundClip: 'padding-box'
    }
  }, {
    props: ({
      ownerState
    }) => ownerState.button,
    style: {
      transition: theme.transitions.create('background-color', {
        duration: theme.transitions.duration.shortest
      }),
      '&:hover': {
        textDecoration: 'none',
        backgroundColor: (theme.vars || theme).palette.action.hover,
        // Reset on touch devices, it doesn't add specificity
        '@media (hover: none)': {
          backgroundColor: 'transparent'
        }
      }
    }
  }]
})));
const StyledListItemSecondaryAction = (0, _zeroStyled.styled)(_ListItemSecondaryAction.default, {
  name: 'MuiListItem',
  slot: 'secondaryAction'
})({});
const ListItem = /*#__PURE__*/React.forwardRef(function ListItem(inProps, ref) {
  const props = (0, _DefaultPropsProvider.useDefaultProps)({
    props: inProps,
    name: 'MuiListItem'
  });
  const {
    alignItems = 'center',
    children: childrenProp,
    className,
    component: componentProp = 'li',
    dense = false,
    disableGutters = false,
    disablePadding = false,
    divider = false,
    secondaryAction,
    slotProps = {},
    slots = {},
    ...other
  } = props;
  const context = React.useContext(_ListContext.default);
  const childContext = React.useMemo(() => ({
    dense: dense || context.dense || false,
    alignItems,
    disableGutters
  }), [alignItems, context.dense, dense, disableGutters]);
  const ownerState = {
    ...props,
    alignItems,
    dense: childContext.dense,
    disableGutters,
    disablePadding,
    divider,
    secondaryAction
  };
  const classes = useUtilityClasses(ownerState);
  const externalForwardedProps = {
    slots,
    slotProps
  };
  const [RootSlot, rootSlotProps] = (0, _useSlot.default)('root', {
    ref,
    elementType: ListItemRoot,
    externalForwardedProps: {
      component: componentProp,
      ...externalForwardedProps,
      ...other
    },
    ownerState,
    className: (0, _clsx.default)(classes.root, className)
  });
  const [SecondaryActionSlot, secondaryActionSlotProps] = (0, _useSlot.default)('secondaryAction', {
    elementType: StyledListItemSecondaryAction,
    shouldForwardComponentProp: true,
    externalForwardedProps,
    ownerState,
    className: classes.secondaryAction
  });
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(_ListContext.default.Provider, {
    value: childContext,
    children: /*#__PURE__*/(0, _jsxRuntime.jsxs)(RootSlot, {
      ...rootSlotProps,
      children: [childrenProp, secondaryAction && /*#__PURE__*/(0, _jsxRuntime.jsx)(SecondaryActionSlot, {
        ...secondaryActionSlotProps,
        children: secondaryAction
      })]
    })
  });
});
process.env.NODE_ENV !== "production" ? ListItem.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * Defines the `align-items` style property.
   * @default 'center'
   */
  alignItems: _propTypes.default.oneOf(['center', 'flex-start']),
  /**
   * The content of the component.
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
   * The component used for the root node.
   * Either a string to use a HTML element or a component.
   */
  component: _propTypes.default.elementType,
  /**
   * If `true`, compact vertical padding designed for keyboard and mouse input is used.
   * The prop defaults to the value inherited from the parent List component.
   * @default false
   */
  dense: _propTypes.default.bool,
  /**
   * If `true`, the left and right padding is removed.
   * @default false
   */
  disableGutters: _propTypes.default.bool,
  /**
   * If `true`, all padding is removed.
   * @default false
   */
  disablePadding: _propTypes.default.bool,
  /**
   * If `true`, a 1px light border is added to the bottom of the list item.
   * @default false
   */
  divider: _propTypes.default.bool,
  /**
   * The element to display at the end of ListItem.
   */
  secondaryAction: _propTypes.default.node,
  /**
   * The extra props for the slot components.
   * You can override the existing props or add new ones.
   *
   * @default {}
   */
  slotProps: _propTypes.default.shape({
    root: _propTypes.default.object,
    secondaryAction: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object])
  }),
  /**
   * The components used for each slot inside.
   *
   * @default {}
   */
  slots: _propTypes.default.shape({
    root: _propTypes.default.elementType,
    secondaryAction: _propTypes.default.elementType
  }),
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: _propTypes.default.oneOfType([_propTypes.default.arrayOf(_propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object, _propTypes.default.bool])), _propTypes.default.func, _propTypes.default.object])
} : void 0;
var _default = exports.default = ListItem;