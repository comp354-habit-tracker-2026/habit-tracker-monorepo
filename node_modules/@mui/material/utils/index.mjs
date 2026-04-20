'use client';

import ClassNameGenerator from '@mui/utils/ClassNameGenerator';
export { default as capitalize } from "./capitalize.mjs";
export { default as createChainedFunction } from "./createChainedFunction.mjs";
export { default as createSvgIcon } from "./createSvgIcon.mjs";
export { default as debounce } from "./debounce.mjs";
export { default as deprecatedPropType } from "./deprecatedPropType.mjs";
export { default as isMuiElement } from "./isMuiElement.mjs";
export { default as getActiveElement } from "./getActiveElement.mjs";
export { default as unstable_memoTheme } from "./memoTheme.mjs";
export { default as ownerDocument } from "./ownerDocument.mjs";
export { default as ownerWindow } from "./ownerWindow.mjs";
export { default as requirePropFactory } from "./requirePropFactory.mjs";
export { default as setRef } from "./setRef.mjs";
export { default as unstable_useEnhancedEffect } from "./useEnhancedEffect.mjs";
export { default as unstable_useId } from "./useId.mjs";
export { default as unsupportedProp } from "./unsupportedProp.mjs";
export { default as useControlled } from "./useControlled.mjs";
export { default as useEventCallback } from "./useEventCallback.mjs";
export { default as useForkRef } from "./useForkRef.mjs";
export { default as mergeSlotProps } from "./mergeSlotProps.mjs";
// TODO: remove this export once ClassNameGenerator is stable
// eslint-disable-next-line @typescript-eslint/naming-convention
export const unstable_ClassNameGenerator = {
  configure: generator => {
    if (process.env.NODE_ENV !== 'production') {
      console.warn(['MUI: `ClassNameGenerator` import from `@mui/material/utils` is outdated and might cause unexpected issues.', '', "You should use `import { unstable_ClassNameGenerator } from '@mui/material/className'` instead", '', 'The detail of the issue: https://github.com/mui/material-ui/issues/30011#issuecomment-1024993401', '', 'The updated documentation: https://mui.com/guides/classname-generator/'].join('\n'));
    }
    ClassNameGenerator.configure(generator);
  }
};