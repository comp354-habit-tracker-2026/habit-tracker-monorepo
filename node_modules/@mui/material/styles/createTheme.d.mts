import { PaletteOptions } from "./createPalette.mjs";
import { ColorSystemOptions } from "./createThemeFoundation.mjs";
import { CssVarsThemeOptions } from "./createThemeWithVars.mjs";
import { Theme, CssThemeVariables } from "./createThemeNoVars.mjs";
export type { Theme, CssThemeVariables } from "./createThemeNoVars.mjs";
type CssVarsOptions = CssThemeVariables extends {
  enabled: true;
} ? ColorSystemOptions : {};
type CssVarsConfigList = 'colorSchemeSelector' | 'rootSelector' | 'disableCssColorScheme' | 'cssVarPrefix' | 'shouldSkipGeneratingVar' | 'nativeColor';
export interface ThemeOptions extends CssVarsOptions, Omit<CssVarsThemeOptions, CssVarsConfigList> {
  cssVariables?: boolean | Pick<CssVarsThemeOptions, CssVarsConfigList> | undefined;
  palette?: PaletteOptions | undefined;
}
/**
 * Generate a theme base on the options received.
 * @param options Takes an incomplete theme object and adds the missing parts.
 * @param args Deep merge the arguments with the about to be returned theme.
 * @returns A complete, ready-to-use theme object.
 */
export default function createTheme(options?: ThemeOptions,
// cast type to skip module augmentation test
...args: object[]): Theme;