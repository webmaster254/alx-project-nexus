import { render, screen, act } from '@testing-library/react';
import { vi } from 'vitest';
import { FilterProvider, useFilter } from '../FilterContext';
import type { ExperienceLevel } from '../../types';

// Test component that uses the FilterContext
function TestComponent() {
  const {
    state,
    setSearchQuery,
    setCategories,
    addCategory,
    removeCategory,
    setLocations,
    addLocation,
    removeLocation,
    setExperienceLevels,
    addExperienceLevel,
    removeExperienceLevel,
    setSalaryRange,
    setJobTypes,
    addJobType,
    removeJobType,
    setIsRemote,
    clearFilters,
    resetFilters,
    getActiveFiltersCount,
    hasActiveFilters,
  } = useFilter();

  return (
    <div>
      <div data-testid="search-query">{state.searchQuery}</div>
      <div data-testid="categories">{state.categories.join(',')}</div>
      <div data-testid="locations">{state.locations.join(',')}</div>
      <div data-testid="experience-levels">{state.experienceLevels.join(',')}</div>
      <div data-testid="salary-range">{state.salaryRange.join('-')}</div>
      <div data-testid="job-types">{state.jobTypes.join(',')}</div>
      <div data-testid="is-remote">{String(state.isRemote)}</div>
      <div data-testid="is-active">{state.isActive.toString()}</div>
      <div data-testid="active-filters-count">{getActiveFiltersCount()}</div>
      <div data-testid="has-active-filters">{hasActiveFilters().toString()}</div>

      <button onClick={() => setSearchQuery('developer')} data-testid="set-search">
        Set Search
      </button>
      <button onClick={() => setCategories([1, 2])} data-testid="set-categories">
        Set Categories
      </button>
      <button onClick={() => addCategory(3)} data-testid="add-category">
        Add Category
      </button>
      <button onClick={() => removeCategory(1)} data-testid="remove-category">
        Remove Category
      </button>
      <button onClick={() => setLocations(['New York', 'San Francisco'])} data-testid="set-locations">
        Set Locations
      </button>
      <button onClick={() => addLocation('Boston')} data-testid="add-location">
        Add Location
      </button>
      <button onClick={() => removeLocation('New York')} data-testid="remove-location">
        Remove Location
      </button>
      <button onClick={() => setExperienceLevels(['mid', 'senior'])} data-testid="set-experience">
        Set Experience
      </button>
      <button onClick={() => addExperienceLevel('junior')} data-testid="add-experience">
        Add Experience
      </button>
      <button onClick={() => removeExperienceLevel('mid')} data-testid="remove-experience">
        Remove Experience
      </button>
      <button onClick={() => setSalaryRange([50000, 100000])} data-testid="set-salary">
        Set Salary
      </button>
      <button onClick={() => setJobTypes([1, 2])} data-testid="set-job-types">
        Set Job Types
      </button>
      <button onClick={() => addJobType(3)} data-testid="add-job-type">
        Add Job Type
      </button>
      <button onClick={() => removeJobType(1)} data-testid="remove-job-type">
        Remove Job Type
      </button>
      <button onClick={() => setIsRemote(true)} data-testid="set-remote">
        Set Remote
      </button>
      <button onClick={() => clearFilters()} data-testid="clear-filters">
        Clear Filters
      </button>
      <button onClick={() => resetFilters()} data-testid="reset-filters">
        Reset Filters
      </button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <FilterProvider>
      <TestComponent />
    </FilterProvider>
  );
}

