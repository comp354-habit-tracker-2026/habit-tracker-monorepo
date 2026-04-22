/**
 * Loading skeleton displayed while activities are being fetched.
 * Shows placeholder cards with animated shimmer effect.
 */

export function ActivityListSkeleton() {
  return (
    <div className="activity-list-skeleton" role="status" aria-label="Loading activities">
      <div className="activity-list-skeleton__item">
        <div className="activity-list-skeleton__icon" />
        <div className="activity-list-skeleton__content">
          <div className="activity-list-skeleton__line activity-list-skeleton__line--title" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--subtitle" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--meta" />
        </div>
      </div>
      <div className="activity-list-skeleton__item">
        <div className="activity-list-skeleton__icon" />
        <div className="activity-list-skeleton__content">
          <div className="activity-list-skeleton__line activity-list-skeleton__line--title" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--subtitle" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--meta" />
        </div>
      </div>
      <div className="activity-list-skeleton__item">
        <div className="activity-list-skeleton__icon" />
        <div className="activity-list-skeleton__content">
          <div className="activity-list-skeleton__line activity-list-skeleton__line--title" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--subtitle" />
          <div className="activity-list-skeleton__line activity-list-skeleton__line--meta" />
        </div>
      </div>
    </div>
  );
}
