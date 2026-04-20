import generateUtilityClasses from '@mui/utils/generateUtilityClasses';
import generateUtilityClass from '@mui/utils/generateUtilityClass';
export function getImageListItemBarUtilityClass(slot) {
  return generateUtilityClass('MuiImageListItemBar', slot);
}
const imageListItemBarClasses = generateUtilityClasses('MuiImageListItemBar', ['root', 'positionBottom', 'positionTop', 'positionBelow', 'actionPositionLeft', 'actionPositionRight', 'titleWrap', 'title', 'subtitle', 'actionIcon']);
export default imageListItemBarClasses;