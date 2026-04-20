'use client';

import * as React from 'react';
const SelectFocusSourceContext = /*#__PURE__*/React.createContext(null);
if (process.env.NODE_ENV !== 'production') {
  SelectFocusSourceContext.displayName = 'SelectFocusSourceContext';
}
function useSelectFocusSource() {
  const context = React.useContext(SelectFocusSourceContext);
  return context;
}
const SelectFocusSourceProvider = SelectFocusSourceContext.Provider;
export { useSelectFocusSource, SelectFocusSourceProvider };