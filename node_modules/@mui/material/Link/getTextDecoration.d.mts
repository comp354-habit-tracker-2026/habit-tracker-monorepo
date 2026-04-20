import type { Theme } from "../styles/index.mjs";
declare const getTextDecoration: <T extends Theme>({
  theme,
  ownerState
}: {
  theme: T;
  ownerState: {
    color: string;
  };
}) => string;
export default getTextDecoration;