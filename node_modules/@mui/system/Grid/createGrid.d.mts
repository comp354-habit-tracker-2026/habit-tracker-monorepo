import * as React from 'react';
import { OverridableComponent } from '@mui/types';
import useThemeSystem from "../useTheme/index.mjs";
import { GridTypeMap } from "./GridProps.mjs";
declare const defaultCreateStyledComponent: import("@mui/styled-engine").CreateStyledComponent<import("../index.mjs").MUIStyledCommonProps<any>, Pick<React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>, keyof React.ClassAttributes<HTMLDivElement> | keyof React.HTMLAttributes<HTMLDivElement>>, {}, any>;
declare function useThemePropsDefault<T extends {}>(props: T): T;
export default function createGrid(options?: {
  createStyledComponent?: typeof defaultCreateStyledComponent | undefined;
  useThemeProps?: typeof useThemePropsDefault | undefined;
  useTheme?: typeof useThemeSystem | undefined;
  componentName?: string | undefined;
}): OverridableComponent<GridTypeMap<{}, "div">>;
export {};