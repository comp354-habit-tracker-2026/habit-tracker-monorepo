import { PropsFor, SimpleStyleFunction } from "../style/index.mjs";
declare const shadows: SimpleStyleFunction<'boxShadow'>;
export type ShadowsProps = PropsFor<typeof shadows>;
export default shadows;