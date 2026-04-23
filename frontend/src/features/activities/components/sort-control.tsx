import React from 'react';

export type SortOption = 'date-newest' | 'date-oldest' | 'duration' | 'distance';

type SortControlProps = {
  value: SortOption;
  onChange: (value: SortOption) => void;
};

/**
 * SortControl component for sorting activities list.
 * Provides dropdown with options: Date (newest/oldest), Duration, Distance
 */
export function SortControl({ value, onChange }: SortControlProps) {
  return (
    <div className="sort-control">
      <label htmlFor="sort-select" className="sort-control__label">
        Sort by:
      </label>
      <select
        id="sort-select"
        className="sort-control__select"
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        aria-label="Sort activities"
      >
        <option value="date-newest">Date (Newest)</option>
        <option value="date-oldest">Date (Oldest)</option>
        <option value="duration">Duration</option>
        <option value="distance">Distance</option>
      </select>
    </div>
  );
}
