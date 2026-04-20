import { Breakpoints } from "../createBreakpoints/createBreakpoints.mjs";
import { Spacing } from "../createTheme/createSpacing.mjs";
import { ResponsiveStyleValue } from "../styleFunctionSx/index.mjs";
import { GridDirection, GridOwnerState } from "./GridProps.mjs";
interface Props {
  theme: {
    breakpoints: Breakpoints;
    spacing?: Spacing | undefined;
  };
  ownerState: GridOwnerState;
}
export declare const generateGridSizeStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridOffsetStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridColumnsStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridRowSpacingStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridColumnSpacingStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridDirectionStyles: ({
  theme,
  ownerState
}: Props) => {};
export declare const generateGridStyles: ({
  ownerState
}: Props) => {};
export declare const generateSizeClassNames: (size: GridOwnerState["size"]) => string[];
export declare const generateSpacingClassNames: (spacing: GridOwnerState["spacing"], smallestBreakpoint?: string) => string[];
export declare const generateDirectionClasses: (direction: ResponsiveStyleValue<GridDirection> | undefined) => string[];
export {};