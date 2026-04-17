import { RadioGroupContextValue } from "./RadioGroupContext.mjs";
export interface RadioGroupState extends RadioGroupContextValue {}
export default function useRadioGroup(): RadioGroupState | undefined;