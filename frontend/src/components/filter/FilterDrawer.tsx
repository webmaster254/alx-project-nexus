import React, { useState, useEffect } from 'react';
import FilterSidebar from './FilterSidebar';
import { useFilter } from '../../contexts/FilterContext';

interface FilterDrawerProps {
  className?: string;
}

const FilterDrawer: React.FC<FilterDrawerProps> = ({ className = "" }) => {
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { getActiveFiltersCount } = useFilter();

  // Check if we're on mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024); // lg breakpoint
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Close mobile filter when clicking outside or pressing escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileFilterOpen(false);
      }
    };

    if (isMobileFilterOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isMobileFilterOpen]);

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <>
      {/* Mobile Filter Button */}
      {isMobile && (
        <div className="lg:hidden mb-4 sm:mb-6">
          <button
            onClick={() => setIsMobileFilterOpen(true)}
            className="inline-flex items-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-base sm:text-sm font-medium text-gray-700 hover:bg-gray-50 active:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 touch-manipulation"
            aria-label="Open filters"
            style={{ minHeight: '44px' }} // Ensure minimum touch target size
          >
            <svg
              className="w-5 h-5 mr-2 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z"
              />
            </svg>
            Filters
            {activeFiltersCount > 0 && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {activeFiltersCount}
              </span>
            )}
          </button>
        </div>
      )}

      {/* Desktop Sidebar */}
      {!isMobile && (
        <div className={`hidden lg:block ${className}`}>
          <FilterSidebar />
        </div>
      )}

      {/* Mobile Drawer */}
      <FilterSidebar
        isMobile={true}
        isOpen={isMobileFilterOpen}
        onClose={() => setIsMobileFilterOpen(false)}
      />
    </>
  );
};

export default FilterDrawer;