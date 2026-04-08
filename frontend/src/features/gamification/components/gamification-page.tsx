import { useSummary } from '../api/get-summary';
import { DEMO_SUMMARY } from '../api/mock-data';
import './gamification.css';

import { PointsBanner } from './points-banner';
import { StreakCard } from './streak-card';
import { BadgeGrid } from './badge-grid';
import { MilestoneList } from './milestone-list';

export function GamificationPage() {
  const summaryQuery = useSummary();

  // Use real API data if available, otherwise fall back to demo data
  const summary = summaryQuery.data ?? (summaryQuery.isError ? DEMO_SUMMARY : null);

  if (summaryQuery.isLoading) return <p>Loading achievements...</p>;
  if (!summary) return null;

  return (
    <div className="gamification">
      {/* Top row: points + streak side by side */}
      <div className="gamification__top-row">
        <PointsBanner totalPoints={summary.total_points} />
        <StreakCard streak={summary.streak} />
      </div>

      {/* Badges and milestones fill the width */}
      <BadgeGrid
        badgeProgress={summary.badge_progress}
        earnedBadges={summary.badges_earned}
      />
      <MilestoneList
        milestoneProgress={summary.milestone_progress}
        reachedMilestones={summary.milestones_reached}
      />
    </div>
  );
}
