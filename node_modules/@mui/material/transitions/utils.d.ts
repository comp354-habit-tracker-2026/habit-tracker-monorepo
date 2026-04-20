import * as React from 'react';
export declare const reflow: (node: Element) => number;
interface ComponentProps {
  easing: string | {
    enter?: string | undefined;
    exit?: string | undefined;
  } | undefined;
  style: React.CSSProperties | undefined;
  timeout: number | {
    enter?: number | undefined;
    exit?: number | undefined;
  };
}
interface Options {
  mode: 'enter' | 'exit';
}
interface TransitionProps {
  duration: string | number;
  easing: string | undefined;
  delay: string | undefined;
}
export declare function normalizedTransitionCallback(nodeRef: React.RefObject<HTMLElement | null>, callback: ((node: HTMLElement, isAppearing?: boolean) => void) | undefined): (maybeIsAppearing?: boolean) => void;
type TransitionState = 'entering' | 'entered' | 'exiting' | 'exited';
/**
 * Computes the child style for a transition component, reusing existing
 * references when possible to preserve referential equality for React.memo.
 */
export declare function getTransitionChildStyle(state: TransitionState, inProp: boolean | undefined, baseStyles: Record<string, React.CSSProperties>, hiddenStyles: React.CSSProperties, styleProp: React.CSSProperties | undefined, childStyle: React.CSSProperties | undefined): React.CSSProperties | undefined;
export declare function getTransitionProps(props: ComponentProps, options: Options): TransitionProps;
export {};