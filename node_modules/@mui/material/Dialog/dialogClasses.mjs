import generateUtilityClasses from '@mui/utils/generateUtilityClasses';
import generateUtilityClass from '@mui/utils/generateUtilityClass';
export function getDialogUtilityClass(slot) {
  return generateUtilityClass('MuiDialog', slot);
}
const dialogClasses = generateUtilityClasses('MuiDialog', ['root', 'backdrop', 'scrollPaper', 'scrollBody', 'container', 'paper', 'paperWidthFalse', 'paperWidthXs', 'paperWidthSm', 'paperWidthMd', 'paperWidthLg', 'paperWidthXl', 'paperFullWidth', 'paperFullScreen']);
export default dialogClasses;