'use client';

import createStyled from '@mui/system/createStyled';
import defaultTheme from "./defaultTheme.mjs";
import THEME_ID from "./identifier.mjs";
import rootShouldForwardProp from "./rootShouldForwardProp.mjs";
export { default as slotShouldForwardProp } from "./slotShouldForwardProp.mjs";
export { default as rootShouldForwardProp } from "./rootShouldForwardProp.mjs";
const styled = createStyled({
  themeId: THEME_ID,
  defaultTheme,
  rootShouldForwardProp
});
export default styled;