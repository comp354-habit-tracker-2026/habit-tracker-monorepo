import { CSSObject } from '@mui/styled-engine';
import { Breakpoints } from "../createBreakpoints/createBreakpoints.mjs";
import type { Breakpoint, Theme } from "../createTheme/index.mjs";
import { ResponsiveStyleValue } from "../styleFunctionSx/index.mjs";
import { StyleFunction } from "../style/index.mjs";
export const DEFAULT_BREAKPOINTS: Breakpoints;
export interface ResolveBreakpointValuesOptions<T> {
  values: ResponsiveStyleValue<T>;
  breakpoints?: Breakpoints['values'] | undefined;
  base?: Record<string, boolean> | undefined;
}
export function resolveBreakpointValues<T>(options: ResolveBreakpointValuesOptions<T>): Record<string, T>;
export function mergeBreakpointsInOrder(breakpoints: Breakpoints, styles: CSSObject[]): CSSObject;
export function iterateBreakpoints(target: any, theme: Theme, propValue: any, callback: (mediaKey: string | undefined, value: any, initialKey?: string) => any): any;
export function handleBreakpoints<Props>(props: Props, propValue: any, styleFromPropValue: (value: any, breakpoint?: Breakpoint) => any): any;
export function hasBreakpoint(breakpoints: Breakpoints, value: any): boolean;
type DefaultBreakPoints = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * @returns An enhanced stylefunction that considers breakpoints
 */
export default function breakpoints<Props, Breakpoints extends string = DefaultBreakPoints>(styleFunction: StyleFunction<Props>): StyleFunction<Partial<Record<Breakpoints, Props>> & Props>;