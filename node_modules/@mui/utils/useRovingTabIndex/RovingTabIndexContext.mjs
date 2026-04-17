'use client';

import * as React from 'react';
export const RovingTabIndexContext = /*#__PURE__*/React.createContext(undefined);
if (process.env.NODE_ENV !== 'production') {
  RovingTabIndexContext.displayName = 'RovingTabIndexContext';
}
export function useRovingTabIndexContext() {
  const context = React.useContext(RovingTabIndexContext);
  if (context === undefined) {
    throw new Error('MUI: RovingTabIndexContext is missing. Roving tab index items must be placed within a roving tab index provider.');
  }
  return context;
}