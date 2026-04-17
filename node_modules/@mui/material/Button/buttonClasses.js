"use strict";

var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
exports.getButtonUtilityClass = getButtonUtilityClass;
var _generateUtilityClasses = _interopRequireDefault(require("@mui/utils/generateUtilityClasses"));
var _generateUtilityClass = _interopRequireDefault(require("@mui/utils/generateUtilityClass"));
function getButtonUtilityClass(slot) {
  return (0, _generateUtilityClass.default)('MuiButton', slot);
}
const buttonClasses = (0, _generateUtilityClasses.default)('MuiButton', ['root', 'text', 'outlined', 'contained', 'disableElevation', 'focusVisible', 'disabled', 'colorInherit', 'colorPrimary', 'colorSecondary', 'colorSuccess', 'colorError', 'colorInfo', 'colorWarning', 'sizeMedium', 'sizeSmall', 'sizeLarge', 'fullWidth', 'startIcon', 'endIcon', 'icon', 'loading', 'loadingWrapper', 'loadingIconPlaceholder', 'loadingIndicator', 'loadingPositionCenter', 'loadingPositionStart', 'loadingPositionEnd']);
var _default = exports.default = buttonClasses;