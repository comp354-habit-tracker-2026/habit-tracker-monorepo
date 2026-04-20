"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DEFAULT_BREAKPOINTS = void 0;
exports.computeBreakpointsBase = computeBreakpointsBase;
exports.createEmptyBreakpointObject = createEmptyBreakpointObject;
exports.default = void 0;
exports.handleBreakpoints = handleBreakpoints;
exports.hasBreakpoint = hasBreakpoint;
exports.iterateBreakpoints = iterateBreakpoints;
exports.mergeBreakpointsInOrder = mergeBreakpointsInOrder;
exports.removeUnusedBreakpoints = removeUnusedBreakpoints;
exports.resolveBreakpointValues = resolveBreakpointValues;
exports.values = void 0;
var _propTypes = _interopRequireDefault(require("prop-types"));
var _isObjectEmpty = _interopRequireDefault(require("@mui/utils/isObjectEmpty"));
var _fastDeepAssign = _interopRequireDefault(require("@mui/utils/fastDeepAssign"));
var _deepmerge = _interopRequireDefault(require("@mui/utils/deepmerge"));
var _merge = _interopRequireDefault(require("../merge"));
var _cssContainerQueries = require("../cssContainerQueries");
var _createBreakpoints = _interopRequireDefault(require("../createBreakpoints/createBreakpoints"));
const EMPTY_THEME = {};

// The breakpoint **start** at this value.
// For instance with the first breakpoint xs: [xs, sm[.
const values = exports.values = {
  xs: 0,
  // phone
  sm: 600,
  // tablet
  md: 900,
  // small laptop
  lg: 1200,
  // desktop
  xl: 1536 // large screen
};
const DEFAULT_BREAKPOINTS = exports.DEFAULT_BREAKPOINTS = (0, _createBreakpoints.default)({
  values
});
const defaultContainerQueries = {
  containerQueries: containerName => ({
    up: key => {
      let result = typeof key === 'number' ? key : values[key] || key;
      if (typeof result === 'number') {
        result = `${result}px`;
      }
      return containerName ? `@container ${containerName} (min-width:${result})` : `@container (min-width:${result})`;
    }
  })
};
function handleBreakpoints(props, propValue, styleFromPropValue) {
  const result = {};
  return iterateBreakpoints(result, props.theme, propValue, (mediaKey, value, initialKey) => {
    const finalValue = styleFromPropValue(value, initialKey);
    if (mediaKey) {
      result[mediaKey] = finalValue;
    } else {
      (0, _fastDeepAssign.default)(result, finalValue);
    }
  });
}
function iterateBreakpoints(target, theme, propValue, callback) {
  theme ?? (theme = EMPTY_THEME);
  if (Array.isArray(propValue)) {
    const breakpoints = theme.breakpoints ?? DEFAULT_BREAKPOINTS;
    for (let i = 0; i < propValue.length; i += 1) {
      buildBreakpoint(target, breakpoints.up(breakpoints.keys[i]), propValue[i], undefined, callback);
    }
    return target;
  }
  if (typeof propValue === 'object') {
    const breakpoints = theme.breakpoints ?? DEFAULT_BREAKPOINTS;
    const breakpointValues = breakpoints.values ?? values;
    for (const key in propValue) {
      if ((0, _cssContainerQueries.isCqShorthand)(breakpoints.keys, key)) {
        const containerKey = (0, _cssContainerQueries.getContainerQuery)(theme.containerQueries ? theme : defaultContainerQueries, key);
        if (containerKey) {
          buildBreakpoint(target, containerKey, propValue[key], key, callback);
        }
      }
      // key is key
      else if (key in breakpointValues) {
        const mediaKey = breakpoints.up(key);
        buildBreakpoint(target, mediaKey, propValue[key], key, callback);
      } else {
        const cssKey = key;
        target[cssKey] = propValue[cssKey];
      }
    }
    return target;
  }
  callback(undefined, propValue);
  return target;
}
function buildBreakpoint(target, mediaKey, value, initialKey, callback) {
  target[mediaKey] ?? (target[mediaKey] = {});
  callback(mediaKey, value, initialKey);
}
function setupBreakpoints(styleFunction) {
  // eslint-disable-next-line react/function-component-definition
  const newStyleFunction = props => {
    const theme = props.theme || {};
    const base = styleFunction(props);
    const themeBreakpoints = theme.breakpoints || DEFAULT_BREAKPOINTS;
    const extended = themeBreakpoints.keys.reduce((acc, key) => {
      if (props[key]) {
        acc = acc || {};
        acc[themeBreakpoints.up(key)] = styleFunction({
          theme,
          ...props[key]
        });
      }
      return acc;
    }, null);
    return (0, _merge.default)(base, extended);
  };
  newStyleFunction.propTypes = process.env.NODE_ENV !== 'production' ? {
    ...styleFunction.propTypes,
    xs: _propTypes.default.object,
    sm: _propTypes.default.object,
    md: _propTypes.default.object,
    lg: _propTypes.default.object,
    xl: _propTypes.default.object
  } : {};
  newStyleFunction.filterProps = ['xs', 'sm', 'md', 'lg', 'xl', ...styleFunction.filterProps];
  return newStyleFunction;
}
function createEmptyBreakpointObject(breakpoints = DEFAULT_BREAKPOINTS) {
  const {
    internal_mediaKeys: mediaKeys
  } = breakpoints;
  const result = {};
  for (let i = 0; i < mediaKeys.length; i += 1) {
    result[mediaKeys[i]] = {};
  }
  return result;
}
function removeUnusedBreakpoints(breakpoints, style) {
  const breakpointKeys = breakpoints.internal_mediaKeys;
  for (let i = 0; i < breakpointKeys.length; i += 1) {
    const key = breakpointKeys[i];
    if ((0, _isObjectEmpty.default)(style[key])) {
      delete style[key];
    }
  }
  return style;
}
function mergeBreakpointsInOrder(breakpoints, ...styles) {
  const emptyBreakpoints = createEmptyBreakpointObject(breakpoints);
  const mergedOutput = [emptyBreakpoints, ...styles].reduce((prev, next) => (0, _deepmerge.default)(prev, next), {});
  return removeUnusedBreakpoints(breakpoints, mergedOutput);
}

