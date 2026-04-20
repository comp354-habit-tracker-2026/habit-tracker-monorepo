import * as React from 'react';
import type { UseRovingTabIndexReturnValue } from "./useRovingTabIndex.mjs";
type RovingTabIndexContextValue = UseRovingTabIndexReturnValue<unknown>;
export declare const RovingTabIndexContext: React.Context<RovingTabIndexContextValue | undefined>;
export declare function useRovingTabIndexContext(): RovingTabIndexContextValue;
export {};