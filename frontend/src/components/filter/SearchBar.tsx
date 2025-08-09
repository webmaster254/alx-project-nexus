import React, { useState, useEffect, useRef } from 'react';
import { useFilter } from '../../contexts/FilterContext';
import { useResponsive } from '../../hooks';
import { searchService } from '../../services/searchService';
import type { SearchSuggestion } from '../../types';

interface SearchBarProps {
  placeholder?: string;
  className?: string;
  showSuggestions?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Search jobs by title, company, or keywords...",
  className = "",
  showSuggestions = true
}) => {
  const { state, setSearchQuery } = useFilter();
  const [localQuery, setLocalQuery] = useState(state.searchQuery);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const suggestionDebounceRef = useRef<NodeJS.Timeout | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
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
      if (localQuery.trim()) {
        searchService.saveRecentSearch(localQuery.trim());
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [localQuery, setSearchQuery]);

  // Load suggestions with debouncing
  useEffect(() => {
    if (!showSuggestions) return;

    if (suggestionDebounceRef.current) {
      clearTimeout(suggestionDebounceRef.current);
    }

    suggestionDebounceRef.current = setTimeout(async () => {
      setIsLoadingSuggestions(true);
      try {
        const newSuggestions = await searchService.getMixedSuggestions(localQuery);
        setSuggestions(newSuggestions);
      } catch (error) {
        console.warn('Failed to load suggestions:', error);
        setSuggestions([]);
      } finally {
        setIsLoadingSuggestions(false);
      }
    }, 150);

    return () => {
      if (suggestionDebounceRef.current) {
        clearTimeout(suggestionDebounceRef.current);
      }
    };
  }, [localQuery, showSuggestions]);

  // Handle clicks outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestionsList(false);
        setSelectedSuggestionIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalQuery(e.target.value);
    setSelectedSuggestionIndex(-1);
    if (showSuggestions) {
      setShowSuggestionsList(true);
    }
  };

  const handleInputFocus = () => {
    if (showSuggestions && suggestions.length > 0) {
      setShowSuggestionsList(true);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setLocalQuery(suggestion.text);
    setSearchQuery(suggestion.text);
    setShowSuggestionsList(false);
    setSelectedSuggestionIndex(-1);
    searchService.saveRecentSearch(suggestion.text);
    inputRef.current?.blur();
  };

  const handleClear = () => {
    setLocalQuery('');
    setSearchQuery('');
    setShowSuggestionsList(false);
    setSelectedSuggestionIndex(-1);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestionsList || suggestions.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault();
        // Immediately trigger search on Enter
        if (debounceRef.current) {
          clearTimeout(debounceRef.current);
        }
        setSearchQuery(localQuery);
        if (localQuery.trim()) {
          searchService.saveRecentSearch(localQuery.trim());
        }
        inputRef.current?.blur();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0) {
          const selectedSuggestion = suggestions[selectedSuggestionIndex];
          handleSuggestionClick(selectedSuggestion);
        } else {
          setSearchQuery(localQuery);
          if (localQuery.trim()) {
            searchService.saveRecentSearch(localQuery.trim());
          }
          setShowSuggestionsList(false);
          inputRef.current?.blur();
        }
        break;
      case 'Escape':
        setShowSuggestionsList(false);
        setSelectedSuggestionIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const getSuggestionIcon = (type: SearchSuggestion['type']) => {
    switch (type) {
      case 'company':
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        );
      case 'location':
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        );
      case 'skill':
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        );
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
          ref={inputRef}
          type="text"
          value={localQuery}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          placeholder={isMobile ? "Search jobs..." : placeholder}
          className={`block w-full pl-10 pr-10 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 touch-manipulation ${
            isMobile 
              ? 'py-3 text-base' 
              : 'py-3 sm:py-3 text-base sm:text-sm'
          }`}
          aria-label="Search jobs"
          role="combobox"
          aria-expanded={showSuggestionsList}
          aria-haspopup="listbox"
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

      {/* Suggestions Dropdown */}
      {showSuggestions && showSuggestionsList && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto"
          role="listbox"
          aria-label="Search suggestions"
        >
          {isLoadingSuggestions ? (
            <div className="px-4 py-3 text-sm text-gray-500 flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading suggestions...
            </div>
          ) : suggestions.length > 0 ? (
            suggestions.map((suggestion, index) => (
              <button
                key={suggestion.id}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors duration-150 flex items-center space-x-3 touch-manipulation ${
                  index === selectedSuggestionIndex ? 'bg-blue-50 text-blue-700' : 'text-gray-900'
                } ${isMobile ? 'py-4' : 'py-3'}`}
                role="option"
                aria-selected={index === selectedSuggestionIndex}
                style={{ minHeight: isMobile ? '52px' : '44px' }}
              >
                <div className="flex-shrink-0">
                  {getSuggestionIcon(suggestion.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">
                    {suggestion.text}
                  </div>
                  {suggestion.count && (
                    <div className="text-xs text-gray-500">
                      {suggestion.count} jobs
                    </div>
                  )}
                </div>
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                    {suggestion.type.replace('_', ' ')}
                  </span>
                </div>
              </button>
            ))
          ) : localQuery.trim() && !isLoadingSuggestions ? (
            <div className="px-4 py-3 text-sm text-gray-500">
              No suggestions found for "{localQuery}"
            </div>
          ) : null}
          
          {/* Recent searches section */}
          {!localQuery.trim() && !isLoadingSuggestions && suggestions.length === 0 && (
            <div className="px-4 py-3 text-sm text-gray-500">
              Start typing to see suggestions
            </div>
          )}
        </div>
      )}

      {/* Screen reader description */}
      <div id="search-description" className="sr-only">
        Search for jobs by entering keywords, job titles, or company names. Results will update automatically as you type.
        {showSuggestionsList && suggestions.length > 0 && (
          <span> Use arrow keys to navigate suggestions and press Enter to select.</span>
        )}
      </div>
    </div>
  );
};

export default SearchBar;