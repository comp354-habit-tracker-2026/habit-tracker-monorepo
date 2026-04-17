import capitalize from '@mui/utils/capitalize';
import responsivePropType from "../responsivePropType/index.mjs";
import { handleBreakpoints } from "../breakpoints/index.mjs";
/**
 * TODO(v7): Keep either this one or `getStyleValue2`
 */
export function getStyleValue(themeMapping, transform, valueFinal, userValue = valueFinal) {
  let value;
  if (typeof themeMapping === 'function') {
    value = themeMapping(valueFinal);
  } else if (Array.isArray(themeMapping)) {
    value = themeMapping[valueFinal] || userValue;
  } else if (typeof valueFinal === 'string') {
    value = getPath(themeMapping, valueFinal) || userValue;
  } else {
    value = userValue;
  }
  if (transform) {
    value = transform(value, userValue, themeMapping);
  }
  return value;
}

/**
 * HACK: The `alternateProp` logic is there because our theme looks like this:
 * {
 *   typography: {
 *     fontFamily: 'comic sans',
 *     fontFamilyCode: 'courrier new',
 *   }
 * }
 * And we support targetting:
 * - `typography.fontFamily`     with `sx={{ fontFamily: 'default' }}`
 * - `typography.fontFamilyCode` with `sx={{ fontFamily: 'code' }}`
 *
 * TODO(v7): Refactor our theme to look like this and remove the horrendous logic:
 * {
 *   typography: {
 *     fontFamily: {
 *       default: 'comic sans',
 *       code: 'courrier new',
 *     }
 *   }
 * }
 */
export function getStyleValue2(themeMapping, transform, userValue, alternateProp) {
  let value;
  if (typeof themeMapping === 'function') {
    value = themeMapping(userValue);
  } else if (Array.isArray(themeMapping)) {
    value = themeMapping[userValue] || userValue;
  } else if (typeof userValue === 'string') {
    value = getPath(themeMapping, userValue, true, alternateProp) || userValue;
  } else {
    value = userValue;
  }
  if (transform) {
    value = transform(value, userValue, themeMapping);
  }
  return value;
}
export function getPath(obj, pathInput, checkVars = true, alternateProp = undefined) {
  if (!obj || !pathInput) {
    return null;
  }
  const path = pathInput.split('.');

  // Check if CSS variables are used
  if (obj.vars && checkVars) {
    const val = getPathImpl(obj.vars, path, alternateProp);
    if (val != null) {
      return val;
    }
  }
  return getPathImpl(obj, path, alternateProp);
}
function getPathImpl(object, path, alternateProp = undefined) {
  let lastResult = undefined;
  let result = object;
  let index = 0;
  while (index < path.length) {
    if (result === null || result === undefined) {
      return result;
    }
    lastResult = result;
    result = result[path[index]];
    index += 1;
  }
  if (alternateProp && result === undefined) {
    const lastKey = path[path.length - 1];
    const alternateKey = `${alternateProp}${lastKey === 'default' ? '' : capitalize(lastKey)}`;
    return lastResult?.[alternateKey];
  }
  return result;
}
export default function style(options) {
  const {
    prop,
    cssProperty = options.prop,
    themeKey,
    transform
  } = options;

  // eslint-disable-next-line react/function-component-definition
  const fn = props => {
    if (props[prop] == null) {
      return null;
    }
    const propValue = props[prop];
    const theme = props.theme;
    const themeMapping = getPath(theme, themeKey) || {};
    const styleFromPropValue = valueFinal => {
      const value = getStyleValue2(themeMapping, transform, valueFinal, prop);
      return cssProperty === false ? value : {
        [cssProperty]: value
      };
    };
    return handleBreakpoints(props, propValue, styleFromPropValue);
  };
  fn.propTypes = process.env.NODE_ENV !== 'production' ? {
    [prop]: responsivePropType
  } : {};
  fn.filterProps = [prop];
  return fn;
}