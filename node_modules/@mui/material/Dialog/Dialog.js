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
var _useId = _interopRequireDefault(require("@mui/utils/useId"));
var _capitalize = _interopRequireDefault(require("../utils/capitalize"));
var _Modal = _interopRequireDefault(require("../Modal"));
var _Fade = _interopRequireDefault(require("../Fade"));
var _Paper = _interopRequireDefault(require("../Paper"));
var _dialogClasses = require("./dialogClasses");
var _DialogContext = _interopRequireDefault(require("./DialogContext"));
var _Backdrop = _interopRequireDefault(require("../Backdrop"));
var _zeroStyled = require("../zero-styled");
var _memoTheme = _interopRequireDefault(require("../utils/memoTheme"));
var _DefaultPropsProvider = require("../DefaultPropsProvider");
var _useSlot = _interopRequireDefault(require("../utils/useSlot"));
var _jsxRuntime = require("react/jsx-runtime");
const DialogBackdrop = (0, _zeroStyled.styled)(_Backdrop.default, {
  name: 'MuiDialog',
  slot: 'Backdrop'
})({
  // Improve scrollable dialog support.
  zIndex: -1
});
const useUtilityClasses = ownerState => {
  const {
    classes,
    scroll,
    maxWidth,
    fullWidth,
    fullScreen
  } = ownerState;
  const slots = {
    root: ['root'],
    backdrop: ['backdrop'],
    container: ['container', `scroll${(0, _capitalize.default)(scroll)}`],
    paper: ['paper', `paperWidth${(0, _capitalize.default)(String(maxWidth))}`, fullWidth && 'paperFullWidth', fullScreen && 'paperFullScreen']
  };
  return (0, _composeClasses.default)(slots, _dialogClasses.getDialogUtilityClass, classes);
};
const DialogRoot = (0, _zeroStyled.styled)(_Modal.default, {
  name: 'MuiDialog',
  slot: 'Root'
})({
  '@media print': {
    // Use !important to override the Modal inline-style.
    position: 'absolute !important'
  }
});
const DialogContainer = (0, _zeroStyled.styled)('div', {
  name: 'MuiDialog',
  slot: 'Container',
  overridesResolver: (props, styles) => {
    const {
      ownerState
    } = props;
    return [styles.container, styles[`scroll${(0, _capitalize.default)(ownerState.scroll)}`]];
  }
})({
  height: '100%',
  '@media print': {
    height: 'auto'
  },
  // We disable the focus ring for mouse, touch and keyboard users.
  outline: 0,
  variants: [{
    props: {
      scroll: 'paper'
    },
    style: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    }
  }, {
    props: {
      scroll: 'body'
    },
    style: {
      overflowY: 'auto',
      overflowX: 'hidden',
      textAlign: 'center',
      '&::after': {
        content: '""',
        display: 'inline-block',
        verticalAlign: 'middle',
        height: '100%',
        width: '0'
      }
    }
  }]
});
const DialogPaper = (0, _zeroStyled.styled)(_Paper.default, {
  name: 'MuiDialog',
  slot: 'Paper',
  overridesResolver: (props, styles) => {
    const {
      ownerState
    } = props;
    return [styles.paper, styles[`paperWidth${(0, _capitalize.default)(String(ownerState.maxWidth))}`], ownerState.fullWidth && styles.paperFullWidth, ownerState.fullScreen && styles.paperFullScreen];
  }
})((0, _memoTheme.default)(({
  theme
}) => ({
  margin: 32,
  position: 'relative',
  overflowY: 'auto',
  '@media print': {
    overflowY: 'visible',
    boxShadow: 'none'
  },
  variants: [{
    props: {
      scroll: 'paper'
    },
    style: {
      display: 'flex',
      flexDirection: 'column',
      maxHeight: 'calc(100% - 64px)'
    }
  }, {
    props: {
      scroll: 'body'
    },
    style: {
      display: 'inline-block',
      verticalAlign: 'middle',
      textAlign: 'initial'
    }
  }, {
    props: ({
      ownerState
    }) => !ownerState.maxWidth,
    style: {
      maxWidth: 'calc(100% - 64px)'
    }
  }, {
    props: {
      maxWidth: 'xs'
    },
    style: {
      maxWidth: theme.breakpoints.unit === 'px' ? Math.max(theme.breakpoints.values.xs, 444) : `max(${theme.breakpoints.values.xs}${theme.breakpoints.unit}, 444px)`
    }
  }, {
    props: {
      maxWidth: 'xs',
      scroll: 'body'
    },
    style: {
      [theme.breakpoints.down(Math.max(theme.breakpoints.values.xs, 444) + 32 * 2)]: {
        maxWidth: 'calc(100% - 64px)'
      }
    }
  }, ...Object.keys(theme.breakpoints.values).filter(maxWidth => maxWidth !== 'xs').map(maxWidth => ({
    props: {
      maxWidth
    },
    style: {
      maxWidth: `${theme.breakpoints.values[maxWidth]}${theme.breakpoints.unit}`
    }
  })), ...Object.keys(theme.breakpoints.values).filter(maxWidth => maxWidth !== 'xs').map(maxWidth => ({
    props: {
      maxWidth,
      scroll: 'body'
    },
    style: {
      [theme.breakpoints.down(theme.breakpoints.values[maxWidth] + 32 * 2)]: {
        maxWidth: 'calc(100% - 64px)'
      }
    }
  })), {
    props: ({
      ownerState
    }) => ownerState.fullWidth,
    style: {
      width: 'calc(100% - 64px)'
    }
  }, {
    props: ({
      ownerState
    }) => ownerState.fullScreen,
    style: {
      margin: 0,
      width: '100%',
      maxWidth: '100%',
      height: '100%',
      maxHeight: 'none',
      borderRadius: 0
    }
  }, {
    props: ({
      ownerState
    }) => ownerState.fullScreen && ownerState.scroll === 'body',
    style: {
      margin: 0,
      maxWidth: '100%'
    }
  }]
})));

