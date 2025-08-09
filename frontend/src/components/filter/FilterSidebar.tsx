import React, { useState, useEffect, useRef } from 'react';
import { useFilter } from '../../contexts/FilterContext';
import { categoryService } from '../../services/categoryService';
import { useSwipeGesture } from '../../hooks';
import type { Category, ExperienceLevel } from '../../types';

interface FilterSidebarProps {
  className?: string;
  isMobile?: boolean;
  isOpen?: boolean;
  onClose?: () => void;
}

const FilterSidebar: React.FC<FilterSidebarProps> = ({
  className = "",
  isMobile = false,
  isOpen = true,
  onClose
}) => {
  const {
    state,
    addCategory,
    removeCategory,
    addLocation,
    removeLocation,
    addExperienceLevel,
    removeExperienceLevel,
    setSalaryRange,
    setIsRemote,
    clearFilters,
    getActiveFiltersCount
  } = useFilter();

  const [categories, setAvailableCategories] = useState<Category[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);
  const [locationInput, setLocationInput] = useState('');
  const [showAllCategories, setShowAllCategories] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  // Swipe gesture for mobile sidebar
  const { attachSwipeListeners } = useSwipeGesture({
    onSwipeLeft: () => {
      if (isMobile && onClose) {
        onClose();
      }
    },
    threshold: 50,
  });

  // Experience level options
  const experienceLevels: { value: ExperienceLevel; label: string }[] = [
    { value: 'entry', label: 'Entry Level' },
    { value: 'junior', label: 'Junior' },
    { value: 'mid', label: 'Mid Level' },
    { value: 'senior', label: 'Senior' },
    { value: 'lead', label: 'Lead' },
    { value: 'executive', label: 'Executive' }
  ];

  // Common locations (could be fetched from API in the future)
  const commonLocations = [
    'New York, NY',
    'San Francisco, CA',
    'Los Angeles, CA',
    'Chicago, IL',
    'Boston, MA',
    'Seattle, WA',
    'Austin, TX',
    'Denver, CO',
    'Remote'
  ];

  // Load categories on mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        setIsLoadingCategories(true);
        const fetchedCategories = await categoryService.getCategories();
        setAvailableCategories(fetchedCategories);
      } catch (error) {
        console.error('Failed to load categories:', error);
      } finally {
        setIsLoadingCategories(false);
      }
    };

    loadCategories();
  }, []);

  // Attach swipe listeners for mobile
  useEffect(() => {
    if (isMobile && isOpen && sidebarRef.current) {
      const cleanup = attachSwipeListeners(sidebarRef.current);
      return cleanup;
    }
  }, [isMobile, isOpen, attachSwipeListeners]);

  const handleCategoryChange = (categoryId: number, checked: boolean) => {
    if (checked) {
      addCategory(categoryId);
    } else {
      removeCategory(categoryId);
    }
  };

  const handleLocationAdd = (location: string) => {
    if (location && !state.locations.includes(location)) {
      addLocation(location);
      setLocationInput('');
    }
  };

  const handleLocationInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleLocationAdd(locationInput);
    }
  };

  const handleExperienceLevelChange = (level: ExperienceLevel, checked: boolean) => {
    if (checked) {
      addExperienceLevel(level);
    } else {
      removeExperienceLevel(level);
    }
  };

  const handleSalaryRangeChange = (min: number, max: number) => {
    setSalaryRange([min, max]);
  };

  const handleRemoteChange = (value: boolean | null) => {
    setIsRemote(value);
  };

  const activeFiltersCount = getActiveFiltersCount();
  const displayedCategories = showAllCategories ? categories : categories.slice(0, 8);

  const sidebarContent = (
    <div className="space-y-6">
      {/* Filter Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Filters
          {activeFiltersCount > 0 && (
            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {activeFiltersCount}
            </span>
          )}
        </h2>
        {isMobile && onClose && (
          <button
            onClick={onClose}
            className="p-3 text-gray-400 hover:text-gray-600 active:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md touch-manipulation"
            aria-label="Close filters"
            style={{ minHeight: '44px', minWidth: '44px' }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Clear Filters */}
      {activeFiltersCount > 0 && (
        <button
          onClick={clearFilters}
          className="w-full text-sm text-blue-600 hover:text-blue-800 focus:outline-none focus:underline transition-colors duration-200"
        >
          Clear all filters
        </button>
      )}

      {/* Categories */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Category</h3>
        {isLoadingCategories ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {displayedCategories.map((category) => (
              <label key={category.id} className="flex items-center py-2 cursor-pointer touch-manipulation">
                <input
                  type="checkbox"
                  checked={state.categories.includes(category.id)}
                  onChange={(e) => handleCategoryChange(category.id, e.target.checked)}
                  className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-3 text-sm text-gray-700 select-none">{category.name}</span>
              </label>
            ))}
            {categories.length > 8 && (
              <button
                onClick={() => setShowAllCategories(!showAllCategories)}
                className="text-sm text-blue-600 hover:text-blue-800 focus:outline-none focus:underline"
              >
                {showAllCategories ? 'Show less' : `Show ${categories.length - 8} more`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Location */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Location</h3>
        
        {/* Location Input */}
        <div className="mb-3">
          <input
            type="text"
            value={locationInput}
            onChange={(e) => setLocationInput(e.target.value)}
            onKeyDown={handleLocationInputKeyDown}
            placeholder="Add location..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Selected Locations */}
        {state.locations.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-2">
              {state.locations.map((location) => (
                <span
                  key={location}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {location}
                  <button
                    onClick={() => removeLocation(location)}
                    className="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-600 focus:outline-none focus:bg-blue-200 focus:text-blue-600"
                    aria-label={`Remove ${location}`}
                  >
                    <svg className="w-2 h-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                      <path strokeLinecap="round" strokeWidth="1.5" d="m1 1 6 6m0-6L1 7" />
                    </svg>
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Common Locations */}
        <div className="space-y-2">
          {commonLocations.map((location) => (
            <label key={location} className="flex items-center py-2 cursor-pointer touch-manipulation">
              <input
                type="checkbox"
                checked={state.locations.includes(location)}
                onChange={(e) => {
                  if (e.target.checked) {
                    addLocation(location);
                  } else {
                    removeLocation(location);
                  }
                }}
                className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-3 text-sm text-gray-700 select-none">{location}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Level */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Experience Level</h3>
        <div className="space-y-2">
          {experienceLevels.map((level) => (
            <label key={level.value} className="flex items-center py-2 cursor-pointer touch-manipulation">
              <input
                type="checkbox"
                checked={state.experienceLevels.includes(level.value)}
                onChange={(e) => handleExperienceLevelChange(level.value, e.target.checked)}
                className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-3 text-sm text-gray-700 select-none">{level.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Salary Range */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Salary Range</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <input
              type="number"
              placeholder="Min"
              value={state.salaryRange[0] || ''}
              onChange={(e) => handleSalaryRangeChange(Number(e.target.value) || 0, state.salaryRange[1])}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="text-gray-500">to</span>
            <input
              type="number"
              placeholder="Max"
              value={state.salaryRange[1] === 200000 ? '' : state.salaryRange[1]}
              onChange={(e) => handleSalaryRangeChange(state.salaryRange[0], Number(e.target.value) || 200000)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="text-xs text-gray-500">
            {state.salaryRange[0] > 0 || state.salaryRange[1] < 200000 ? (
              `$${state.salaryRange[0].toLocaleString()} - $${state.salaryRange[1].toLocaleString()}`
            ) : (
              'Any salary range'
            )}
          </div>
        </div>
      </div>

      {/* Remote Work */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">Work Type</h3>
        <div className="space-y-2">
          <label className="flex items-center py-2 cursor-pointer touch-manipulation">
            <input
              type="radio"
              name="remote"
              checked={state.isRemote === null}
              onChange={() => handleRemoteChange(null)}
              className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-3 text-sm text-gray-700 select-none">All jobs</span>
          </label>
          <label className="flex items-center py-2 cursor-pointer touch-manipulation">
            <input
              type="radio"
              name="remote"
              checked={state.isRemote === true}
              onChange={() => handleRemoteChange(true)}
              className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-3 text-sm text-gray-700 select-none">Remote only</span>
          </label>
          <label className="flex items-center py-2 cursor-pointer touch-manipulation">
            <input
              type="radio"
              name="remote"
              checked={state.isRemote === false}
              onChange={() => handleRemoteChange(false)}
              className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-3 text-sm text-gray-700 select-none">On-site only</span>
          </label>
        </div>
      </div>
    </div>
  );

  if (isMobile) {
    return (
      <>
        {/* Mobile Overlay */}
        {isOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div className="fixed inset-0 bg-black bg-opacity-25" onClick={onClose} />
            <div ref={sidebarRef} className="relative flex flex-col w-full h-full max-w-sm bg-white shadow-xl">
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 touch-manipulation">
                {sidebarContent}
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      {sidebarContent}
    </div>
  );
};

export default FilterSidebar;