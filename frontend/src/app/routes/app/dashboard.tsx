import { useState } from 'react';

import { ContentLayout } from '@/components/layouts/content-layout';
import '@coreui/coreui-pro/dist/css/coreui.min.css';
import { CCalendar } from '@coreui/react-pro';
import {
  formatMockActivityDate,
  getMockActivitiesForDate,
  mockActivityCalendarDays,
} from './mock-activities';

const activityCalendarDate = mockActivityCalendarDays[0]?.date ?? new Date();
type StatsViewMode = 'total' | 'per-activity';
const oneDayMs = 24 * 60 * 60 * 1000;

function toLocalDateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

function dateKeyToUtcMs(dateKey: string) {
  const [year, month, day] = dateKey.split('-').map(Number);

  return Date.UTC(year, month - 1, day);
}

function getStreakGroups() {
  const sortedDateKeys = [...mockActivityCalendarDays]
    .map((day) => day.dateKey)
    .sort((left, right) => dateKeyToUtcMs(left) - dateKeyToUtcMs(right));
  const groups: string[][] = [];
  let currentGroup: string[] = [];

  for (const dateKey of sortedDateKeys) {
    if (!currentGroup.length) {
      currentGroup = [dateKey];
      continue;
    }

    const previous = currentGroup[currentGroup.length - 1];
    if (dateKeyToUtcMs(dateKey) - dateKeyToUtcMs(previous) === oneDayMs) {
      currentGroup.push(dateKey);
      continue;
    }

    groups.push(currentGroup);
    currentGroup = [dateKey];
  }

  if (currentGroup.length) {
    groups.push(currentGroup);
  }

  return groups;
}

const streakGroups = getStreakGroups();
const streakDateKeys = new Set(
  streakGroups.filter((group) => group.length > 1).flatMap((group) => group),
);
const longestStreak = streakGroups.reduce(
  (longest, group) => (group.length > longest ? group.length : longest),
  0,
);

function formatDuration(totalSeconds: number) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  return `${minutes}m`;
}

function formatNumber(value: number, fractionDigits = 1) {
  return value.toLocaleString('en-US', {
    maximumFractionDigits: fractionDigits,
    minimumFractionDigits: fractionDigits,
  });
}

function summarizeActivities(activities: ReturnType<typeof getMockActivitiesForDate>) {
  return activities.reduce(
    (summary, activity) => {
      summary.count += 1;
      summary.durationSeconds += activity.summary.durationSeconds;
      summary.distanceKm += activity.summary.distanceKm ?? 0;
      summary.calories += activity.summary.calories ?? 0;
      summary.elevationGainM += activity.summary.elevationGainM ?? 0;
      summary.elevationLossM += activity.summary.elevationLossM ?? 0;
      summary.speedValues.push(activity.summary.avgSpeedKmh ?? activity.summary.maxSpeedKmh ?? 0);
      summary.heartRateValues.push(activity.summary.avgHeartRate ?? 0);

      return summary;
    },
    {
      calories: 0,
      count: 0,
      distanceKm: 0,
      durationSeconds: 0,
      elevationGainM: 0,
      elevationLossM: 0,
      heartRateValues: [] as number[],
      speedValues: [] as number[],
    },
  );
}

