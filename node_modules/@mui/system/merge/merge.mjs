import deepmerge from '@mui/utils/deepmerge';
const options = {
  clone: false
};
function merge(acc, item) {
  if (!item) {
    return acc;
  }
  return deepmerge(acc, item, options);
}
export default merge;