import * as React from 'react';
import { OverridableComponent, OverrideProps } from '@mui/types';
import { Theme as SystemTheme } from "../createTheme/index.mjs";
import { SxProps, AllSystemCSSProperties, ResponsiveStyleValue, OverwriteCSSProperties, AliasesCSSProperties } from "../styleFunctionSx/index.mjs";
import { PropsFor } from "../style/index.mjs";
import { ComposedStyleFunction } from "../compose/index.mjs";
import borders from "../borders/index.mjs";
import display from "../display/index.mjs";
import flexbox from "../flexbox/index.mjs";
import grid from "../cssGrid/index.mjs";
import palette from "../palette/index.mjs";
import positions from "../positions/index.mjs";
import shadows from "../shadows/index.mjs";
import sizing from "../sizing/index.mjs";
import spacing from "../spacing/index.mjs";
import typography from "../typography/index.mjs";
export interface CustomSystemProps extends AliasesCSSProperties, OverwriteCSSProperties {}
export type SimpleSystemKeys = keyof PropsFor<ComposedStyleFunction<[typeof borders, typeof display, typeof flexbox, typeof grid, typeof palette, typeof positions, typeof shadows, typeof sizing, typeof spacing, typeof typography]>>;

// The SimpleSystemKeys are subset of the AllSystemCSSProperties, so this should be ok
// This is needed as these are used as keys inside AllSystemCSSProperties
type StandardSystemKeys = Extract<SimpleSystemKeys, keyof AllSystemCSSProperties>;
export type SystemProps<Theme extends object = {}> = { [K in StandardSystemKeys]?: ResponsiveStyleValue<AllSystemCSSProperties[K]> | ((theme: Theme) => ResponsiveStyleValue<AllSystemCSSProperties[K]>) };
export interface BoxOwnProps<Theme extends object = SystemTheme> {
  children?: React.ReactNode;
  ref?: React.Ref<unknown> | undefined;
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx?: SxProps<Theme> | undefined;
}
export interface BoxTypeMap<AdditionalProps = {}, RootComponent extends React.ElementType = 'div', Theme extends object = SystemTheme> {
  props: AdditionalProps & BoxOwnProps<Theme>;
  defaultComponent: RootComponent;
}

/**
 *
 * Demos:
 *
 * - [Box (Material UI)](https://mui.com/material-ui/react-box/)
 * - [Menubar (Material UI)](https://mui.com/material-ui/react-menubar/)
 * - [Box (MUI System)](https://mui.com/system/react-box/)
 *
 * API:
 *
 * - [Box API](https://mui.com/system/api/box/)
 */
declare const Box: OverridableComponent<BoxTypeMap>;
export type BoxProps<RootComponent extends React.ElementType = BoxTypeMap['defaultComponent'], AdditionalProps = {}> = OverrideProps<BoxTypeMap<AdditionalProps, RootComponent>, RootComponent> & {
  component?: React.ElementType | undefined;
};
export default Box;