import * as React from 'react';
declare function useSelectFocusSource(): "touch" | "mouse" | "keyboard" | null;
declare const SelectFocusSourceProvider: React.Provider<"touch" | "mouse" | "keyboard" | null>;
export { useSelectFocusSource, SelectFocusSourceProvider };