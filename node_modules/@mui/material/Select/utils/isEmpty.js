"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = isEmpty;
function isEmpty(display) {
  return display == null || typeof display === 'string' && !display.trim();
}