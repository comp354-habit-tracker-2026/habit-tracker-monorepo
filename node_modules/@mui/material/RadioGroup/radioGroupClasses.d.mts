import { FormGroupClasses } from "../FormGroup/index.mjs";
export type RadioGroupClassKey = keyof FormGroupClasses;
export type RadioGroupClasses = FormGroupClasses;
export declare function getRadioGroupUtilityClass(slot: string): string;
declare const radioGroupClasses: RadioGroupClasses;
export default radioGroupClasses;