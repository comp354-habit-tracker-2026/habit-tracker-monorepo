"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.RovingTabIndexContext = void 0;
exports.useRovingTabIndexContext = useRovingTabIndexContext;
var React = _interopRequireWildcard(require("react"));
const RovingTabIndexContext = exports.RovingTabIndexContext = /*#__PURE__*/React.createContext(undefined);
if (process.env.NODE_ENV !== 'production') {
  RovingTabIndexContext.displayName = 'RovingTabIndexContext';
}
function useRovingTabIndexContext() {
  const context = React.useContext(RovingTabIndexContext);
  if (context === undefined) {
    throw new Error('MUI: RovingTabIndexContext is missing. Roving tab index items must be placed within a roving tab index provider.');
  }
  return context;
}