/**
 * Dialogs are overlaid modal paper based components with a backdrop.
 */
const Dialog = /*#__PURE__*/React.forwardRef(function Dialog(inProps, ref) {
  const props = (0, _DefaultPropsProvider.useDefaultProps)({
    props: inProps,
    name: 'MuiDialog'
  });
  const theme = (0, _zeroStyled.useTheme)();
  const defaultTransitionDuration = {
    enter: theme.transitions.duration.enteringScreen,
    exit: theme.transitions.duration.leavingScreen
  };
  const {
    'aria-describedby': ariaDescribedby,
    'aria-labelledby': ariaLabelledbyProp,
    'aria-modal': ariaModal = true,
    children,
    className,
    fullScreen = false,
    fullWidth = false,
    maxWidth = 'sm',
    onClick,
    onClose,
    open,
    PaperComponent = _Paper.default,
    role = 'dialog',
    scroll = 'paper',
    slots = {},
    slotProps = {},
    transitionDuration = defaultTransitionDuration,
    ...other
  } = props;
  const ownerState = {
    ...props,
    fullScreen,
    fullWidth,
    maxWidth,
    scroll
  };
  const classes = useUtilityClasses(ownerState);
  const backdropClick = React.useRef();
  const handleMouseDown = event => {
    // We don't want to close the dialog when clicking the dialog content.
    // Make sure the event starts and ends on the same DOM element.
    backdropClick.current = event.target === event.currentTarget;
  };
  const handleBackdropClick = event => {
    if (onClick) {
      onClick(event);
    }

    // Ignore the events not coming from the "backdrop".
    if (!backdropClick.current) {
      return;
    }
    backdropClick.current = null;
    if (onClose) {
      onClose(event, 'backdropClick');
    }
  };
  const ariaLabelledby = (0, _useId.default)(ariaLabelledbyProp);
  const dialogContextValue = React.useMemo(() => {
    return {
      titleId: ariaLabelledby
    };
  }, [ariaLabelledby]);
  const externalForwardedProps = {
    slots,
    slotProps
  };
  const [RootSlot, rootSlotProps] = (0, _useSlot.default)('root', {
    elementType: DialogRoot,
    shouldForwardComponentProp: true,
    externalForwardedProps,
    ownerState,
    className: (0, _clsx.default)(classes.root, className),
    ref
  });
  const [BackdropSlot, backdropSlotProps] = (0, _useSlot.default)('backdrop', {
    elementType: DialogBackdrop,
    shouldForwardComponentProp: true,
    externalForwardedProps,
    ownerState,
    className: classes.backdrop
  });
  const [PaperSlot, paperSlotProps] = (0, _useSlot.default)('paper', {
    elementType: DialogPaper,
    shouldForwardComponentProp: true,
    externalForwardedProps,
    ownerState,
    className: classes.paper
  });
  const [ContainerSlot, containerSlotProps] = (0, _useSlot.default)('container', {
    elementType: DialogContainer,
    externalForwardedProps,
    ownerState,
    className: classes.container
  });
  const [TransitionSlot, transitionSlotProps] = (0, _useSlot.default)('transition', {
    elementType: _Fade.default,
    externalForwardedProps,
    ownerState,
    additionalProps: {
      appear: true,
      in: open,
      timeout: transitionDuration,
      role: 'presentation'
    }
  });
  return /*#__PURE__*/(0, _jsxRuntime.jsx)(RootSlot, {
    closeAfterTransition: true,
    slots: {
      backdrop: BackdropSlot
    },
    slotProps: {
      backdrop: {
        transitionDuration,
        ...backdropSlotProps
      }
    },
    onClose: onClose,
    open: open,
    onClick: handleBackdropClick,
    ...rootSlotProps,
    ...other,
    children: /*#__PURE__*/(0, _jsxRuntime.jsx)(TransitionSlot, {
      ...transitionSlotProps,
      children: /*#__PURE__*/(0, _jsxRuntime.jsx)(ContainerSlot, {
        onMouseDown: handleMouseDown,
        ...containerSlotProps,
        children: /*#__PURE__*/(0, _jsxRuntime.jsx)(PaperSlot, {
          as: PaperComponent,
          elevation: 24,
          role: role,
          "aria-describedby": ariaDescribedby,
          "aria-labelledby": ariaLabelledby,
          "aria-modal": ariaModal,
          ...paperSlotProps,
          children: /*#__PURE__*/(0, _jsxRuntime.jsx)(_DialogContext.default.Provider, {
            value: dialogContextValue,
            children: children
          })
        })
      })
    })
  });
});
process.env.NODE_ENV !== "production" ? Dialog.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * The id(s) of the element(s) that describe the dialog.
   */
  'aria-describedby': _propTypes.default.string,
  /**
   * The id(s) of the element(s) that label the dialog.
   */
  'aria-labelledby': _propTypes.default.string,
  /**
   * Informs assistive technologies that the element is modal.
   * It's added on the element with role="dialog".
   * @default true
   */
  'aria-modal': _propTypes.default.oneOfType([_propTypes.default.oneOf(['false', 'true']), _propTypes.default.bool]),
  /**
   * Dialog children, usually the included sub-components.
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
   * If `true`, the dialog is full-screen.
   * @default false
   */
  fullScreen: _propTypes.default.bool,
  /**
   * If `true`, the dialog stretches to `maxWidth`.
   *
   * Notice that the dialog width grow is limited by the default margin.
   * @default false
   */
  fullWidth: _propTypes.default.bool,
  /**
   * Determine the max-width of the dialog.
   * The dialog width grows with the size of the screen.
   * Set to `false` to disable `maxWidth`.
   * @default 'sm'
   */
  maxWidth: _propTypes.default /* @typescript-to-proptypes-ignore */.oneOfType([_propTypes.default.oneOf(['xs', 'sm', 'md', 'lg', 'xl', false]), _propTypes.default.string]),
  /**
   * @ignore
   */
  onClick: _propTypes.default.func,
  /**
   * Callback fired when the component requests to be closed.
   *
   * @param {object} event The event source of the callback.
   * @param {string} reason Can be: `"escapeKeyDown"`, `"backdropClick"`.
   */
  onClose: _propTypes.default.func,
  /**
   * If `true`, the component is shown.
   */
  open: _propTypes.default.bool.isRequired,
  /**
   * The component used to render the body of the dialog.
   * @default Paper
   */
  PaperComponent: _propTypes.default.elementType,
  /**
   * The ARIA role for the dialog element.
   * The main dialog role is `dialog`, but `alertdialog` can be used if the content of the dialog requires immediate attention.
   * See https://www.w3.org/TR/wai-aria-1.2/#dialog and https://www.w3.org/TR/wai-aria-1.2/#alertdialog for more details.
   * @default 'dialog'
   */
  role: _propTypes.default.oneOf(['alertdialog', 'dialog']),
  /**
   * Determine the container for scrolling the dialog.
   * @default 'paper'
   */
  scroll: _propTypes.default.oneOf(['body', 'paper']),
  /**
   * The props used for each slot inside.
   * @default {}
   */
  slotProps: _propTypes.default.shape({
    backdrop: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
    container: _propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object]),
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
    container: _propTypes.default.elementType,
    paper: _propTypes.default.elementType,
    root: _propTypes.default.elementType,
    transition: _propTypes.default.elementType
  }),
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: _propTypes.default.oneOfType([_propTypes.default.arrayOf(_propTypes.default.oneOfType([_propTypes.default.func, _propTypes.default.object, _propTypes.default.bool])), _propTypes.default.func, _propTypes.default.object]),
  /**
   * The duration for the transition, in milliseconds.
   * You may specify a single timeout for all transitions, or individually with an object.
   * @default {
   *   enter: theme.transitions.duration.enteringScreen,
   *   exit: theme.transitions.duration.leavingScreen,
   * }
   */
  transitionDuration: _propTypes.default.oneOfType([_propTypes.default.number, _propTypes.default.shape({
    appear: _propTypes.default.number,
    enter: _propTypes.default.number,
    exit: _propTypes.default.number
  })])
} : void 0;
var _default = exports.default = Dialog;