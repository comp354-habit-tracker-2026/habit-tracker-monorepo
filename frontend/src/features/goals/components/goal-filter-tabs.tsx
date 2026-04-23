import '../goals-ui.css';

export type GoalFilters = {
  type: 'all' | 'distance' | 'duration' | 'frequency' | 'calories' | 'custom';
  status: 'all' | 'active' | 'completed' | 'paused' | 'overdue';
  datePreset: 'all' | 'week' | 'month' | 'year' | 'range';
  dateFrom: string;
  dateTo: string;
};

type Props = {
  value: GoalFilters;
  onChange: (value: GoalFilters) => void;
};

const typeOptions: { label: string; value: GoalFilters['type'] }[] = [
  { value: 'all', label: 'All Types' },
  { value: 'distance', label: 'Distance' },
  { value: 'frequency', label: 'frequency' }, 
  { value: 'duration', label: 'Duration' },
  { value: 'calories', label: 'Calories' },
  { value: 'custom', label: 'Custom' },
];

const statusOptions: { label: string; value: GoalFilters['status'] }[] = [
  { label: 'All Status', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Completed', value: 'completed' },
  { label: 'Paused', value: 'paused' },
  { label: 'Overdue', value: 'overdue' },
];

const dateOptions: { label: string; value: GoalFilters['datePreset'] }[] = [
  { label: 'All Time', value: 'all' },
  { label: 'Past Week', value: 'week' },
  { label: 'Past Month', value: 'month' },
  { label: 'Past Year', value: 'year' },
  { label: 'Custom Range', value: 'range' },
];

export const GoalFilterTabs = ({ value, onChange }: Props) => {
  const renderGroup = <T extends string>(
    label: string,
    options: { label: string; value: T }[],
    selected: T,
    keyName: keyof GoalFilters
  ) => (
    <div className="goals-filter-section">
      <p className="goals-filter-title">{label}</p>

      <div className="goals-filter-pills">
        {options.map((opt) => (
          <button
            key={opt.value}
            onClick={() =>
              onChange({
                ...value,
                [keyName]: opt.value,
                ...(keyName === 'datePreset' && opt.value !== 'range'
                  ? { dateFrom: '', dateTo: '' }
                  : {}),
              })
            }
            className={`goals-pill ${
              selected === opt.value ? 'is-active' : ''
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="goals-filters-panel">
      {renderGroup('Goal Type', typeOptions, value.type, 'type')}
      {renderGroup('Status', statusOptions, value.status, 'status')}
      {renderGroup('Date Period', dateOptions, value.datePreset, 'datePreset')}

      {value.datePreset === 'range' && (
        <div className="goals-range-row">
          <input
            type="date"
            className="goals-input"
            value={value.dateFrom}
            onChange={(e) =>
              onChange({ ...value, dateFrom: e.target.value })
            }
          />

          <span className="goals-range-separator">to</span>

          <input
            type="date"
            className="goals-input"
            value={value.dateTo}
            onChange={(e) =>
              onChange({ ...value, dateTo: e.target.value })
            }
          />
        </div>
      )}
    </div>
  );
};