/**
 * Re-export the habit query hook so that components can import from
 * a stable, feature-local path rather than reaching into the api/ folder.
 *
 * If additional data-shaping logic is needed, add it here rather than
 * in the component.
 */
export { useHabit } from '../api/get-habit';
