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
var _useTimeout = _interopRequireDefault(require("@mui/utils/useTimeout"));
var _elementAcceptingRef = _interopRequireDefault(require("@mui/utils/elementAcceptingRef"));
var _getReactElementRef = _interopRequireDefault(require("@mui/utils/getReactElementRef"));
var _reactTransitionGroup = require("react-transition-group");
var _zeroStyled = require("../zero-styled");
var _utils = require("../transitions/utils");
var _useForkRef = _interopRequireDefault(require("../utils/useForkRef"));
var _jsxRuntime = require("react/jsx-runtime");
function getScale(value) {
  return `scale(${value}, ${value ** 2})`;
}
const styles = {
  entering: {
    opacity: 1,
    transform: getScale(1)
  },
  entered: {
    opacity: 1,
    transform: 'none'
  },
  exiting: {
    opacity: 0,
    transform: getScale(0.75)
  },
  exited: {
    opacity: 0,
    transform: getScale(0.75)
  }
};
const hiddenStyles = {
  opacity: 0,
  transform: getScale(0.75),
  visibility: 'hidden'
};

/**
 * The Grow transition is used by the [Tooltip](/material-ui/react-tooltip/) and
 * [Popover](/material-ui/react-popover/) components.
 * It uses [react-transition-group](https://github.com/reactjs/react-transition-group) internally.
 */
const Grow = /*#__PURE__*/React.forwardRef(function Grow(props, ref) {
  const {
    addEndListener,
    appear = true,
    children,
    easing,
    in: inProp,
    onEnter,
    onEntered,
    onEntering,
    onExit,
    onExited,
    onExiting,
    style,
    timeout = 'auto',
    ...other
  } = props;
  const timer = (0, _useTimeout.default)();
  const autoTimeout = React.useRef();
  const theme = (0, _zeroStyled.useTheme)();
  const nodeRef = React.useRef(null);
  const handleRef = (0, _useForkRef.default)(nodeRef, (0, _getReactElementRef.default)(children), ref);
  const handleEntering = (0, _utils.normalizedTransitionCallback)(nodeRef, onEntering);
  const handleEnter = (0, _utils.normalizedTransitionCallback)(nodeRef, (node, isAppearing) => {
    (0, _utils.reflow)(node); // So the animation always start from the start.

    const {
      duration: transitionDuration,
      delay,
      easing: transitionTimingFunction
    } = (0, _utils.getTransitionProps)({
      style,
      timeout,
      easing
    }, {
      mode: 'enter'
    });
    let duration;
    if (timeout === 'auto') {
      duration = theme.transitions.getAutoHeightDuration(node.clientHeight);
      autoTimeout.current = duration;
    } else {
      duration = transitionDuration;
    }
    node.style.transition = [theme.transitions.create('opacity', {
      duration,
      delay
    }), theme.transitions.create('transform', {
      duration: duration * 0.666,
      delay,
      easing: transitionTimingFunction
    })].join(',');
    if (onEnter) {
      onEnter(node, isAppearing);
    }
  });
  const handleEntered = (0, _utils.normalizedTransitionCallback)(nodeRef, onEntered);
  const handleExiting = (0, _utils.normalizedTransitionCallback)(nodeRef, onExiting);
  const handleExit = (0, _utils.normalizedTransitionCallback)(nodeRef, node => {
    const {
      duration: transitionDuration,
      delay,
      easing: transitionTimingFunction
    } = (0, _utils.getTransitionProps)({
      style,
      timeout,
      easing
    }, {
      mode: 'exit'
    });
    let duration;
    if (timeout === 'auto') {
      duration = theme.transitions.getAutoHeightDuration(node.clientHeight);
      autoTimeout.current = duration;
    } else {
      duration = transitionDuration;
    }
    node.style.transition = [theme.transitions.create('opacity', {
      duration,
      delay
    }), theme.transitions.create('transform', {
      duration: duration * 0.666,
      delay: delay || duration * 0.333,
      easing: transitionTimingFunction
    })].join(',');
    node.style.opacity = 0;
    node.style.transform = getScale(0.75);
    if (onExit) {
      onExit(node);
    }
  });
  const handleExited = (0, _utils.normalizedTransitionCallback)(nodeRef, node => {
    node.style.transition = '';
    if (onExited) {
      onExited(node);
    }
  });
  const handleAddEndListener = next => {
    if (timeout === 'auto') {
      timer.start(autoTimeout.current || 0, next);
    }
    if (addEndListener) {
      // Old call signature before `react-transition-group` implemented `nodeRef`
      addEndListener(nodeRef.current, next);
    }
  };
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(_reactTransitionGroup.Transition, {
    appear: appear,
    in: inProp,
    nodeRef: nodeRef,
    onEnter: handleEnter,
    onEntered: handleEntered,
    onEntering: handleEntering,
    onExit: handleExit,
    onExited: handleExited,
    onExiting: handleExiting,
    addEndListener: handleAddEndListener,
    timeout: timeout === 'auto' ? null : timeout,
    ...other,
    children: (state, {
      ownerState,
      ...restChildProps
    }) => {
      const childStyle = (0, _utils.getTransitionChildStyle)(state, inProp, styles, hiddenStyles, style, children.props.style);
      return /*#__PURE__*/React.cloneElement(children, {
        style: childStyle,
        ref: handleRef,
        ...restChildProps
      });
    }
  });
});
process.env.NODE_ENV !== "production" ? Grow.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * Add a custom transition end trigger. Called with the transitioning DOM
   * node and a done callback. Allows for more fine grained transition end
   * logic. Note: Timeouts are still used as a fallback if provided.
   */
  addEndListener: _propTypes.default.func,
  /**
   * Perform the enter transition when it first mounts if `in` is also `true`.
   * Set this to `false` to disable this behavior.
   * @default true
   */
  appear: _propTypes.default.bool,
  /**
   * A single child content element.
   */
  children: _elementAcceptingRef.default.isRequired,
  /**
   * The transition timing function.
   * You may specify a single easing or a object containing enter and exit values.
   */
  easing: _propTypes.default.oneOfType([_propTypes.default.shape({
    enter: _propTypes.default.string,
    exit: _propTypes.default.string
  }), _propTypes.default.string]),
  /**
   * If `true`, the component will transition in.
   */
  in: _propTypes.default.bool,
  /**
   * @ignore
   */
  onEnter: _propTypes.default.func,
  /**
   * @ignore
   */
  onEntered: _propTypes.default.func,
  /**
   * @ignore
   */
  onEntering: _propTypes.default.func,
  /**
   * @ignore
   */
  onExit: _propTypes.default.func,
  /**
   * @ignore
   */
  onExited: _propTypes.default.func,
  /**
   * @ignore
   */
  onExiting: _propTypes.default.func,
  /**
   * @ignore
   */
  style: _propTypes.default.object,
  /**
   * The duration for the transition, in milliseconds.
   * You may specify a single timeout for all transitions, or individually with an object.
   *
   * Set to 'auto' to automatically calculate transition time based on height.
   * @default 'auto'
   */
  timeout: _propTypes.default.oneOfType([_propTypes.default.oneOf(['auto']), _propTypes.default.number, _propTypes.default.shape({
    appear: _propTypes.default.number,
    enter: _propTypes.default.number,
    exit: _propTypes.default.number
  })])
} : void 0;
if (Grow) {
  Grow.muiSupportAuto = true;
}
var _default = exports.default = Grow;