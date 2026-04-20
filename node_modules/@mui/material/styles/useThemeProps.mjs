'use client';

import systemUseThemeProps from '@mui/system/useThemeProps';
import defaultTheme from "./defaultTheme.mjs";
import THEME_ID from "./identifier.mjs";
export default function useThemeProps({
  props,
  name
}) {
  return systemUseThemeProps({
    props,
    name,
    defaultTheme,
    themeId: THEME_ID
  });
}