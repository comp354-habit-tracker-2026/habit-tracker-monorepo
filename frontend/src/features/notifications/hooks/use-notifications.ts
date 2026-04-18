//copy from habits.hooks.use-habits

/**
 * Re-export the notifications query hook so that components can import from
 * a stable, feature-local path rather than reaching into the api/ folder.
 *
 * If additional data-shaping logic is needed, add it here rather than
 * in the component.
 */
export { useNotifications } from '../api/get-notifications';