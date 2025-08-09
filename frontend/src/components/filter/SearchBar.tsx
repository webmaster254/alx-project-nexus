import React, { useState, useEffect, useRef } from 'react';
import { useFilter } from '../../contexts/FilterContext';
import { useResponsive } from '../../hooks';

interface SearchBarProps {
  placeholder?: string;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Search jobs by title, company, or keywords...",
  className = ""
}) => {
  const { state, setSearchQuery } = useFilter();
  const [localQuery, setLocalQuery] = useState(state.searchQuery);
  const debounceRef = useRef<number | null>(null);
  const { isMobile } = useResponsive();

  // Update local state when context changes (e.g., from URL params)
  useEffect(() => {
    setLocalQuery(state.searchQuery);
  }, [state.searchQuery]);

  // Debounced search handler
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      setSearchQuery(localQuery);
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [localQuery, setSearchQuery]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(e.target.value);
  };

  const handleClear = () => {
    setLocalQuery('');
    setSearchQuery('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      // Immediately trigger search on Enter
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      setSearchQuery(localQuery);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        {/* Search Icon */}
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        {/* Input Field */}
        <input
          type="text"
          value={localQuery}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={isMobile ? "Search jobs..." : placeholder}
          className={`block w-full pl-10 pr-10 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 touch-manipulation ${
            isMobile 
              ? 'py-3 text-base' 
              : 'py-3 sm:py-3 text-base sm:text-sm'
          }`}
          aria-label="Search jobs"
          role="searchbox"
          aria-describedby="search-description"
          style={{ minHeight: isMobile ? '48px' : '44px' }} // Larger touch target for mobile
          autoComplete="off"
          autoCapitalize="none"
          autoCorrect="off"
          spellCheck="false"
        />

        {/* Clear Button */}
        {localQuery && (
          <button
            type="button"
            onClick={handleClear}
            className={`absolute inset-y-0 right-0 flex items-center hover:text-gray-600 focus:outline-none focus:text-gray-600 transition-colors duration-200 touch-manipulation ${
              isMobile ? 'pr-2 w-12' : 'pr-3'
            }`}
            aria-label="Clear search"
            style={{ minHeight: isMobile ? '48px' : '44px', minWidth: isMobile ? '48px' : '44px' }}
          >
            <svg
              className={`text-gray-400 hover:text-gray-600 ${isMobile ? 'h-6 w-6' : 'h-5 w-5'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Screen reader description */}
      <div id="search-description" className="sr-only">
        Search for jobs by entering keywords, job titles, or company names. Results will update automatically as you type.
      </div>
    </div>
  );
};

export default SearchBar;