function renderActivityDayCell(date: Date) {
  const activitiesForDay = getMockActivitiesForDate(date);
  const activityCount = activitiesForDay.length;
  const isStreakDay = streakDateKeys.has(toLocalDateKey(date));

  return (
    <div
      style={{
        alignItems: 'center',
        border: isStreakDay ? '2px solid #f59f00' : '2px solid transparent',
        borderRadius: '0.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.25rem',
        justifyContent: 'center',
        minHeight: '2.75rem',
        opacity: activitiesForDay.length ? 1 : 0.85,
        width: '100%',
      }}
    >
      <span style={{ fontWeight: 600 }}>{date.getDate()}</span>
      {activityCount > 0 && (
        <div style={{ alignItems: 'center', display: 'flex', gap: '0.25rem' }}>
          <span
            style={{
              alignItems: 'center',
              backgroundColor: '#0d6efd',
              borderRadius: '999px',
              color: '#fff',
              display: 'inline-flex',
              fontSize: '0.7rem',
              fontWeight: 700,
              height: '1.1rem',
              justifyContent: 'center',
              minWidth: '1.1rem',
              padding: '0 0.35rem',
            }}
          >
            {activityCount}
          </span>
          {isStreakDay && (
            <span
              style={{
                color: '#f59f00',
                fontSize: '0.65rem',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              streak
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function getStreakLengthForDate(date: Date) {
  const target = toLocalDateKey(date);
  const group = streakGroups.find((days) => days.includes(target));

  return group?.length ?? (getMockActivitiesForDate(date).length > 0 ? 1 : 0);
}

function DashboardRoute() {
  const [selectedDate, setSelectedDate] = useState(activityCalendarDate);
  const [statsViewMode, setStatsViewMode] = useState<StatsViewMode>('total');

  const selectedActivities = getMockActivitiesForDate(selectedDate);
  const selectedSummary = summarizeActivities(selectedActivities);
  const averageSpeed =
    selectedSummary.speedValues.length > 0
      ? selectedSummary.speedValues.reduce((total, value) => total + value, 0) /
        selectedSummary.speedValues.length
      : 0;
  const averageHeartRate =
    selectedSummary.heartRateValues.length > 0
      ? selectedSummary.heartRateValues.reduce((total, value) => total + value, 0) /
        selectedSummary.heartRateValues.length
      : 0;
  const selectedDayStreak = getStreakLengthForDate(selectedDate);

  return (
    <ContentLayout title="Dashboard">
      <div className="row g-4 align-items-start">
        <div className="col-12 col-xl-8">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body p-4">
              <div className="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-3">
                <div>
                  <h2 className="h4 mb-1">Activity calendar</h2>
                  <p className="text-secondary mb-0">
                    Days with activities are marked with a count badge.
                  </p>
                </div>
                <span className="badge text-bg-primary align-self-center">
                  {mockActivityCalendarDays.length} active days
                </span>
              </div>
              <div className="d-flex flex-wrap gap-2 mb-3">
                <span className="badge text-bg-warning">Longest streak: {longestStreak} days</span>
                <span className="badge text-bg-light border">Streak days are outlined in gold</span>
              </div>
              <CCalendar
                calendarDate={selectedDate}
                className="border rounded-3"
                locale="en-US"
                onStartDateChange={(date) => {
                  if (date) {
                    setSelectedDate(new Date(date));
                  }
                }}
                startDate={selectedDate}
                renderDayCell={renderActivityDayCell}
              />
            </div>
          </div>
        </div>

        <div className="col-12 col-xl-4">
          <div className="card border-0 shadow-sm h-100">
            <div className="card-body p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 mb-3">
                <div>
                  <h2 className="h5 mb-1">Selected day stats</h2>
                  <p className="text-secondary mb-0">Click a day with activity to inspect totals.</p>
                </div>
                <span className="badge text-bg-dark">
                  {formatMockActivityDate(selectedDate)}
                </span>
              </div>
              {selectedActivities.length > 0 && (
                <div className="alert alert-warning py-2 px-3 mb-3" role="status">
                  Activity streak for this day: {selectedDayStreak} day
                  {selectedDayStreak === 1 ? '' : 's'}
                </div>
              )}

              {selectedActivities.length > 1 && (
                <div className="btn-group mb-3" role="group" aria-label="Selected day stats mode">
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      statsViewMode === 'total' ? 'btn-primary' : 'btn-outline-primary'
                    }`}
                    onClick={() => setStatsViewMode('total')}
                  >
                    Total day
                  </button>
                  <button
                    type="button"
                    className={`btn btn-sm ${
                      statsViewMode === 'per-activity' ? 'btn-primary' : 'btn-outline-primary'
                    }`}
                    onClick={() => setStatsViewMode('per-activity')}
                  >
                    Per activity
                  </button>
                </div>
              )}

              {selectedActivities.length > 0 ? (
                <div className="d-grid gap-3">
                  {statsViewMode === 'total' && (
                    <>
                      <div className="row g-3">
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Activities</div>
                            <div className="h4 mb-0">{selectedSummary.count}</div>
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Total duration</div>
                            <div className="h4 mb-0">{formatDuration(selectedSummary.durationSeconds)}</div>
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Distance</div>
                            <div className="h4 mb-0">{formatNumber(selectedSummary.distanceKm)} km</div>
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Calories</div>
                            <div className="h4 mb-0">{selectedSummary.calories.toLocaleString('en-US')}</div>
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Avg speed</div>
                            <div className="h4 mb-0">{formatNumber(averageSpeed)} km/h</div>
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="border rounded-3 p-3 bg-body-tertiary h-100">
                            <div className="text-secondary small">Avg heart rate</div>
                            <div className="h4 mb-0">{Math.round(averageHeartRate)} bpm</div>
                          </div>
                        </div>
                      </div>
                      <article className="border rounded-3 p-3 bg-body-tertiary">
                        <div className="fw-semibold mb-2">Activities on this day</div>
                        <ul className="list-unstyled mb-0 small">
                          {selectedActivities.map((activity) => (
                            <li key={activity.id} className="d-flex justify-content-between gap-2 py-1">
                              <span className="text-body">{activity.title}</span>
                              <span className="text-secondary text-capitalize">{activity.activityType}</span>
                            </li>
                          ))}
                        </ul>
                      </article>
                    </>
                  )}

                  {statsViewMode === 'per-activity' && (
                    <div className="d-grid gap-3">
                      {selectedActivities.map((activity) => (
                        <article key={activity.id} className="border rounded-3 p-3 bg-body-tertiary">
                          <div className="d-flex justify-content-between align-items-start gap-2 mb-3">
                            <div>
                              <div className="fw-semibold">{activity.title}</div>
                              <div className="text-secondary small text-capitalize">
                                {activity.activityType}
                              </div>
                            </div>
                          </div>
                          <div className="row g-2 small">
                            <div className="col-6">
                              <div className="text-secondary">Duration</div>
                              <div className="fw-semibold">
                                {formatDuration(activity.summary.durationSeconds)}
                              </div>
                            </div>
                            <div className="col-6">
                              <div className="text-secondary">Distance</div>
                              <div className="fw-semibold">
                                {activity.summary.distanceKm !== undefined
                                  ? `${formatNumber(activity.summary.distanceKm)} km`
                                  : 'N/A'}
                              </div>
                            </div>
                            <div className="col-6">
                              <div className="text-secondary">Calories</div>
                              <div className="fw-semibold">
                                {activity.summary.calories?.toLocaleString('en-US') ?? 'N/A'}
                              </div>
                            </div>
                            <div className="col-6">
                              <div className="text-secondary">Avg speed</div>
                              <div className="fw-semibold">
                                {activity.summary.avgSpeedKmh !== undefined
                                  ? `${formatNumber(activity.summary.avgSpeedKmh)} km/h`
                                  : 'N/A'}
                              </div>
                            </div>
                          </div>
                        </article>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="border rounded-3 p-4 bg-body-tertiary text-secondary">
                  No activities were recorded on this day.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ContentLayout>
  );
}

export default DashboardRoute;
