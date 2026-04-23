type FilterBarProps = {
  availableTypes: string[];
  selectedTypes: string[];
  startDate: string;
  endDate: string;
  onTypeToggle: (type: string) => void;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  onClearFilters: () => void;
};

export function FilterBar({
  availableTypes,
  selectedTypes,
  startDate,
  endDate,
  onTypeToggle,
  onStartDateChange,
  onEndDateChange,
  onClearFilters,
}: FilterBarProps) {
  return (
    <section className="activities-filter-bar" aria-label="Activity filters">
      <div className="activities-filter-bar__header">
        <h2 className="activities-filter-bar__title">Filter activities</h2>
        <button
          type="button"
          className="activities-filter-bar__clear-button"
          onClick={onClearFilters}
        >
          Clear filters
        </button>
      </div>

      <div className="activities-filter-bar__section">
        <p className="activities-filter-bar__label">Activity type</p>
        <div className="activities-filter-bar__types">
          {availableTypes.map((type) => (
            <label
              key={type}
              className="activities-filter-bar__type-option"
            >
              <input
                type="checkbox"
                checked={selectedTypes.includes(type)}
                onChange={() => onTypeToggle(type)}
              />
              <span>{type}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="activities-filter-bar__section activities-filter-bar__dates">
        <label className="activities-filter-bar__date-field">
          <span>Start date</span>
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </label>

        <label className="activities-filter-bar__date-field">
          <span>End date</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </label>
      </div>
    </section>
  );
} // code developed from chatGPT