// compute base for responsive values; e.g.,
// [1,2,3] => {xs: true, sm: true, md: true}
// {xs: 1, sm: 2, md: 3} => {xs: true, sm: true, md: true}
function computeBreakpointsBase(breakpointValues, themeBreakpoints) {
  // fixed value
  if (typeof breakpointValues !== 'object') {
    return {};
  }
  const base = {};
  const breakpointsKeys = Object.keys(themeBreakpoints);
  if (Array.isArray(breakpointValues)) {
    breakpointsKeys.forEach((breakpoint, i) => {
      if (i < breakpointValues.length) {
        base[breakpoint] = true;
      }
    });
  } else {
    breakpointsKeys.forEach(breakpoint => {
      if (breakpointValues[breakpoint] != null) {
        base[breakpoint] = true;
      }
    });
  }
  return base;
}
function resolveBreakpointValues({
  values: breakpointValues,
  breakpoints: themeBreakpoints,
  base: customBase
}) {
  const base = customBase || computeBreakpointsBase(breakpointValues, themeBreakpoints);
  const keys = Object.keys(base);
  if (keys.length === 0) {
    return breakpointValues;
  }
  let previous;
  return keys.reduce((acc, breakpoint, i) => {
    if (Array.isArray(breakpointValues)) {
      acc[breakpoint] = breakpointValues[i] != null ? breakpointValues[i] : breakpointValues[previous];
      previous = i;
    } else if (typeof breakpointValues === 'object') {
      acc[breakpoint] = breakpointValues[breakpoint] != null ? breakpointValues[breakpoint] : breakpointValues[previous];
      previous = breakpoint;
    } else {
      acc[breakpoint] = breakpointValues;
    }
    return acc;
  }, {});
}
function hasBreakpoint(breakpoints, value) {
  if (Array.isArray(value)) {
    return true;
  }
  if (typeof value === 'object' && value !== null) {
    for (let i = 0; i < breakpoints.keys.length; i += 1) {
      if (breakpoints.keys[i] in value) {
        return true;
      }
    }
    const valueKeys = Object.keys(value);
    for (let i = 0; i < valueKeys.length; i += 1) {
      if ((0, _cssContainerQueries.isCqShorthand)(breakpoints.keys, valueKeys[i])) {
        return true;
      }
    }
  }
  return false;
}
var _default = exports.default = setupBreakpoints;