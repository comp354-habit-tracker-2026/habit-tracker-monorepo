import { Interpolation } from '@mui/system';
import { extendSxProp } from '@mui/system/styleFunctionSx';
import { Theme } from "../styles/createTheme.mjs";
import useTheme from "../styles/useTheme.mjs";
export { css, keyframes } from '@mui/system';
export { default as styled } from "../styles/styled.mjs";
export declare function globalCss(styles: Interpolation<{
  theme: Theme;
}>): (props: Record<string, any>) => import("react/jsx-runtime").JSX.Element;
export declare function internal_createExtendSxProp(): typeof extendSxProp;
export { useTheme };