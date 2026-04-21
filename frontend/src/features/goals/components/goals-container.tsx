import { useEffect, useMemo, useState } from 'react';
import { useGoals } from '../api/get-goals';
import { GoalCard } from './goal-card';
import { GoalFilterTabs, type GoalFilters } from './goal-filter-tabs';
import { CreateGoalForm } from './create-goal-form';
import type { Goal } from '../types/goal';
import '../goals-ui.css';

const mockGoals: Goal[] = [

  {
    id: 102,
    title: 'Morning Run Consistency',
    description: 'Keep a routine of shorter daily runs.',
    target_value: 40,
    current_value: 9,
    progress_percentage: 22.5,
    goal_type: 'distance',
    status: 'active',
    start_date: '2026-04-10',
    end_date: '2026-05-02',
    created_at: '2026-04-10T08:00:00Z',
    updated_at: '2026-04-19T08:00:00Z',
  },

  {
    id: 104,
    title: 'Trail Weekend Block',
    description: 'Paused while recovering from fatigue.',
    target_value: 90,
    current_value: 24,
    progress_percentage: 26.7,
    goal_type: 'distance',
    status: 'paused',
    start_date: '2026-04-01',
    end_date: '2026-06-01',
    created_at: '2026-04-01T11:00:00Z',
    updated_at: '2026-04-14T11:00:00Z',
  },
  {
    id: 105,
    title: 'Half Marathon Base',
    description: 'This one should appear as overdue.',
    target_value: 120,
    current_value: 86,
    progress_percentage: 71.7,
    goal_type: 'distance',
    status: 'active',
    start_date: '2026-03-01',
    end_date: '2026-03-28',
    created_at: '2026-03-01T07:30:00Z',
    updated_at: '2026-03-29T07:30:00Z',
  },
  {
    id: 106,
    title: 'Winter Mileage Goal',
    description: 'Older distance goal for year filter testing.',
    target_value: 300,
    current_value: 300,
    progress_percentage: 100,
    goal_type: 'distance',
    status: 'completed',
    start_date: '2025-10-10',
    end_date: '2025-12-31',
    created_at: '2025-10-10T07:00:00Z',
    updated_at: '2025-12-31T07:00:00Z',
  },
  {
    id: 108,
    title: 'Long Run Time Goal',
    description: 'Increase time on feet gradually.',
    target_value: 360,
    current_value: 145,
    progress_percentage: 40.3,
    goal_type: 'duration',
    status: 'active',
    start_date: '2026-04-05',
    end_date: '2026-05-05',
    created_at: '2026-04-05T06:40:00Z',
    updated_at: '2026-04-18T06:40:00Z',
  },
  {
    id: 109,
    title: 'Core Session Minutes',
    description: 'Completed time-based conditioning block.',
    target_value: 180,
    current_value: 180,
    progress_percentage: 100,
    goal_type: 'duration',
    status: 'completed',
    start_date: '2026-03-15',
    end_date: '2026-04-05',
    created_at: '2026-03-15T12:00:00Z',
    updated_at: '2026-04-05T12:00:00Z',
  },
  {
    id: 110,
    title: 'Yoga Reset',
    description: 'Temporarily paused during exams.',
    target_value: 210,
    current_value: 40,
    progress_percentage: 19,
    goal_type: 'duration',
    status: 'paused',
    start_date: '2026-04-12',
    end_date: '2026-05-20',
    created_at: '2026-04-12T18:00:00Z',
    updated_at: '2026-04-15T18:00:00Z',
  },
  {
    id: 111,
    title: 'Stretch Before Bed',
    description: 'Should show as overdue because end date passed.',
    target_value: 120,
    current_value: 58,
    progress_percentage: 48.3,
    goal_type: 'duration',
    status: 'active',
    start_date: '2026-03-01',
    end_date: '2026-03-20',
    created_at: '2026-03-01T20:00:00Z',
    updated_at: '2026-03-20T20:00:00Z',
  },
  {
    id: 112,
    title: 'Meditation Minutes',
    description: 'Older duration goal for broader date tests.',
    target_value: 500,
    current_value: 410,
    progress_percentage: 82,
    goal_type: 'duration',
    status: 'active',
    start_date: '2025-08-10',
    end_date: '2025-12-01',
    created_at: '2025-08-10T08:10:00Z',
    updated_at: '2025-11-10T08:10:00Z',
  },
  {
    id: 113,
    title: 'Workout Frequency Block',
    description: 'Hit four sessions each week.',
    target_value: 15,
    current_value: 6,
    progress_percentage: 40,
    goal_type: 'frequency',
    status: 'active',
    start_date: '2026-04-15',
    end_date: '2026-05-15',
    created_at: '2026-04-15T14:00:00Z',
    updated_at: '2026-04-18T14:00:00Z',
  },
  {
    id: 114,
    title: 'Gym Consistency',
    description: 'Keep lifting three times a week.',
    target_value: 12,
    current_value: 9,
    progress_percentage: 75,
    goal_type: 'frequency',
    status: 'active',
    start_date: '2026-04-01',
    end_date: '2026-04-30',
    created_at: '2026-04-01T17:00:00Z',
    updated_at: '2026-04-18T17:00:00Z',
  },
  {
    id: 115,
    title: 'Martial arts course',
    description: 'Finished all planned sessions.',
    target_value: 10,
    current_value: 10,
    progress_percentage: 100,
    goal_type: 'frequency',
    status: 'completed',
    start_date: '2026-03-10',
    end_date: '2026-04-10',
    created_at: '2026-03-10T16:00:00Z',
    updated_at: '2026-04-10T16:00:00Z',
  },
  {
    id: 116,
    title: 'Swim Sessions',
    description: 'Paused while pool access is limited.',
    target_value: 8,
    current_value: 2,
    progress_percentage: 25,
    goal_type: 'frequency',
    status: 'paused',
    start_date: '2026-04-08',
    end_date: '2026-05-28',
    created_at: '2026-04-08T13:00:00Z',
    updated_at: '2026-04-12T13:00:00Z',
  },
  {
    id: 118,
    title: 'Dance Practice Sessions',
    description: 'Older frequency-based goal.',
    target_value: 20,
    current_value: 15,
    progress_percentage: 75,
    goal_type: 'frequency',
    status: 'active',
    start_date: '2025-11-05',
    end_date: '2025-12-20',
    created_at: '2025-11-05T19:00:00Z',
    updated_at: '2025-12-10T19:00:00Z',
  },
  {
    id: 119,
    title: 'Calories Burned This Month',
    description: 'Daily cardio calorie target.',
    target_value: 3000,
    current_value: 850,
    progress_percentage: 28.3,
    goal_type: 'calories',
    status: 'active',
    start_date: '2026-04-14',
    end_date: '2026-05-10',
    created_at: '2026-04-14T08:45:00Z',
    updated_at: '2026-04-18T08:45:00Z',
  },
  {
    id: 121,
    title: 'Spring Cut Goal',
    description: 'Completed calorie target.',
    target_value: 1800,
    current_value: 1800,
    progress_percentage: 100,
    goal_type: 'calories',
    status: 'completed',
    start_date: '2026-03-18',
    end_date: '2026-04-12',
    created_at: '2026-03-18T15:00:00Z',
    updated_at: '2026-04-12T15:00:00Z',
  },
  {
    id: 122,
    title: 'Workout Burn Goal',
    description: 'Paused during deload week.',
    target_value: 2500,
    current_value: 900,
    progress_percentage: 36,
    goal_type: 'calories',
    status: 'paused',
    start_date: '2026-04-07',
    end_date: '2026-05-25',
    created_at: '2026-04-07T11:30:00Z',
    updated_at: '2026-04-13T11:30:00Z',
  },
  {
    id: 124,
    title: 'Winter Calorie Burn',
    description: 'Older calorie goal for date coverage.',
    target_value: 5000,
    current_value: 3200,
    progress_percentage: 64,
    goal_type: 'calories',
    status: 'active',
    start_date: '2025-09-12',
    end_date: '2025-11-30',
    created_at: '2025-09-12T09:15:00Z',
    updated_at: '2025-11-15T09:15:00Z',
  },
  {
    id: 125,
    title: 'Read 12 Books',
    description: 'Custom goal with manual progress.',
    target_value: 12,
    current_value: 4,
    progress_percentage: 33.3,
    goal_type: 'custom',
    status: 'active',
    start_date: '2026-04-13',
    end_date: '2026-06-30',
    created_at: '2026-04-13T21:00:00Z',
    updated_at: '2026-04-18T21:00:00Z',
  },
  {
    id: 126,
    title: 'Drink More Water',
    description: 'Simple personal habit tracker.',
    target_value: 30,
    current_value: 17,
    progress_percentage: 56.7,
    goal_type: 'custom',
    status: 'active',
    start_date: '2026-04-01',
    end_date: '2026-04-30',
    created_at: '2026-04-01T06:00:00Z',
    updated_at: '2026-04-18T06:00:00Z',
  },
  {
    id: 127,
    title: 'No Sugar Challenge',
    description: 'Successfully completed challenge period.',
    target_value: 21,
    current_value: 21,
    progress_percentage: 100,
    goal_type: 'custom',
    status: 'completed',
    start_date: '2026-03-15',
    end_date: '2026-04-05',
    created_at: '2026-03-15T09:40:00Z',
    updated_at: '2026-04-05T09:40:00Z',
  },
  {
    id: 128,
    title: 'Journal Every Night',
    description: 'Paused while travelling.',
    target_value: 30,
    current_value: 7,
    progress_percentage: 23.3,
    goal_type: 'custom',
    status: 'paused',
    start_date: '2026-04-09',
    end_date: '2026-05-31',
    created_at: '2026-04-09T22:00:00Z',
    updated_at: '2026-04-14T22:00:00Z',
  },
  {
    id: 129,
    title: 'Daily Habit Streak',
    description: 'Custom goal that should appear overdue.',
    target_value: 30,
    current_value: 18,
    progress_percentage: 60,
    goal_type: 'custom',
    status: 'active',
    start_date: '2026-03-02',
    end_date: '2026-03-22',
    created_at: '2026-03-02T08:30:00Z',
    updated_at: '2026-03-22T08:30:00Z',
  },
  {
    id: 130,
    title: 'Save for Trip',
    description: 'Older custom goal for broad date filtering.',
    target_value: 1000,
    current_value: 650,
    progress_percentage: 65,
    goal_type: 'custom',
    status: 'active',
    start_date: '2025-07-01',
    end_date: '2025-12-31',
    created_at: '2025-07-01T10:10:00Z',
    updated_at: '2025-11-20T10:10:00Z',
  },
];

