"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _fastDeepAssign = _interopRequireDefault(require("@mui/utils/fastDeepAssign"));
function compose(...styles) {
  const handlers = styles.reduce((acc, style) => {
    style.filterProps.forEach(prop => {
      acc[prop] = style;
    });
    return acc;
  }, {});

  // eslint-disable-next-line react/function-component-definition
  const fn = props => {
    const result = {};
    for (const prop in props) {
      if (handlers[prop]) {
        (0, _fastDeepAssign.default)(result, handlers[prop](props));
      }
    }
    return result;
  };
  fn.propTypes = process.env.NODE_ENV !== 'production' ? styles.reduce((acc, style) => Object.assign(acc, style.propTypes), {}) : {};
  fn.filterProps = styles.reduce((acc, style) => acc.concat(style.filterProps), []);
  return fn;
}
var _default = exports.default = compose;