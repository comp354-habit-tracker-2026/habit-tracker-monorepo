"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = areEqualValues;
function areEqualValues(a, b) {
  if (typeof b === 'object' && b !== null) {
    return a === b;
  }

  // The value could be a number, the DOM will stringify it anyway.
  return String(a) === String(b);
}