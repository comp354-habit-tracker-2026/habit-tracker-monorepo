"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.MenuListContext = void 0;
exports.useMenuListContext = useMenuListContext;
var React = _interopRequireWildcard(require("react"));
/**
 * @ignore - internal component.
 */

const MenuListContext = exports.MenuListContext = /*#__PURE__*/React.createContext(undefined);
if (process.env.NODE_ENV !== 'production') {
  MenuListContext.displayName = 'MenuListContext';
}
function useMenuListContext() {
  const context = React.useContext(MenuListContext);
  if (context === undefined) {
    throw new Error('MUI: MenuListContext is missing. MenuItems must be placed within Menu or MenuList.');
  }
  return context;
}