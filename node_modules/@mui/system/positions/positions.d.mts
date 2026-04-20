import { PropsFor, SimpleStyleFunction } from "../style/index.mjs";
declare const positions: SimpleStyleFunction<'zIndex' | 'position' | 'top' | 'right' | 'bottom' | 'left'>;
export type PositionsProps = PropsFor<typeof positions>;
export default positions;