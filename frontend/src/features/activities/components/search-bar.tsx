import React, { useState, useEffect, useCallback } from 'react';

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

/**
 * SearchBar component with debounced input.
 * Filters activities by keyword as user types.
 * Uses 300ms debounce to avoid excessive re-renders.
 */
export function SearchBar({ value, onChange, placeholder = 'Search activities...' }: SearchBarProps) {
  const [inputValue, setInputValue] = useState(value);

  // Debounce logic - update parent state only after user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      onChange(inputValue);
    }, 300);

    return () => clearTimeout(timer);
  }, [inputValue, onChange]);

  // Sync internal state with external value
  useEffect(() => {
    setInputValue(value);
  }, [value]);

  const handleClear = useCallback(() => {
    setInputValue('');
    onChange('');
  }, [onChange]);

  return (
    <div className="search-bar">
      <div className="search-bar__wrapper">
        <span className="search-bar__icon" aria-hidden="true">
          🔍
        </span>
        <input
          type="text"
          className="search-bar__input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={placeholder}
          aria-label="Search activities"
        />
        {inputValue && (
          <button
            className="search-bar__clear"
            onClick={handleClear}
            aria-label="Clear search"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
