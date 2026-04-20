"use strict";
'use client';

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
exports.setTranslateValue = setTranslateValue;
var React = _interopRequireWildcard(require("react"));
var _propTypes = _interopRequireDefault(require("prop-types"));
var _reactTransitionGroup = require("react-transition-group");
var _chainPropTypes = _interopRequireDefault(require("@mui/utils/chainPropTypes"));
var _HTMLElementType = _interopRequireDefault(require("@mui/utils/HTMLElementType"));
var _elementAcceptingRef = _interopRequireDefault(require("@mui/utils/elementAcceptingRef"));
var _getReactElementRef = _interopRequireDefault(require("@mui/utils/getReactElementRef"));
var _isLayoutSupported = _interopRequireDefault(require("../utils/isLayoutSupported"));
var _debounce = _interopRequireDefault(require("../utils/debounce"));
var _useForkRef = _interopRequireDefault(require("../utils/useForkRef"));
var _zeroStyled = require("../zero-styled");
var _utils = require("../transitions/utils");
var _utils2 = require("../utils");
var _jsxRuntime = require("react/jsx-runtime");
const hiddenStyles = {
  visibility: 'hidden'
};

// Translate the node so it can't be seen on the screen.
// Later, we're going to translate the node back to its original location with `none`.
function getTranslateValue(direction, node, resolvedContainer) {
  const containerRect = resolvedContainer && resolvedContainer.getBoundingClientRect();
  const containerWindow = (0, _utils2.ownerWindow)(node);

  // Clear the inline transform and transition before reading layout and computed
  // style so we compute from the element's natural position, not its previous
  // off-screen translation. The transition must also be cleared, otherwise the
  // browser may report an animated intermediate value from a still-running
  // enter transition when reading getComputedStyle during exit.
  const previousTransform = node.style.transform;
  const previousTransition = node.style.transition;
  node.style.transition = '';
  node.style.transform = '';
  const rect = node.getBoundingClientRect();
  const computedStyle = containerWindow.getComputedStyle(node);
  const transform = computedStyle.getPropertyValue('transform');
  node.style.transform = previousTransform;
  node.style.transition = previousTransition;
  let offsetX = 0;
  let offsetY = 0;
  if (transform && transform !== 'none' && typeof transform === 'string') {
    const transformValues = transform.split('(')[1].split(')')[0].split(',');
    offsetX = parseInt(transformValues[4], 10);
    offsetY = parseInt(transformValues[5], 10);
  }
  if (direction === 'left') {
    if (containerRect) {
      return `translateX(${containerRect.right + offsetX - rect.left}px)`;
    }
    return `translateX(${containerWindow.innerWidth + offsetX - rect.left}px)`;
  }
  if (direction === 'right') {
    if (containerRect) {
      return `translateX(-${rect.right - containerRect.left - offsetX}px)`;
    }
    return `translateX(-${rect.left + rect.width - offsetX}px)`;
  }
  if (direction === 'up') {
    if (containerRect) {
      return `translateY(${containerRect.bottom + offsetY - rect.top}px)`;
    }
    return `translateY(${containerWindow.innerHeight + offsetY - rect.top}px)`;
  }

  // direction === 'down'
  if (containerRect) {
    return `translateY(-${rect.top - containerRect.top + rect.height - offsetY}px)`;
  }
  return `translateY(-${rect.top + rect.height - offsetY}px)`;
}
function resolveContainer(containerPropProp) {
  return typeof containerPropProp === 'function' ? containerPropProp() : containerPropProp;
}
function setTranslateValue(direction, node, containerProp) {
  const resolvedContainer = resolveContainer(containerProp);
  const transform = getTranslateValue(direction, node, resolvedContainer);
  if (transform) {
    node.style.transform = transform;
  }
}

/**
 * The Slide transition is used by the [Drawer](/material-ui/react-drawer/) component.
 * It uses [react-transition-group](https://github.com/reactjs/react-transition-group) internally.
 */
