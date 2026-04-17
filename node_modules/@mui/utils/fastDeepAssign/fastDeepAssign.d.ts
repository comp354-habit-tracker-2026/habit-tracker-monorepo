/**
 * Assigns props from one object to another. Focused on performance, only normal objects with no
 * prototype are supported.
 */
export default function fastDeepAssign<T extends Record<string, any>>(target: T, source: any): any;