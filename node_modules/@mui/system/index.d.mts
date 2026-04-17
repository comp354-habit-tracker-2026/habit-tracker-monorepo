// disable automatic export
export {};
export * from "./borders/index.mjs";
export { default as borders } from "./borders/index.mjs";
export { default as breakpoints, handleBreakpoints, mergeBreakpointsInOrder } from "./breakpoints/index.mjs";
export { default as cssContainerQueries, type CssContainerQueries } from "./cssContainerQueries/index.mjs";
export { default as compose } from "./compose/index.mjs";
export * from "./display/index.mjs";
export { default as display } from "./display/index.mjs";
export * from "./flexbox/index.mjs";
export { default as flexbox } from "./flexbox/index.mjs";
export * from "./cssGrid/index.mjs";
export { default as grid } from "./cssGrid/index.mjs";
export * from "./palette/index.mjs";
export { default as palette } from "./palette/index.mjs";
export * from "./positions/index.mjs";
export { default as positions } from "./positions/index.mjs";
export * from "./shadows/index.mjs";
export { default as shadows } from "./shadows/index.mjs";
export * from "./sizing/index.mjs";
export { default as sizing } from "./sizing/index.mjs";
export * from "./typography/index.mjs";
export { default as typography } from "./typography/index.mjs";
export { default as unstable_getThemeValue } from "./getThemeValue/index.mjs";

/**
 * The `css` function accepts arrays as values for mobile-first responsive styles.
 * Note that this extends to non-theme values also. For example `display=['none', 'block']`
 * will also works.
 */
export type ResponsiveStyleValue<T> = T | Array<T | null> | {
  [key: string]: T | null;
};
export { DefaultTheme } from '@mui/private-theming';
export { css, keyframes, StyledEngineProvider, Interpolation, CSSInterpolation, CSSObject } from '@mui/styled-engine';
export { default as GlobalStyles } from "./GlobalStyles/index.mjs";
export type { GlobalStylesProps } from "./GlobalStyles/index.mjs";
export * from "./style/index.mjs";
export { default as style } from "./style/index.mjs";
export * from "./spacing/index.mjs";
export { default as spacing } from "./spacing/index.mjs";
export { default as unstable_styleFunctionSx, unstable_createStyleFunctionSx, extendSxProp as unstable_extendSxProp, unstable_defaultSxConfig } from "./styleFunctionSx/index.mjs";
export * from "./styleFunctionSx/index.mjs";

// TODO: Remove this function in v6.
// eslint-disable-next-line @typescript-eslint/naming-convention
export function experimental_sx(): any;
export { default as Box } from "./Box/index.mjs";
export * from "./Box/index.mjs";
export { default as createBox } from "./createBox/index.mjs";
export * from "./createBox/index.mjs";
export { default as createStyled } from "./createStyled/index.mjs";
export * from "./createStyled/index.mjs";
export { default as styled } from "./styled/index.mjs";
export * from "./styled/index.mjs";
export { default as createTheme } from "./createTheme/index.mjs";
export * from "./createTheme/index.mjs";
export { default as createBreakpoints } from "./createBreakpoints/createBreakpoints.mjs";
export * from "./createBreakpoints/createBreakpoints.mjs";
export { default as createSpacing } from "./createTheme/createSpacing.mjs";
export { SpacingOptions, Spacing } from "./createTheme/createSpacing.mjs";
export { default as shape } from "./createTheme/shape.mjs";
export * from "./createTheme/shape.mjs";
export { default as useThemeProps, getThemeProps } from "./useThemeProps/index.mjs";
export { default as useTheme } from "./useTheme/index.mjs";
export * from "./useTheme/index.mjs";
export { default as useThemeWithoutDefault } from "./useThemeWithoutDefault/index.mjs";
export * from "./useThemeWithoutDefault/index.mjs";
export { default as useMediaQuery } from "./useMediaQuery/index.mjs";
export * from "./useMediaQuery/index.mjs";
export * from "./colorManipulator/index.mjs";
export { default as ThemeProvider } from "./ThemeProvider/index.mjs";
export * from "./ThemeProvider/index.mjs";
export { default as unstable_memoTheme } from "./memoTheme.mjs";
export { default as unstable_createCssVarsProvider, CreateCssVarsProviderResult } from "./cssVars/index.mjs";
export { default as unstable_createGetCssVar } from "./cssVars/createGetCssVar.mjs";
export { default as unstable_cssVarsParser } from "./cssVars/cssVarsParser.mjs";
export { default as unstable_prepareCssVars } from "./cssVars/prepareCssVars.mjs";
export { default as unstable_createCssVarsTheme } from "./cssVars/createCssVarsTheme.mjs";
export * from "./cssVars/index.mjs";
export { default as responsivePropType } from "./responsivePropType/index.mjs";
export { default as createContainer } from "./Container/createContainer.mjs";
export * from "./Container/createContainer.mjs";
export { default as Container } from "./Container/index.mjs";
export * from "./Container/index.mjs";
export { default as Grid } from "./Grid/index.mjs";
export * from "./Grid/index.mjs";
export { default as Stack } from "./Stack/index.mjs";
export * from "./Stack/index.mjs";
export * from "./version/index.mjs";