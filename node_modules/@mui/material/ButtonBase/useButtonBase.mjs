'use client';

import * as React from 'react';
import useFocusableWhenDisabled from "../utils/useFocusableWhenDisabled.mjs";
const EMPTY = {};
export default function useButtonBase(parameters) {
  const {
    nativeButton,
    nativeButtonProp,
    internalNativeButton = nativeButton,
    allowInferredHostMismatch = false,
    disabled,
    type,
    hasFormAction = false,
    tabIndex = 0,
    focusableWhenDisabled: focusableWhenDisabledParam,
    stopEventPropagation = false,
    onBeforeKeyDown,
    onBeforeKeyUp
  } = parameters;
  const rootRef = React.useRef(null);
  const focusableWhenDisabled = focusableWhenDisabledParam === true;
  const focusableWhenDisabledProps = useFocusableWhenDisabled({
    focusableWhenDisabled,
    disabled,
    isNativeButton: nativeButton,
    tabIndex
  });
  if (process.env.NODE_ENV !== 'production') {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    React.useEffect(() => {
      const root = rootRef.current;
      if (root == null) {
        return;
      }
      const isButtonTag = root.tagName === 'BUTTON';
      if (nativeButtonProp !== undefined) {
        if (nativeButtonProp && !isButtonTag) {
          const message = 'MUI: A component that acts as a button expected a native <button> because the ' + '`nativeButton` prop is true. Rendering a non-<button> removes native button ' + 'semantics, which can impact forms and accessibility. Render a real <button> ' + 'or set `nativeButton` to `false`.';
          console.error(message);
        }
        if (!nativeButtonProp && isButtonTag) {
          const message = 'MUI: A component that acts as a button expected a non-<button> because the `nativeButton` ' + 'prop is false. Rendering a <button> keeps native behavior while additionally applies ' + 'non-native attributes and handlers, which can add unintended extra attributes (such ' + 'as `role` or `aria-disabled`). Render a non-<button> such as <div>, or set ' + '`nativeButton` to `true`.';
          console.error(message);
        }
        return;
      }
      if (allowInferredHostMismatch) {
        return;
      }

      // warn when expecting a native <button> element but a non-string `component` prop resolved to a non-button element
      if (internalNativeButton && !isButtonTag) {
        const message = 'MUI: A component rendering a native <button> resolved to a non-<button> element, ' + 'but `nativeButton={false}` was not specified and the resolved root is a non-<button>. ' + 'When rendering a custom component, set `nativeButton={false}` explicitly or render a <button> element.';
        console.error(message);
      }

      // warn when expecting a non-button but a non-string `component` prop resolved to a native <button> element
      if (!internalNativeButton && isButtonTag) {
        const message = 'MUI: A component that acts as a non-native button resolved to a native <button> element, ' + 'but `nativeButton={true}` was not specified. ' + 'When rendering a custom component, set `nativeButton={true}` explicitly or render a non-<button> element.';
        console.error(message);
      }
    }, [allowInferredHostMismatch, internalNativeButton, nativeButtonProp]);
  }

  // A helper for event handlers to determine whether to use browser-defined keyboard activation
  // for native elements like <button> and <a href>, or synthesize Enter/Space clicks for non-native
  // elements like `<div role="button">`.
  // This is UNSAFE TO USE outside of event handers, e.g. in render.
  const hasNativeKeyboardActivation = React.useCallback(() => {
    const root = rootRef.current;
    if (root == null) {
      return nativeButton;
    }
    if (root.tagName === 'BUTTON') {
      return true;
    }

    // Although this hook is not intended for links, this check is for
    // backward compatibility with `<ButtonBase href="#" />` since ButtonBase
    // uses the returned event handlers.
    return Boolean(root.tagName === 'A' && root.href);
  }, [nativeButton]);
  const buttonProps = React.useMemo(() => {
    const resolvedButtonProps = focusableWhenDisabled ? {} : {
      tabIndex: disabled ? -1 : tabIndex
    };
    if (nativeButton) {
      resolvedButtonProps.type = type === undefined && !hasFormAction ? 'button' : type;
      if (!focusableWhenDisabled) {
        resolvedButtonProps.disabled = disabled;
      }
    } else {
      resolvedButtonProps.role = 'button';
      if (!focusableWhenDisabled && disabled) {
        resolvedButtonProps['aria-disabled'] = disabled;
      }
    }
    if (focusableWhenDisabled) {
      return {
        ...resolvedButtonProps,
        ...focusableWhenDisabledProps
      };
    }
    return resolvedButtonProps;
  }, [disabled, focusableWhenDisabled, focusableWhenDisabledProps, hasFormAction, nativeButton, tabIndex, type]);
  const getButtonProps = React.useCallback((externalProps = EMPTY) => {
    const {
      onClick: externalOnClick,
      onKeyDown: externalOnKeyDown,
      onKeyUp: externalOnKeyUp,
      ...otherExternalProps
    } = externalProps;
    const handleClick = event => {
      if (stopEventPropagation) {
        event.stopPropagation();
      }
      if (disabled) {
        event.preventDefault();
        return;
      }
      externalOnClick?.(event);
    };
    const handleKeyDown = event => {
      if (focusableWhenDisabled) {
        focusableWhenDisabledProps.onKeyDown(event);
      }
      if (disabled) {
        return;
      }
      onBeforeKeyDown?.(event);
      externalOnKeyDown?.(event);
      if (event.target !== event.currentTarget || hasNativeKeyboardActivation()) {
        return;
      }
      if (event.key === ' ') {
        event.preventDefault();
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        event.currentTarget.click();
      }
    };
    const handleKeyUp = event => {
      if (disabled) {
        return;
      }
      onBeforeKeyUp?.(event);
      externalOnKeyUp?.(event);
      if (event.target === event.currentTarget && !hasNativeKeyboardActivation() && event.key === ' ' && !event.defaultPrevented) {
        event.currentTarget.click();
      }
    };
    return {
      ...buttonProps,
      ...otherExternalProps,
      onClick: handleClick,
      onKeyDown: handleKeyDown,
      onKeyUp: handleKeyUp
    };
  }, [buttonProps, disabled, focusableWhenDisabled, focusableWhenDisabledProps, hasNativeKeyboardActivation, onBeforeKeyDown, onBeforeKeyUp, stopEventPropagation]);
  return {
    getButtonProps,
    rootRef
  };
}