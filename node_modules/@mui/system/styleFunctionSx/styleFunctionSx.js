"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
exports.unstable_createStyleFunctionSx = unstable_createStyleFunctionSx;
var _fastDeepAssign = _interopRequireDefault(require("@mui/utils/fastDeepAssign"));
var _style = require("../style");
var _breakpoints = require("../breakpoints");
var _cssContainerQueries = require("../cssContainerQueries");
var _defaultSxConfig = _interopRequireDefault(require("./defaultSxConfig"));
/* eslint-disable guard-for-in */

const EMPTY_THEME = {};

// eslint-disable-next-line @typescript-eslint/naming-convention
function unstable_createStyleFunctionSx() {
  function styleFunctionSx(props) {
    if (!props.sx) {
      return null;
    }
    const {
      sx,
      theme = EMPTY_THEME,
      nested
    } = props;
    const config = theme.unstable_sxConfig ?? _defaultSxConfig.default;

    // Pass argument without loop allocations
    const wrapper = {
      sx: null,
      theme,
      nested: true
    };
    function process(sxInput) {
      let sxObject = sxInput;
      if (typeof sxInput === 'function') {
        sxObject = sxInput(theme);
      } else if (typeof sxInput !== 'object') {
        // value
        return sxInput;
      }
      if (!sxObject) {
        return null;
      }
      const breakpoints = theme.breakpoints ?? _breakpoints.DEFAULT_BREAKPOINTS;
      const css = (0, _breakpoints.createEmptyBreakpointObject)(breakpoints);
      for (const styleKey in sxObject) {
        const value = callIfFn(sxObject[styleKey], theme);
        if (value === null || value === undefined) {
          continue;
        }
        if (typeof value !== 'object') {
          setThemeValue(css, styleKey, value, theme, config);
          continue;
        }
        if (config[styleKey]) {
          setThemeValue(css, styleKey, value, theme, config);
          continue;
        }
        if ((0, _breakpoints.hasBreakpoint)(breakpoints, value)) {
          (0, _breakpoints.iterateBreakpoints)(css, props.theme, value, (mediaKey, finalValue) => {
            css[mediaKey][styleKey] = finalValue;
          });
        } else {
          wrapper.sx = value;
          css[styleKey] = styleFunctionSx(wrapper);
        }
      }
      if (!nested && theme.modularCssLayers) {
        return {
          '@layer sx': (0, _cssContainerQueries.sortContainerQueries)(theme, (0, _breakpoints.removeUnusedBreakpoints)(breakpoints, css))
        };
      }
      return (0, _cssContainerQueries.sortContainerQueries)(theme, (0, _breakpoints.removeUnusedBreakpoints)(breakpoints, css));
    }
    return Array.isArray(sx) ? sx.map(process) : process(sx);
  }
  styleFunctionSx.filterProps = ['sx'];
  return styleFunctionSx;
}
var _default = exports.default = unstable_createStyleFunctionSx();
function setThemeValue(css, prop, value, theme, config) {
  const options = config[prop];
  if (!options) {
    css[prop] = value;
    return;
  }
  if (value == null) {
    return;
  }
  const {
    themeKey
  } = options;
  // TODO v6: remove, see https://github.com/mui/material-ui/pull/38123
  if (themeKey === 'typography' && value === 'inherit') {
    css[prop] = value;
    return;
  }
  const {
    style
  } = options;
  if (style) {
    (0, _fastDeepAssign.default)(css, style({
      [prop]: value,
      theme
    }));
    return;
  }
  const {
    cssProperty = prop,
    transform
  } = options;
  const themeMapping = (0, _style.getPath)(theme, themeKey);
  (0, _breakpoints.iterateBreakpoints)(css, theme, value, (mediaKey, valueFinal) => {
    const finalValue = (0, _style.getStyleValue2)(themeMapping, transform, valueFinal, prop);
    if (cssProperty === false) {
      if (mediaKey) {
        css[mediaKey] = finalValue;
      } else {
        (0, _fastDeepAssign.default)(css, finalValue);
      }
    } else {
      // eslint-disable-next-line no-lonely-if
      if (mediaKey) {
        css[mediaKey][cssProperty] = finalValue;
      } else {
        css[cssProperty] = finalValue;
      }
    }
  });
}
function callIfFn(maybeFn, arg) {
  return typeof maybeFn === 'function' ? maybeFn(arg) : maybeFn;
}