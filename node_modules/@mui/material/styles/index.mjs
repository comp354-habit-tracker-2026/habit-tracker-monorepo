import _formatErrorMessage from "@mui/utils/formatMuiErrorMessage";
export { default as THEME_ID } from "./identifier.mjs";
export { default as adaptV4Theme } from "./adaptV4Theme.mjs";
export { hexToRgb, rgbToHex, hslToRgb, decomposeColor, recomposeColor, getContrastRatio, getLuminance, emphasize, alpha, darken, lighten, css, keyframes } from '@mui/system';
export { unstable_createBreakpoints } from '@mui/system/createBreakpoints';
// TODO: Remove this function in v6.
// eslint-disable-next-line @typescript-eslint/naming-convention
export function experimental_sx() {
  throw new Error(process.env.NODE_ENV !== "production" ? 'MUI: The `experimental_sx` has been moved to `theme.unstable_sx`.' + 'For more details, see https://github.com/mui/material-ui/pull/35150.' : _formatErrorMessage(19));
}
export { default as createTheme } from "./createTheme.mjs";
export { default as unstable_createMuiStrictModeTheme } from "./createMuiStrictModeTheme.mjs";
export { default as createStyles } from "./createStyles.mjs";
export { getUnit as unstable_getUnit, toUnitless as unstable_toUnitless } from "./cssUtils.mjs";
export { default as responsiveFontSizes } from "./responsiveFontSizes.mjs";
export { default as createTransitions, duration, easing } from "./createTransitions.mjs";
export { default as createColorScheme } from "./createColorScheme.mjs";
export { default as useTheme } from "./useTheme.mjs";
export { default as useThemeProps } from "./useThemeProps.mjs";
export { default as styled } from "./styled.mjs";
export { default as ThemeProvider } from "./ThemeProvider.mjs";
export { StyledEngineProvider } from '@mui/system';
// The legacy utilities from @mui/styles
// These are just empty functions that throws when invoked
export { default as makeStyles } from "./makeStyles.mjs";
export { default as withStyles } from "./withStyles.mjs";
export { default as withTheme } from "./withTheme.mjs";
export * from "./ThemeProviderWithVars.mjs";
export { default as extendTheme } from "./createThemeWithVars.mjs";
export { default as experimental_extendTheme } from "./experimental_extendTheme.mjs"; // TODO: Remove in v7
export { default as getOverlayAlpha } from "./getOverlayAlpha.mjs";
export { default as shouldSkipGeneratingVar } from "./shouldSkipGeneratingVar.mjs";

// Private methods for creating parts of the theme
export { default as private_createTypography } from "./createTypography.mjs";
export { default as private_createMixins } from "./createMixins.mjs";
export { default as private_excludeVariablesFromRoot } from "./excludeVariablesFromRoot.mjs";