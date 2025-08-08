import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import SearchBar from '../SearchBar';
import { FilterProvider } from '../../../contexts/FilterContext';

// Mock the FilterContext
const mockSetSearchQuery = vi.fn();
const mockFilterState = {
  searchQuery: '',
  categories: [],
  locations: [],
  experienceLevels: [],
  salaryRange: [0, 200000] as [number, number],
  jobTypes: [],
  isRemote: null,
  isActive: false,
};

vi.mock('../../../contexts/FilterContext', async () => {
  const actual = await vi.importActual('../../../contexts/FilterContext');
  return {
    ...actual,
    useFilter: () => ({
      state: mockFilterState,
      setSearchQuery: mockSetSearchQuery,
    }),
  };
});

const renderSearchBar = (props = {}) => {
  return render(
    <FilterProvider>
      <SearchBar {...props} />
    </FilterProvider>
  );
};

describe('SearchBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with default placeholder', () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'Search jobs by title, company, or keywords...');
  });

  it('renders with custom placeholder', () => {
    const customPlaceholder = 'Custom search placeholder';
    renderSearchBar({ placeholder: customPlaceholder });
    
    const input = screen.getByRole('searchbox');
    expect(input).toHaveAttribute('placeholder', customPlaceholder);
  });

  it('displays search icon', () => {
    renderSearchBar();
    
    const searchIcon = screen.getByRole('searchbox').parentElement?.querySelector('svg');
    expect(searchIcon).toBeInTheDocument();
  });

  it('updates local state when typing', () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'developer' } });
    
    expect(input).toHaveValue('developer');
  });

  it('calls setSearchQuery with debounced input', async () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'developer' } });
    
    // Should not call immediately
    expect(mockSetSearchQuery).not.toHaveBeenCalled();
    
    // Should call after debounce delay
    await waitFor(() => {
      expect(mockSetSearchQuery).toHaveBeenCalledWith('developer');
    }, { timeout: 500 });
  });

  it('calls setSearchQuery immediately on Enter key', async () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    // Should call immediately without waiting for debounce
    expect(mockSetSearchQuery).toHaveBeenCalledWith('developer');
  });

  it('shows clear button when there is text', () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'developer' } });
    
    const clearButton = screen.getByLabelText('Clear search');
    expect(clearButton).toBeInTheDocument();
  });

  it('clears input when clear button is clicked', () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    fireEvent.change(input, { target: { value: 'developer' } });
    
    const clearButton = screen.getByLabelText('Clear search');
    fireEvent.click(clearButton);
    
    expect(input).toHaveValue('');
    expect(mockSetSearchQuery).toHaveBeenCalledWith('');
  });

  it('has proper accessibility attributes', () => {
    renderSearchBar();
    
    const input = screen.getByRole('searchbox');
    expect(input).toHaveAttribute('aria-label', 'Search jobs');
    expect(input).toHaveAttribute('aria-describedby', 'search-description');
    
    const description = screen.getByText(/Search for jobs by entering keywords/);
    expect(description).toHaveClass('sr-only');
  });

  it('applies custom className', () => {
    const customClass = 'custom-search-class';
    renderSearchBar({ className: customClass });
    
    const container = screen.getByRole('searchbox').closest('.relative')?.parentElement;
    expect(container).toHaveClass(customClass);
  });
});