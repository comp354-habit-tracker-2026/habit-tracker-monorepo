import slotShouldForwardProp from "./slotShouldForwardProp.mjs";
const rootShouldForwardProp = prop => slotShouldForwardProp(prop) && prop !== 'classes';
export default rootShouldForwardProp;