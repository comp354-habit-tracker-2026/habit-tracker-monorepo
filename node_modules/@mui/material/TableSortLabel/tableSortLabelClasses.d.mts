export interface TableSortLabelClasses {
  /** Styles applied to the root element. */
  root: string;
  /** Styles applied to the root element if `direction="desc"`. */
  directionDesc: string;
  /** Styles applied to the root element if `direction="asc"`. */
  directionAsc: string;
  /** State class applied to the root element if `active={true}`. */
  active: string;
  /** Styles applied to the icon component. */
  icon: string;
}
export type TableSortLabelClassKey = keyof TableSortLabelClasses;
export declare function getTableSortLabelUtilityClass(slot: string): string;
declare const tableSortLabelClasses: TableSortLabelClasses;
export default tableSortLabelClasses;