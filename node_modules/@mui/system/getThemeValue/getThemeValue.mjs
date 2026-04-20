import borders from "../borders/index.mjs";
import display from "../display/index.mjs";
import flexbox from "../flexbox/index.mjs";
import grid from "../cssGrid/index.mjs";
import positions from "../positions/index.mjs";
import palette from "../palette/index.mjs";
import shadows from "../shadows/index.mjs";
import sizing from "../sizing/index.mjs";
import spacing from "../spacing/index.mjs";
import typography from "../typography/index.mjs";
const filterPropsMapping = {
  borders: borders.filterProps,
  display: display.filterProps,
  flexbox: flexbox.filterProps,
  grid: grid.filterProps,
  positions: positions.filterProps,
  palette: palette.filterProps,
  shadows: shadows.filterProps,
  sizing: sizing.filterProps,
  spacing: spacing.filterProps,
  typography: typography.filterProps
};
export const styleFunctionMapping = {
  borders,
  display,
  flexbox,
  grid,
  positions,
  palette,
  shadows,
  sizing,
  spacing,
  typography
};
export const propToStyleFunction = Object.keys(filterPropsMapping).reduce((acc, styleFnName) => {
  filterPropsMapping[styleFnName].forEach(propName => {
    acc[propName] = styleFunctionMapping[styleFnName];
  });
  return acc;
}, {});
function getThemeValue(prop, value, theme) {
  const inputProps = {
    [prop]: value,
    theme
  };
  const styleFunction = propToStyleFunction[prop];
  return styleFunction ? styleFunction(inputProps) : {
    [prop]: value
  };
}
export default getThemeValue;