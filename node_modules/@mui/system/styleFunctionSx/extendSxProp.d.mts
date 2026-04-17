import { SxProps } from "./styleFunctionSx.mjs";
export default function extendSxProp<Props extends {
  sx?: SxProps<any> | undefined;
} = {}>(props: Props): Props;