describe('FilterContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should provide initial state', () => {
    renderWithProvider();

    expect(screen.getByTestId('search-query')).toHaveTextContent('');
    expect(screen.getByTestId('categories')).toHaveTextContent('');
    expect(screen.getByTestId('locations')).toHaveTextContent('');
    expect(screen.getByTestId('experience-levels')).toHaveTextContent('');
    expect(screen.getByTestId('salary-range')).toHaveTextContent('0-200000');
    expect(screen.getByTestId('job-types')).toHaveTextContent('');
    expect(screen.getByTestId('is-remote')).toHaveTextContent('null');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('0');
    expect(screen.getByTestId('has-active-filters')).toHaveTextContent('false');
  });

  it('should handle search query', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-search').click();
    });

    expect(screen.getByTestId('search-query')).toHaveTextContent('developer');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
    expect(screen.getByTestId('has-active-filters')).toHaveTextContent('true');
  });

  it('should handle categories', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-categories').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('1,2');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle adding and removing categories', () => {
    renderWithProvider();

    // Set initial categories
    act(() => {
      screen.getByTestId('set-categories').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('1,2');

    // Add a category
    act(() => {
      screen.getByTestId('add-category').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('1,2,3');

    // Remove a category
    act(() => {
      screen.getByTestId('remove-category').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('2,3');
  });

  it('should not add duplicate categories', () => {
    renderWithProvider();

    // Set initial categories
    act(() => {
      screen.getByTestId('set-categories').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('1,2');

    // Try to add existing category
    act(() => {
      screen.getByTestId('add-category').click();
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('1,2,3');

    // Try to add category 1 again (should not be added)
    act(() => {
      screen.getByTestId('remove-category').click(); // This removes category 1
      screen.getByTestId('add-category').click(); // This adds category 3 again
    });

    expect(screen.getByTestId('categories')).toHaveTextContent('2,3'); // Should not have duplicates
  });

  it('should handle locations', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-locations').click();
    });

    expect(screen.getByTestId('locations')).toHaveTextContent('New York,San Francisco');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle adding and removing locations', () => {
    renderWithProvider();

    // Set initial locations
    act(() => {
      screen.getByTestId('set-locations').click();
    });

    expect(screen.getByTestId('locations')).toHaveTextContent('New York,San Francisco');

    // Add a location
    act(() => {
      screen.getByTestId('add-location').click();
    });

    expect(screen.getByTestId('locations')).toHaveTextContent('New York,San Francisco,Boston');

    // Remove a location
    act(() => {
      screen.getByTestId('remove-location').click();
    });

    expect(screen.getByTestId('locations')).toHaveTextContent('San Francisco,Boston');
  });

  it('should handle experience levels', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-experience').click();
    });

    expect(screen.getByTestId('experience-levels')).toHaveTextContent('mid,senior');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle adding and removing experience levels', () => {
    renderWithProvider();

    // Set initial experience levels
    act(() => {
      screen.getByTestId('set-experience').click();
    });

    expect(screen.getByTestId('experience-levels')).toHaveTextContent('mid,senior');

    // Add an experience level
    act(() => {
      screen.getByTestId('add-experience').click();
    });

    expect(screen.getByTestId('experience-levels')).toHaveTextContent('mid,senior,junior');

    // Remove an experience level
    act(() => {
      screen.getByTestId('remove-experience').click();
    });

    expect(screen.getByTestId('experience-levels')).toHaveTextContent('senior,junior');
  });

  it('should handle salary range', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-salary').click();
    });

    expect(screen.getByTestId('salary-range')).toHaveTextContent('50000-100000');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle job types', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-job-types').click();
    });

    expect(screen.getByTestId('job-types')).toHaveTextContent('1,2');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle adding and removing job types', () => {
    renderWithProvider();

    // Set initial job types
    act(() => {
      screen.getByTestId('set-job-types').click();
    });

    expect(screen.getByTestId('job-types')).toHaveTextContent('1,2');

    // Add a job type
    act(() => {
      screen.getByTestId('add-job-type').click();
    });

    expect(screen.getByTestId('job-types')).toHaveTextContent('1,2,3');

    // Remove a job type
    act(() => {
      screen.getByTestId('remove-job-type').click();
    });

    expect(screen.getByTestId('job-types')).toHaveTextContent('2,3');
  });

  it('should handle remote filter', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-remote').click();
    });

    expect(screen.getByTestId('is-remote')).toHaveTextContent('true');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');
  });

  it('should handle clearing filters', () => {
    renderWithProvider();

    // Set some filters
    act(() => {
      screen.getByTestId('set-search').click();
    });
    act(() => {
      screen.getByTestId('set-categories').click();
    });
    act(() => {
      screen.getByTestId('set-remote').click();
    });

    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('3');
    expect(screen.getByTestId('has-active-filters')).toHaveTextContent('true');

    // Clear filters
    act(() => {
      screen.getByTestId('clear-filters').click();
    });

    expect(screen.getByTestId('search-query')).toHaveTextContent('');
    expect(screen.getByTestId('categories')).toHaveTextContent('');
    expect(screen.getByTestId('locations')).toHaveTextContent('');
    expect(screen.getByTestId('experience-levels')).toHaveTextContent('');
    expect(screen.getByTestId('salary-range')).toHaveTextContent('0-200000');
    expect(screen.getByTestId('job-types')).toHaveTextContent('');
    expect(screen.getByTestId('is-remote')).toHaveTextContent('null');
    expect(screen.getByTestId('is-active')).toHaveTextContent('false');
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('0');
    expect(screen.getByTestId('has-active-filters')).toHaveTextContent('false');
  });

  it('should handle resetting filters', () => {
    renderWithProvider();

    // Set some filters
    act(() => {
      screen.getByTestId('set-search').click();
    });
    act(() => {
      screen.getByTestId('set-categories').click();
    });

    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('2');

    // Reset filters
    act(() => {
      screen.getByTestId('reset-filters').click();
    });

    expect(screen.getByTestId('search-query')).toHaveTextContent('');
    expect(screen.getByTestId('categories')).toHaveTextContent('');
    expect(screen.getByTestId('is-active')).toHaveTextContent('true'); // Reset should set isActive to true
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('0');
    expect(screen.getByTestId('has-active-filters')).toHaveTextContent('false');
  });

  it('should correctly count active filters', () => {
    renderWithProvider();

    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('0');

    // Add search query
    act(() => {
      screen.getByTestId('set-search').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('1');

    // Add categories
    act(() => {
      screen.getByTestId('set-categories').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('2');

    // Add locations
    act(() => {
      screen.getByTestId('set-locations').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('3');

    // Add experience levels
    act(() => {
      screen.getByTestId('set-experience').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('4');

    // Add salary range
    act(() => {
      screen.getByTestId('set-salary').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('5');

    // Add job types
    act(() => {
      screen.getByTestId('set-job-types').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('6');

    // Add remote filter
    act(() => {
      screen.getByTestId('set-remote').click();
    });
    expect(screen.getByTestId('active-filters-count')).toHaveTextContent('7');
  });

  it('should throw error when useFilter is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useFilter must be used within a FilterProvider');

    consoleSpy.mockRestore();
  });
});