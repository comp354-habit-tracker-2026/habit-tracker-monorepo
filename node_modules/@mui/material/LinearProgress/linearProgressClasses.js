"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
exports.getLinearProgressUtilityClass = getLinearProgressUtilityClass;
var _generateUtilityClasses = _interopRequireDefault(require("@mui/utils/generateUtilityClasses"));
var _generateUtilityClass = _interopRequireDefault(require("@mui/utils/generateUtilityClass"));
function getLinearProgressUtilityClass(slot) {
  return (0, _generateUtilityClass.default)('MuiLinearProgress', slot);
}
const linearProgressClasses = (0, _generateUtilityClasses.default)('MuiLinearProgress', ['root', 'colorPrimary', 'colorSecondary', 'determinate', 'indeterminate', 'buffer', 'query', 'dashed', 'bar', 'bar1', 'bar2']);
var _default = exports.default = linearProgressClasses;