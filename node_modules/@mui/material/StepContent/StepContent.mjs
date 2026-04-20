'use client';

import * as React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import composeClasses from '@mui/utils/composeClasses';
import { styled } from "../zero-styled/index.mjs";
import memoTheme from "../utils/memoTheme.mjs";
import { useDefaultProps } from "../DefaultPropsProvider/index.mjs";
import Collapse from "../Collapse/index.mjs";
import { useStepperContext } from "../Stepper/StepperContext.mjs";
import StepContext from "../Step/StepContext.mjs";
import { getStepContentUtilityClass } from "./stepContentClasses.mjs";
import useSlot from "../utils/useSlot.mjs";
import { jsx as _jsx } from "react/jsx-runtime";
const useUtilityClasses = ownerState => {
  const {
    classes,
    last
  } = ownerState;
  const slots = {
    root: ['root', last && 'last'],
    transition: ['transition']
  };
  return composeClasses(slots, getStepContentUtilityClass, classes);
};
const StepContentRoot = styled('div', {
  name: 'MuiStepContent',
  slot: 'Root',
  overridesResolver: (props, styles) => {
    const {
      ownerState
    } = props;
    return [styles.root, ownerState.last && styles.last];
  }
})(memoTheme(({
  theme
}) => ({
  marginLeft: 12,
  // half icon
  paddingLeft: 8 + 12,
  // margin + half icon
  paddingRight: 8,
  borderLeft: theme.vars ? `1px solid ${theme.vars.palette.StepContent.border}` : `1px solid ${theme.palette.mode === 'light' ? theme.palette.grey[400] : theme.palette.grey[600]}`,
  variants: [{
    props: {
      last: true
    },
    style: {
      borderLeft: 'none'
    }
  }]
})));
const StepContentTransition = styled(Collapse, {
  name: 'MuiStepContent',
  slot: 'Transition'
})({});
const StepContent = /*#__PURE__*/React.forwardRef(function StepContent(inProps, ref) {
  const props = useDefaultProps({
    props: inProps,
    name: 'MuiStepContent'
  });
  const {
    children,
    className,
    transitionDuration: transitionDurationProp = 'auto',
    slots = {},
    slotProps = {},
    ...other
  } = props;
  const {
    orientation
  } = useStepperContext();
  const {
    active,
    last,
    expanded
  } = React.useContext(StepContext);
  const ownerState = {
    ...props,
    last
  };
  const classes = useUtilityClasses(ownerState);
  if (process.env.NODE_ENV !== 'production') {
    if (orientation !== 'vertical') {
      console.error('MUI: <StepContent /> is only designed for use with the vertical stepper.');
    }
  }
  let transitionDuration = transitionDurationProp;
  if (transitionDurationProp === 'auto' && !(slots.transition ?? Collapse).muiSupportAuto) {
    transitionDuration = undefined;
  }
  const externalForwardedProps = {
    slots,
    slotProps
  };
  const [TransitionSlot, transitionProps] = useSlot('transition', {
    elementType: StepContentTransition,
    externalForwardedProps,
    ownerState,
    className: classes.transition,
    additionalProps: {
      in: active || expanded,
      timeout: transitionDuration,
      unmountOnExit: true
    }
  });
  return /*#__PURE__*/_jsx(StepContentRoot, {
    className: clsx(classes.root, className),
    ref: ref,
    ownerState: ownerState,
    ...other,
    children: /*#__PURE__*/_jsx(TransitionSlot, {
      ...transitionProps,
      children: children
    })
  });
});
process.env.NODE_ENV !== "production" ? StepContent.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * The content of the component.
   */
  children: PropTypes.node,
  /**
   * Override or extend the styles applied to the component.
   */
  classes: PropTypes.object,
  /**
   * @ignore
   */
  className: PropTypes.string,
  /**
   * The props used for each slot inside.
   * @default {}
   */
  slotProps: PropTypes.shape({
    transition: PropTypes.oneOfType([PropTypes.func, PropTypes.object])
  }),
  /**
   * The components used for each slot inside.
   * @default {}
   */
  slots: PropTypes.shape({
    transition: PropTypes.elementType
  }),
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.func, PropTypes.object, PropTypes.bool])), PropTypes.func, PropTypes.object]),
  /**
   * Adjust the duration of the content expand transition.
   * Passed as a prop to the transition component.
   *
   * Set to 'auto' to automatically calculate transition time based on height.
   * @default 'auto'
   */
  transitionDuration: PropTypes.oneOfType([PropTypes.oneOf(['auto']), PropTypes.number, PropTypes.shape({
    appear: PropTypes.number,
    enter: PropTypes.number,
    exit: PropTypes.number
  })])
} : void 0;
export default StepContent;