const Slide = /*#__PURE__*/React.forwardRef(function Slide(props, ref) {
  const theme = (0, _zeroStyled.useTheme)();
  const defaultEasing = {
    enter: theme.transitions.easing.easeOut,
    exit: theme.transitions.easing.sharp
  };
  const defaultTimeout = {
    enter: theme.transitions.duration.enteringScreen,
    exit: theme.transitions.duration.leavingScreen
  };
  const {
    addEndListener,
    appear = true,
    children,
    container: containerProp,
    direction = 'down',
    easing: easingProp = defaultEasing,
    in: inProp,
    onEnter,
    onEntered,
    onEntering,
    onExit,
    onExited,
    onExiting,
    style,
    timeout = defaultTimeout,
    ...other
  } = props;
  const childrenRef = React.useRef(null);
  const handleRef = (0, _useForkRef.default)((0, _getReactElementRef.default)(children), childrenRef, ref);
  const handleEnter = (0, _utils.normalizedTransitionCallback)(childrenRef, (node, isAppearing) => {
    setTranslateValue(direction, node, containerProp);
    (0, _utils.reflow)(node);
    if (onEnter) {
      onEnter(node, isAppearing);
    }
  });
  const handleEntering = (0, _utils.normalizedTransitionCallback)(childrenRef, (node, isAppearing) => {
    const transitionProps = (0, _utils.getTransitionProps)({
      timeout,
      style,
      easing: easingProp
    }, {
      mode: 'enter'
    });
    node.style.transition = theme.transitions.create('transform', transitionProps);
    node.style.transform = 'none';
    if (onEntering) {
      onEntering(node, isAppearing);
    }
  });
  const handleEntered = (0, _utils.normalizedTransitionCallback)(childrenRef, onEntered);
  const handleExiting = (0, _utils.normalizedTransitionCallback)(childrenRef, onExiting);
  const handleExit = (0, _utils.normalizedTransitionCallback)(childrenRef, node => {
    const transitionProps = (0, _utils.getTransitionProps)({
      timeout,
      style,
      easing: easingProp
    }, {
      mode: 'exit'
    });
    node.style.transition = theme.transitions.create('transform', transitionProps);
    setTranslateValue(direction, node, containerProp);
    if (onExit) {
      onExit(node);
    }
  });
  const handleExited = (0, _utils.normalizedTransitionCallback)(childrenRef, node => {
    // No need for transitions when the component is hidden
    node.style.transition = '';
    if (onExited) {
      onExited(node);
    }
  });
  const handleAddEndListener = next => {
    if (addEndListener) {
      // Old call signature before `react-transition-group` implemented `nodeRef`
      addEndListener(childrenRef.current, next);
    }
  };
  const updatePosition = React.useCallback(() => {
    if (childrenRef.current) {
      setTranslateValue(direction, childrenRef.current, containerProp);
    }
  }, [direction, containerProp]);
  React.useEffect(() => {
    // Skip configuration where the position is screen size invariant.
    if (inProp || direction === 'down' || direction === 'right') {
      return undefined;
    }
    const handleResize = (0, _debounce.default)(() => {
      if (childrenRef.current) {
        setTranslateValue(direction, childrenRef.current, containerProp);
      }
    });
    const containerWindow = (0, _utils2.ownerWindow)(childrenRef.current);
    containerWindow.addEventListener('resize', handleResize);
    return () => {
      handleResize.clear();
      containerWindow.removeEventListener('resize', handleResize);
    };
  }, [direction, inProp, containerProp]);
  React.useEffect(() => {
    if (!inProp) {
      // We need to update the position of the drawer when the direction change and
      // when it's hidden.
      updatePosition();
    }
  }, [inProp, updatePosition]);
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(_reactTransitionGroup.Transition, {
    nodeRef: childrenRef,
    onEnter: handleEnter,
    onEntered: handleEntered,
    onEntering: handleEntering,
    onExit: handleExit,
    onExited: handleExited,
    onExiting: handleExiting,
    addEndListener: handleAddEndListener,
    appear: appear,
    in: inProp,
    timeout: timeout,
    ...other,
    children: (state, {
      ownerState,
      ...restChildProps
    }) => {
      let childStyle;
      if (state === 'exited' && !inProp) {
        childStyle = style || children.props.style ? {
          visibility: 'hidden',
          ...style,
          ...children.props.style
        } : hiddenStyles;
      } else if (style && children.props.style) {
        childStyle = {
          ...style,
          ...children.props.style
        };
      } else {
        childStyle = style || children.props.style;
      }
      return /*#__PURE__*/React.cloneElement(children, {
        ref: handleRef,
        style: childStyle,
        ...restChildProps
      });
    }
  });
});
process.env.NODE_ENV !== "production" ? Slide.propTypes /* remove-proptypes */ = {
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
   * An HTML element, or a function that returns one.
   * It's used to set the container the Slide is transitioning from.
   */
  container: (0, _chainPropTypes.default)(_propTypes.default.oneOfType([_HTMLElementType.default, _propTypes.default.func]), props => {
    if (props.open) {
      const resolvedContainer = resolveContainer(props.container);
      if (resolvedContainer && resolvedContainer.nodeType === 1) {
        const box = resolvedContainer.getBoundingClientRect();
        if (process.env.NODE_ENV !== 'production') {
          if ((0, _isLayoutSupported.default)() && box.top === 0 && box.left === 0 && box.right === 0 && box.bottom === 0) {
            return new Error(['MUI: The `container` prop provided to the component is invalid.', 'The anchor element should be part of the document layout.', "Make sure the element is present in the document or that it's not display none."].join('\n'));
          }
        }
      } else if (!resolvedContainer || typeof resolvedContainer.getBoundingClientRect !== 'function' || resolvedContainer.contextElement != null && resolvedContainer.contextElement.nodeType !== 1) {
        return new Error(['MUI: The `container` prop provided to the component is invalid.', 'It should be an HTML element instance.'].join('\n'));
      }
    }
    return null;
  }),
  /**
   * Direction the child node will enter from.
   * @default 'down'
   */
  direction: _propTypes.default.oneOf(['down', 'left', 'right', 'up']),
  /**
   * The transition timing function.
   * You may specify a single easing or a object containing enter and exit values.
   * @default {
   *   enter: theme.transitions.easing.easeOut,
   *   exit: theme.transitions.easing.sharp,
   * }
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
   * @default {
   *   enter: theme.transitions.duration.enteringScreen,
   *   exit: theme.transitions.duration.leavingScreen,
   * }
   */
  timeout: _propTypes.default.oneOfType([_propTypes.default.number, _propTypes.default.shape({
    appear: _propTypes.default.number,
    enter: _propTypes.default.number,
    exit: _propTypes.default.number
  })])
} : void 0;
var _default = exports.default = Slide;