const defaultFilters: GoalFilters = {
  type: 'all',
  status: 'all',
  datePreset: 'all',
  dateFrom: '',
  dateTo: '',
};

const getEffectiveStatus = (goal: Goal): Goal['status'] | 'overdue' => {
  if (goal.status !== 'active' || !goal.end_date) {
    return goal.status;
  }

  const today = new Date();
  const end = new Date(goal.end_date);

  today.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);

  return end < today ? 'overdue' : 'active';
};

const isWithinPreset = (dateValue: string, preset: GoalFilters['datePreset']) => {
  if (!dateValue || preset === 'all' || preset === 'range') return true;

  const date = new Date(dateValue);
  const today = new Date();
  const threshold = new Date();

  today.setHours(23, 59, 59, 999);
  date.setHours(0, 0, 0, 0);

  if (preset === 'week') {
    threshold.setDate(today.getDate() - 7);
  } else if (preset === 'month') {
    threshold.setMonth(today.getMonth() - 1);
  } else if (preset === 'year') {
    threshold.setFullYear(today.getFullYear() - 1);
  }

  threshold.setHours(0, 0, 0, 0);

  return date >= threshold && date <= today;
};

const isWithinRange = (dateValue: string, from: string, to: string) => {
  if (!dateValue) return false;

  const date = new Date(dateValue);
  date.setHours(0, 0, 0, 0);

  if (from) {
    const fromDate = new Date(from);
    fromDate.setHours(0, 0, 0, 0);
    if (date < fromDate) return false;
  }

  if (to) {
    const toDate = new Date(to);
    toDate.setHours(0, 0, 0, 0);
    if (date > toDate) return false;
  }

  return true;
};

