export interface ListItemClasses {
  /** Styles applied to the root element. */
  root: string;
  /** Styles applied to the component element if dense. */
  dense: string;
  /** Styles applied to the component element if `alignItems="flex-start"`. */
  alignItemsFlexStart: string;
  /** Styles applied to the inner `component` element if `divider={true}`. */
  divider: string;
  /** Styles applied to the inner `component` element unless `disableGutters={true}`. */
  gutters: string;
  /** Styles applied to the root element unless `disablePadding={true}`. */
  padding: string;
  /** Styles applied to the secondary action element. */
  secondaryAction: string;
}
export type ListItemClassKey = keyof ListItemClasses;
export declare function getListItemUtilityClass(slot: string): string;
declare const listItemClasses: ListItemClasses;
export default listItemClasses;