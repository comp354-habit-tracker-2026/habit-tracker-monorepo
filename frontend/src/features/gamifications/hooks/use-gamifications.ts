//copy from habits.hooks.use-habits

/**
 * Re-export the gamifications query hook so that components can import from
 * a stable, feature-local path rather than reaching into the api/ folder.
 *
 * If additional data-shaping logic is needed, add it here rather than
 * in the component.
 */
export { useBadges } from '../api/get-gamifications';
export { useStreaks } from '../api/get-gamifications';
export { useMilestones } from '../api/get-gamifications';