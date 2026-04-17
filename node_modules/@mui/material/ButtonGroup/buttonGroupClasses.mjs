import generateUtilityClasses from '@mui/utils/generateUtilityClasses';
import generateUtilityClass from '@mui/utils/generateUtilityClass';
export function getButtonGroupUtilityClass(slot) {
  return generateUtilityClass('MuiButtonGroup', slot);
}
const buttonGroupClasses = generateUtilityClasses('MuiButtonGroup', ['root', 'contained', 'outlined', 'text', 'disableElevation', 'disabled', 'firstButton', 'fullWidth', 'horizontal', 'vertical', 'colorPrimary', 'colorSecondary', 'grouped', 'lastButton', 'middleButton']);
export default buttonGroupClasses;