/**
 * Fast shallow compare for plain objects.
 * Returns `true` when both objects have the same own enumerable keys and each value is equal
 * according to `Object.is()`.
 */
export default function fastObjectShallowCompare<T extends Record<string, any> | null>(a: T, b: T): boolean;