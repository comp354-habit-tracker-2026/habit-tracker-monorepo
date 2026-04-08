type PointsBannerProps = {
  totalPoints: number;
};

export function PointsBanner({ totalPoints }: PointsBannerProps) {
  return (
    <div className="gamification__banner">
      <span className="gamification__banner-label">Total Points</span>
      <span className="gamification__banner-value">{totalPoints.toLocaleString()}</span>
    </div>
  );
}
