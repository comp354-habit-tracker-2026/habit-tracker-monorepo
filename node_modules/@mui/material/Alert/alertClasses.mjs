import generateUtilityClasses from '@mui/utils/generateUtilityClasses';
import generateUtilityClass from '@mui/utils/generateUtilityClass';
export function getAlertUtilityClass(slot) {
  return generateUtilityClass('MuiAlert', slot);
}
const alertClasses = generateUtilityClasses('MuiAlert', ['root', 'action', 'icon', 'message', 'filled', 'colorSuccess', 'colorInfo', 'colorWarning', 'colorError', 'outlined', 'standard']);
export default alertClasses;