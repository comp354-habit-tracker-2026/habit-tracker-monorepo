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
var _clsx = _interopRequireDefault(require("clsx"));
var _composeClasses = _interopRequireDefault(require("@mui/utils/composeClasses"));
var _zeroStyled = require("../zero-styled");
var _DefaultPropsProvider = require("../DefaultPropsProvider");
var _ButtonBase = _interopRequireDefault(require("../ButtonBase"));
var _StepLabel = _interopRequireDefault(require("../StepLabel"));
var _isMuiElement = _interopRequireDefault(require("../utils/isMuiElement"));
var _useRovingTabIndex = require("../utils/useRovingTabIndex");
var _StepperContext = require("../Stepper/StepperContext");
var _StepContext = _interopRequireDefault(require("../Step/StepContext"));
var _stepButtonClasses = _interopRequireWildcard(require("./stepButtonClasses"));
var _jsxRuntime = require("react/jsx-runtime");
const useUtilityClasses = ownerState => {
  const {
    classes,
    orientation
  } = ownerState;
  const slots = {
    root: ['root', orientation],
    touchRipple: ['touchRipple']
  };
  return (0, _composeClasses.default)(slots, _stepButtonClasses.getStepButtonUtilityClass, classes);
};
const StepButtonRoot = (0, _zeroStyled.styled)(_ButtonBase.default, {
  name: 'MuiStepButton',
  slot: 'Root',
  overridesResolver: (props, styles) => {
    const {
      ownerState
    } = props;
    return [{
      [`& .${_stepButtonClasses.default.touchRipple}`]: styles.touchRipple
    }, styles.root, styles[ownerState.orientation]];
  }
})({
  width: '100%',
  padding: '24px 16px',
  margin: '-24px -16px',
  boxSizing: 'content-box',
  [`& .${_stepButtonClasses.default.touchRipple}`]: {
    color: 'rgba(0, 0, 0, 0.3)'
  },
  variants: [{
    props: {
      orientation: 'vertical'
    },
    style: {
      justifyContent: 'flex-start',
      padding: '8px',
      margin: '-8px'
    }
  }]
});
const RovingStepButton = /*#__PURE__*/React.forwardRef(function RovingStepButton(props, ref) {
  // eslint-disable-next-line react/prop-types
  const {
    children,
    disabled,
    index,
    ...other
  } = props;
  const rovingItemProps = (0, _useRovingTabIndex.useRovingTabIndexItem)({
    id: index,
    ref,
    disabled
  });
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(StepButtonRoot, {
    disabled: disabled,
    ...rovingItemProps,
    ...other,
    children: children
  });
});
const StepButton = /*#__PURE__*/React.forwardRef(function StepButton(inProps, ref) {
  const props = (0, _DefaultPropsProvider.useDefaultProps)({
    props: inProps,
    name: 'MuiStepButton'
  });
  const {
    children,
    className,
    icon,
    optional,
    ...other
  } = props;
  const {
    disabled,
    active,
    index
  } = React.useContext(_StepContext.default);
  const {
    orientation,
    totalSteps,
    isTabList
  } = (0, _StepperContext.useStepperContext)();
  const ownerState = {
    ...props,
    orientation
  };
  const classes = useUtilityClasses(ownerState);
  const childProps = {
    icon,
    optional
  };
  const child = (0, _isMuiElement.default)(children, ['StepLabel']) ? (/*#__PURE__*/React.cloneElement(children, childProps)) : /*#__PURE__*/(0, _jsxRuntime.jsx)(_StepLabel.default, {
    ...childProps,
    children: children
  });
  const stepButtonProps = {
    internalNativeButton: true,
    focusRipple: true,
    disabled,
    TouchRippleProps: {
      className: classes.touchRipple
    },
    className: (0, _clsx.default)(classes.root, className),
    ownerState,
    'aria-selected': active,
    'aria-posinset': index + 1,
    'aria-setsize': totalSteps,
    role: 'tab',
    ...other
  };
  if (isTabList) {
    return /*#__PURE__*/(0, _jsxRuntime.jsx)(RovingStepButton, {
      ...stepButtonProps,
      index: index,
      ref: ref,
      children: child
    });
  }
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(StepButtonRoot, {
    ref: ref,
    tabIndex: active ? 0 : -1,
    ...stepButtonProps,
    children: child
  });
});
process.env.NODE_ENV !== "production" ? StepButton.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * Can be a `StepLabel` or a node to place inside `StepLabel` as children.
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
   * The icon displayed by the step label.
   */
  icon: _propTypes.default.node,
  /**
   * The optional node to display.
   */
  optional: _propTypes.default.node,
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: _propTypes.default.oneOfType([_propTypes.default.arrayOf(_propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object, _propTypes.default.bool])), _propTypes.default.func, _propTypes.default.object])
} : void 0;
var _default = exports.default = StepButton;