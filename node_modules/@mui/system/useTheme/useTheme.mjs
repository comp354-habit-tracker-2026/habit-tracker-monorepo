'use client';

import createTheme from "../createTheme/index.mjs";
import useThemeWithoutDefault from "../useThemeWithoutDefault/index.mjs";
export const systemDefaultTheme = createTheme();
function useTheme(defaultTheme = systemDefaultTheme) {
  return useThemeWithoutDefault(defaultTheme);
}
export default useTheme;