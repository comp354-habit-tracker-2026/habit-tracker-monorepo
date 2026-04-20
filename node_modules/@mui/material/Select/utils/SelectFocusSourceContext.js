"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.SelectFocusSourceProvider = void 0;
exports.useSelectFocusSource = useSelectFocusSource;
var React = _interopRequireWildcard(require("react"));
const SelectFocusSourceContext = /*#__PURE__*/React.createContext(null);
if (process.env.NODE_ENV !== 'production') {
  SelectFocusSourceContext.displayName = 'SelectFocusSourceContext';
}
function useSelectFocusSource() {
  const context = React.useContext(SelectFocusSourceContext);
  return context;
}
const SelectFocusSourceProvider = exports.SelectFocusSourceProvider = SelectFocusSourceContext.Provider;