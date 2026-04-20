import { DistributiveOmit } from '@mui/types';
export { default as THEME_ID } from "./identifier.mjs";
export { default as createTheme, default as unstable_createMuiStrictModeTheme, ThemeOptions, Theme, CssThemeVariables } from "./createTheme.mjs";
export { default as adaptV4Theme, DeprecatedThemeOptions } from "./adaptV4Theme.mjs";
export { Shadows } from "./shadows.mjs";
export { ZIndex } from "./zIndex.mjs";
export { CommonColors, Palette, PaletteColor, PaletteColorOptions, PaletteOptions, SimplePaletteColorOptions, TypeText, TypeAction, TypeBackground, PaletteMode, Color } from "./createPalette.mjs";
export { default as createColorScheme } from "./createColorScheme.mjs";
export { default as createStyles } from "./createStyles.mjs";
export { TypographyVariants, TypographyVariantsOptions, TypographyStyle, TypographyVariant } from "./createTypography.mjs";
export { default as responsiveFontSizes } from "./responsiveFontSizes.mjs";
export { Duration, Easing, Transitions, TransitionsOptions, duration, easing } from "./createTransitions.mjs";
export { Mixins, CSSProperties, MixinsOptions } from "./createMixins.mjs";
export { Direction, Breakpoint, BreakpointOverrides, Breakpoints, BreakpointsOptions, CreateMUIStyled, Interpolation, CSSInterpolation, CSSObject, css, keyframes,
// color manipulators
hexToRgb, rgbToHex, hslToRgb, decomposeColor, recomposeColor, getContrastRatio, getLuminance, emphasize, alpha, darken, lighten, ColorFormat, ColorObject, StyledEngineProvider, SxProps } from '@mui/system';
export { unstable_createBreakpoints } from '@mui/system/createBreakpoints';
// TODO: Remove this function in v6.
// eslint-disable-next-line @typescript-eslint/naming-convention
export function experimental_sx(): any;
export { default as useTheme } from "./useTheme.mjs";
export { default as useThemeProps } from "./useThemeProps.mjs";
export * from "./useThemeProps.mjs";
export { default as styled } from "./styled.mjs";
export { default as ThemeProvider, ThemeProviderProps } from "./ThemeProvider.mjs";
export { ComponentsProps, ComponentsPropsList } from "./props.mjs";
export { ComponentsVariants } from "./variants.mjs";
export { ComponentsOverrides, ComponentNameToClassKey } from "./overrides.mjs";
export { Components } from "./components.mjs";
export { getUnit as unstable_getUnit, toUnitless as unstable_toUnitless } from "./cssUtils.mjs";
export type ClassNameMap<ClassKey extends string = string> = Record<ClassKey, string>;
export interface StyledComponentProps<ClassKey extends string = string> {
  /**
   * Override or extend the styles applied to the component.
   */
  classes?: Partial<ClassNameMap<ClassKey>> | undefined;
}

/**
 * All standard components exposed by `material-ui` are `StyledComponents` with
 * certain `classes`, on which one can also set a top-level `className` and inline
 * `style`.
 * @deprecated will be removed in v5 for internal usage only
 */
export type StandardProps<ComponentProps, ClassKey extends string, Removals extends keyof ComponentProps = never> = DistributiveOmit<ComponentProps, 'classes' | Removals> & StyledComponentProps<ClassKey> & {
  className?: string | undefined;
  ref?: (ComponentProps extends {
    ref?: infer RefType | undefined;
  } ? RefType : React.Ref<unknown>) | undefined;
  style?: React.CSSProperties | undefined;
};
export namespace PropTypes {
  // keeping the type structure for backwards compat
  type Color = 'inherit' | 'primary' | 'secondary' | 'default';
}
export { default as makeStyles } from "./makeStyles.mjs";
export { default as withStyles } from "./withStyles.mjs";
export { default as withTheme } from "./withTheme.mjs";
export * from "./ThemeProviderWithVars.mjs";
export type { StorageManager } from '@mui/system/cssVars';
export { default as extendTheme } from "./createThemeWithVars.mjs";
export type { ColorSchemeOverrides, SupportedColorScheme, ColorSystem, CssVarsPalette, Opacity, Overlays, PaletteAlert, PaletteActionChannel, PaletteAppBar, PaletteAvatar, PaletteChip, PaletteColorChannel, PaletteCommonChannel, PaletteFilledInput, PaletteLinearProgress, PaletteSkeleton, PaletteSlider, PaletteSnackbarContent, PaletteSpeedDialAction, PaletteStepConnector, PaletteStepContent, PaletteSwitch, PaletteTableCell, PaletteTextChannel, PaletteTooltip, CssVarsThemeOptions, CssVarsTheme, ThemeVars, ThemeCssVar, ThemeCssVarOverrides, ColorSystemOptions, Shape, ShapeOptions } from "./createThemeWithVars.mjs";
export { default as getOverlayAlpha } from "./getOverlayAlpha.mjs";
export { default as shouldSkipGeneratingVar } from "./shouldSkipGeneratingVar.mjs";

// Private methods for creating parts of the theme
export { default as private_createTypography } from "./createTypography.mjs";
export { default as private_excludeVariablesFromRoot } from "./excludeVariablesFromRoot.mjs";