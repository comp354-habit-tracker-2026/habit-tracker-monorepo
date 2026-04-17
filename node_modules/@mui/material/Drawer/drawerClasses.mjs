import generateUtilityClasses from '@mui/utils/generateUtilityClasses';
import generateUtilityClass from '@mui/utils/generateUtilityClass';
export function getDrawerUtilityClass(slot) {
  return generateUtilityClass('MuiDrawer', slot);
}
const drawerClasses = generateUtilityClasses('MuiDrawer', ['root', 'docked', 'paper', 'anchorLeft', 'anchorRight', 'anchorTop', 'anchorBottom', 'modal']);
export default drawerClasses;