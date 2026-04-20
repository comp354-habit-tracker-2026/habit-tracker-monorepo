/**
 * @mui/system v9.0.0
 *
 * @license MIT
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import _formatErrorMessage from "@mui/utils/formatMuiErrorMessage";
export { css, keyframes, StyledEngineProvider } from '@mui/styled-engine';
export { default as GlobalStyles } from "./GlobalStyles/index.mjs";
export { default as borders } from "./borders/index.mjs";
export * from "./borders/index.mjs";
export { default as breakpoints } from "./breakpoints/index.mjs";
export { default as cssContainerQueries } from "./cssContainerQueries/index.mjs";
export { handleBreakpoints, mergeBreakpointsInOrder, resolveBreakpointValues as unstable_resolveBreakpointValues } from "./breakpoints/index.mjs";
export { default as compose } from "./compose/index.mjs";
export { default as display } from "./display/index.mjs";
export { default as flexbox } from "./flexbox/index.mjs";
export * from "./flexbox/index.mjs";
export { default as grid } from "./cssGrid/index.mjs";
export * from "./cssGrid/index.mjs";
export { default as palette } from "./palette/index.mjs";
export * from "./palette/index.mjs";
export { default as positions } from "./positions/index.mjs";
export * from "./positions/index.mjs";
export { default as shadows } from "./shadows/index.mjs";
export { default as sizing } from "./sizing/index.mjs";
export * from "./sizing/index.mjs";
export { default as spacing } from "./spacing/index.mjs";
export * from "./spacing/index.mjs";
export { default as style, getPath, getStyleValue } from "./style/index.mjs";
export { default as typography } from "./typography/index.mjs";
export * from "./typography/index.mjs";
export { default as unstable_styleFunctionSx, unstable_createStyleFunctionSx, extendSxProp as unstable_extendSxProp, unstable_defaultSxConfig } from "./styleFunctionSx/index.mjs";
// TODO: Remove this function in v6
// eslint-disable-next-line @typescript-eslint/naming-convention
export function experimental_sx() {
  throw new Error(process.env.NODE_ENV !== "production" ? 'MUI: The `experimental_sx` has been moved to `theme.unstable_sx`.' + 'For more details, see https://github.com/mui/material-ui/pull/35150.' : _formatErrorMessage(19));
}
export { default as unstable_getThemeValue } from "./getThemeValue/index.mjs";
export { default as Box } from "./Box/index.mjs";
export * from "./Box/index.mjs";
export { default as createBox } from "./createBox/index.mjs";
export { default as createStyled } from "./createStyled/index.mjs";
export * from "./createStyled/index.mjs";
export { default as styled } from "./styled/index.mjs";
export { default as createTheme } from "./createTheme/index.mjs";
export { default as createBreakpoints } from "./createBreakpoints/createBreakpoints.mjs";
export { default as createSpacing } from "./createTheme/createSpacing.mjs";
export { default as shape } from "./createTheme/shape.mjs";
export { default as useThemeProps, getThemeProps } from "./useThemeProps/index.mjs";
export { default as useTheme } from "./useTheme/index.mjs";
export { default as useThemeWithoutDefault } from "./useThemeWithoutDefault/index.mjs";
export { default as useMediaQuery } from "./useMediaQuery/index.mjs";
export * from "./colorManipulator/index.mjs";
export { default as ThemeProvider } from "./ThemeProvider/index.mjs";
export { default as unstable_memoTheme } from "./memoTheme.mjs";
export { default as unstable_createCssVarsProvider } from "./cssVars/createCssVarsProvider.mjs";
export { default as unstable_createGetCssVar } from "./cssVars/createGetCssVar.mjs";
export { default as unstable_cssVarsParser } from "./cssVars/cssVarsParser.mjs";
export { default as unstable_prepareCssVars } from "./cssVars/prepareCssVars.mjs";
export { default as unstable_createCssVarsTheme } from "./cssVars/createCssVarsTheme.mjs";
export { default as responsivePropType } from "./responsivePropType/index.mjs";
export { default as RtlProvider } from "./RtlProvider/index.mjs";
export * from "./RtlProvider/index.mjs";
export * from "./version/index.mjs";

/** ----------------- */
/** Layout components */
export { default as createContainer } from "./Container/createContainer.mjs";
export { default as Container } from "./Container/index.mjs";
export * from "./Container/index.mjs";
export { default as Grid } from "./Grid/Grid.mjs";
export * from "./Grid/index.mjs";
export { default as Stack } from "./Stack/Stack.mjs";
export * from "./Stack/index.mjs";