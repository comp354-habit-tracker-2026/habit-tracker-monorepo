"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _deepmerge = _interopRequireDefault(require("@mui/utils/deepmerge"));
const options = {
  clone: false
};
function merge(acc, item) {
  if (!item) {
    return acc;
  }
  return (0, _deepmerge.default)(acc, item, options);
}
var _default = exports.default = merge;