export const GoalsContainer = () => {
  const { data: fetchedGoals, isLoading, isError } = useGoals();
  const [dataMode, setDataMode] = useState<'api' | 'mock'>('mock');
  const [filters, setFilters] = useState<GoalFilters>(defaultFilters);
  const [mockGoalsState, setMockGoalsState] = useState<Goal[]>(mockGoals);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  const sourceGoals = dataMode === 'mock' ? mockGoalsState : (fetchedGoals ?? []);

  const filteredGoals = useMemo(() => {
    return sourceGoals.filter((goal) => {
      const effectiveStatus = getEffectiveStatus(goal);

      const matchesType =
        filters.type === 'all' || goal.goal_type === filters.type;

      const matchesStatus =
        filters.status === 'all' || effectiveStatus === filters.status;

      const dateField = goal.start_date;

      const matchesDatePreset =
        filters.datePreset === 'range'
          ? true
          : isWithinPreset(dateField, filters.datePreset);

      const matchesRange =
        filters.datePreset !== 'range'
          ? true
          : isWithinRange(dateField, filters.dateFrom, filters.dateTo);

      return matchesType && matchesStatus && matchesDatePreset && matchesRange;
    });
  }, [sourceGoals, filters]);

  useEffect(() => {
    setCurrentPage(1);
  }, [filters, dataMode]);

  useEffect(() => {
    const maxPage = Math.max(1, Math.ceil(filteredGoals.length / pageSize));
    if (currentPage > maxPage) {
      setCurrentPage(maxPage);
    }
  }, [filteredGoals.length, currentPage]);

  const totalPages = Math.ceil(filteredGoals.length / pageSize);

  const paginatedGoals = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredGoals.slice(start, start + pageSize);
  }, [filteredGoals, currentPage]);

  const startItem =
    filteredGoals.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;

  const endItem = Math.min(currentPage * pageSize, filteredGoals.length);

  const showLoading = dataMode === 'api' && isLoading;
  const showError = dataMode === 'api' && isError;

  return (
    <section className="goals-section">
      <h2 className="goals-heading">Goals Progress</h2>

      <div className="goals-mode-toggle">
        <button
          type="button"
          onClick={() => setDataMode('api')}
          className={`goals-mode-btn ${dataMode === 'api' ? 'is-active' : ''}`}
        >
          Live API
        </button>

        <button
          type="button"
          onClick={() => setDataMode('mock')}
          className={`goals-mode-btn ${dataMode === 'mock' ? 'is-active' : ''}`}
        >
          Mock Data
        </button>
      </div>

      <div className="goals-create-box">
        <CreateGoalForm
          mode={dataMode}
          onCreateMock={(newGoal) =>
            setMockGoalsState((prev) => [newGoal, ...prev])
          }
        />
      </div>

      <div className="goals-filter-box">
        <GoalFilterTabs value={filters} onChange={setFilters} />
      </div>

      {showLoading ? (
        <div className="goals-empty">Loading goals...</div>
      ) : showError ? (
        <div className="goals-empty">
          Could not load API goals. Switch to Mock Data to keep testing.
        </div>
      ) : (
        <div className="goals-list">
          {paginatedGoals.map((goal) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              mode={dataMode}
              onDelete={(id) =>
                setMockGoalsState((prev) => prev.filter((g) => g.id !== id))
              }
              onUpdate={(id, updates) =>
                setMockGoalsState((prev) =>
                  prev.map((g) => {
                    if (g.id !== id) return g;

                    const nextGoal = { ...g, ...updates };
                    const target = Number(nextGoal.target_value) || 0;
                    const current = Number(nextGoal.current_value) || 0;

                    return {
                      ...nextGoal,
                      progress_percentage:
                        target > 0 ? Math.min(100, (current / target) * 100) : 0,
                      updated_at: new Date().toISOString(),
                    };
                  })
                )
              }
            />
          ))}

          {!filteredGoals.length && (
            <div className="goals-empty">No goals match the current filters.</div>
          )}

          {filteredGoals.length > pageSize && (
            <div className="goals-pagination">
              <span className="goals-pagination-info">
                Showing {startItem}-{endItem} of {filteredGoals.length} goals
              </span>

              <div className="goals-pagination-controls">
                <button
                  type="button"
                  className="goals-page-btn"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  ‹
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    type="button"
                    className={`goals-page-btn ${currentPage === page ? 'is-active' : ''}`}
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </button>
                ))}

                <button
                  type="button"
                  className="goals-page-btn"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  ›
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};