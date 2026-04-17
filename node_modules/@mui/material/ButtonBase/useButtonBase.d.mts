import * as React from 'react';
export interface UseButtonBaseParameters {
  /**
   * Whether the root should be treated as a native `<button>` for render-time semantics.
   */
  nativeButton: boolean;
  /**
   * The explicit `nativeButton` value provided by the caller, if any.
   */
  nativeButtonProp?: boolean | undefined;
  /**
   * Whether the default rendered element is expected to be a native button when
   * `nativeButton` was not explicitly provided.
   * @default nativeButton
   */
  internalNativeButton?: boolean | undefined;
  /**
   * Whether to perform additional checks in dev mode on whether the resolved element
   * matches the default native or non-native button expectation.
   * Set to `true` to allow hook callers bypass this check, e.g. when the `component`
   * prop is a string.
   * @default false
   */
  allowInferredHostMismatch?: boolean | undefined;
  /**
   * The disabled state of the component.
   */
  disabled: boolean;
  /**
   * The `type` attribute for the element.
   */
  type?: string | undefined;
  /**
   * Whether the element has a `formAction` attribute. When true, the hook
   * will not default `type` to `'button'` for native buttons so the browser
   * can use its natural submit behaviour.
   * @default false
   */
  hasFormAction?: boolean | undefined;
  /**
   * The `tabIndex` attribute for the element.
   * @default 0
   */
  tabIndex?: number | undefined;
  /**
   * When `true`, a disabled root can remain focusable.
   * When `undefined`, the feature is not enabled.
   */
  focusableWhenDisabled?: boolean | undefined;
  /**
   * When `true`, calls `event.stopPropagation()` on click before the disabled guard runs.
   * @default false
   */
  stopEventPropagation?: boolean | undefined;
  /**
   * An additional function that will run before the user's `onKeyDown`, e.g.
   * to trigger the ripple effect in `<ButtonBase>`.
   */
  onBeforeKeyDown?: React.KeyboardEventHandler<HTMLElement> | undefined;
  /**
   * An additional function that will run before the user's `onKeyUp`, e.g.
   * to control the ripple effect in `<ButtonBase>`.
   */
  onBeforeKeyUp?: React.KeyboardEventHandler<HTMLElement> | undefined;
}
export interface ButtonBaseButtonProps {
  role?: string | undefined;
  'aria-disabled'?: boolean | undefined;
  type?: string | undefined;
  disabled?: boolean | undefined;
  tabIndex: number;
}
export interface ButtonBaseExternalProps extends React.HTMLAttributes<any> {
  'aria-disabled'?: boolean | undefined;
  disabled?: boolean | undefined;
  type?: string | undefined;
}
export interface ButtonBaseEventHandlers {
  onClick: React.MouseEventHandler<HTMLElement>;
  onKeyDown: React.KeyboardEventHandler<HTMLElement>;
  onKeyUp: React.KeyboardEventHandler<HTMLElement>;
}
export interface UseButtonBaseReturnValue {
  /**
   * @param externalProps additional props for the button
   * @returns props that should be spread on the button
   */
  getButtonProps: <ExternalProps extends ButtonBaseExternalProps = ButtonBaseExternalProps>(externalProps?: ExternalProps) => Omit<ExternalProps, keyof ButtonBaseEventHandlers> & ButtonBaseButtonProps & ButtonBaseEventHandlers;
  rootRef: React.RefObject<HTMLElement | null>;
}
export default function useButtonBase(parameters: UseButtonBaseParameters): UseButtonBaseReturnValue;