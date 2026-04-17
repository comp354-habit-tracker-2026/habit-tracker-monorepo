import type { CSSObject } from '@mui/styled-engine';
export type StyleFunction<Props> = (props: Props) => any;
export type PropsFor<SomeStyleFunction> = SomeStyleFunction extends StyleFunction<infer Props> ? Props : never;
export type SimpleStyleFunction<PropKey extends keyof any> = StyleFunction<Partial<Record<PropKey, any>>> & {
  filterProps: string[];
};
export type TransformFunction = (cssValue: unknown, userValue: unknown, transform: object | ((arg: any) => any) | undefined | null) => number | string | React.CSSProperties | CSSObject;
export interface StyleOptions<PropKey> {
  cssProperty?: PropKey | keyof React.CSSProperties | false | undefined;
  prop: PropKey;
  /**
   * dot access in `Theme`
   */
  themeKey?: string | undefined;
  transform?: TransformFunction | undefined;
}
/**
 * TODO(v7): Keep either this one or `getStyleValue2`
 */
export declare function getStyleValue(themeMapping: object | ((arg: any) => any) | null | undefined, transform: TransformFunction | null | undefined, valueFinal: unknown, userValue?: unknown): any;
/**
 * HACK: The `alternateProp` logic is there because our theme looks like this:
 * {
 *   typography: {
 *     fontFamily: 'comic sans',
 *     fontFamilyCode: 'courrier new',
 *   }
 * }
 * And we support targetting:
 * - `typography.fontFamily`     with `sx={{ fontFamily: 'default' }}`
 * - `typography.fontFamilyCode` with `sx={{ fontFamily: 'code' }}`
 *
 * TODO(v7): Refactor our theme to look like this and remove the horrendous logic:
 * {
 *   typography: {
 *     fontFamily: {
 *       default: 'comic sans',
 *       code: 'courrier new',
 *     }
 *   }
 * }
 */
export declare function getStyleValue2(themeMapping: object | ((arg: any) => any) | null | undefined, transform: TransformFunction | null | undefined, userValue: unknown, alternateProp: string | undefined): any;
export declare function getPath<T extends Record<string, any> | undefined | null>(obj: T, pathInput: string | undefined, checkVars?: boolean, alternateProp?: string | undefined): null | unknown;
type StyleResult<PropKey extends string | number | symbol, Theme> = StyleFunction<{ [K in PropKey]?: unknown } & {
  theme?: Theme | undefined;
}> & {
  filterProps: string[];
  propTypes: any;
};
export default function style<PropKey extends string, Theme extends object>(options: StyleOptions<PropKey>): StyleResult<PropKey, Theme>;
export {};