"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getTransitionChildStyle = getTransitionChildStyle;
exports.getTransitionProps = getTransitionProps;
exports.normalizedTransitionCallback = normalizedTransitionCallback;
exports.reflow = void 0;
const reflow = node => node.scrollTop;
exports.reflow = reflow;
function normalizedTransitionCallback(nodeRef, callback) {
  return maybeIsAppearing => {
    if (callback) {
      const node = nodeRef.current;
      // onEnterXxx and onExitXxx callbacks have a different arguments.length value.
      if (maybeIsAppearing === undefined) {
        callback(node);
      } else {
        callback(node, maybeIsAppearing);
      }
    }
  };
}
/**
 * Computes the child style for a transition component, reusing existing
 * references when possible to preserve referential equality for React.memo.
 */
function getTransitionChildStyle(state, inProp, baseStyles, hiddenStyles, styleProp, childStyle) {
  const base = state === 'exited' && !inProp ? hiddenStyles : baseStyles[state] || baseStyles.exited;
  return styleProp || childStyle ? {
    ...base,
    ...styleProp,
    ...childStyle
  } : base;
}
function getTransitionProps(props, options) {
  const {
    timeout,
    easing,
    style = {}
  } = props;
  return {
    duration: style.transitionDuration ?? (typeof timeout === 'number' ? timeout : timeout[options.mode] || 0),
    easing: style.transitionTimingFunction ?? (typeof easing === 'object' ? easing[options.mode] : easing),
    delay: style.transitionDelay
  };
}