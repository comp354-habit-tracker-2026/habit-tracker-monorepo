'use client';

import getThemeProps from "./getThemeProps.mjs";
import useTheme from "../useTheme/index.mjs";
export default function useThemeProps({
  props,
  name,
  defaultTheme,
  themeId
}) {
  let theme = useTheme(defaultTheme);
  if (themeId) {
    theme = theme[themeId] || theme;
  }
  return getThemeProps({
    theme,
    name,
    props
  });
}