export default function getOpenInteractionType(event) {
  if (!event) {
    return null;
  }
  if (event.type === 'mousedown' || event.type === 'pointerdown' || event.type === 'touchstart') {
    return 'pointer';
  }
  if (event.type === 'keydown' || event.type === 'click' && event.detail === 0) {
    return 'keyboard';
  }
  return null;
}