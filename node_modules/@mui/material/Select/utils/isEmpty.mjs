export default function isEmpty(display) {
  return display == null || typeof display === 'string' && !display.trim();
}