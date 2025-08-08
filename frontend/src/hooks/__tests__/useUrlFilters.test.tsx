import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import { useUrlFilters } from '../useUrlFilters';
import { FilterProvider } from '../../contexts/FilterContext';

// Mock the FilterContext
const mockDispatch = vi.fn();
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

vi.mock('../../contexts/FilterContext', () => ({
  useFilter: () => ({
    state: mockFilterState,
    dispatch: mockDispatch,
  }),
  FilterProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Wrapper component for testing
const TestWrapper: React.FC<{ children: React.ReactNode; initialUrl?: string }> = ({ 
  children, 
  initialUrl = '/' 
}) => {
  // Set initial URL
  if (initialUrl !== '/') {
    window.history.pushState({}, '', initialUrl);
  }
  
  return (
    <BrowserRouter>
      <FilterProvider>
        {children}
      </FilterProvider>
    </BrowserRouter>
  );
};

describe('useUrlFilters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset URL
    window.history.pushState({}, '', '/');
  });

  it('should initialize without URL parameters', () => {
    const { result } = renderHook(() => useUrlFilters(), {
      wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
    });

    expect(result.current.hasUrlParams()).toBe(false);
    expect(result.current.getUrlParams()).toEqual({});
  });

  it('should initialize filters from URL parameters', () => {
    const initialUrl = '/?q=developer&categories=1,2&locations=New%20York&experience=mid,senior&salary_min=50000&salary_max=100000&remote=true';
    
    renderHook(() => useUrlFilters(), {
      wrapper: ({ children }) => <TestWrapper initialUrl={initialUrl}>{children}</TestWrapper>,
    });

    // Verify that dispatch was called with URL parameters
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_SEARCH_QUERY', payload: 'developer' });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_CATEGORIES', payload: [1, 2] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_LOCATIONS', payload: ['New York'] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_EXPERIENCE_LEVELS', payload: ['mid', 'senior'] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_SALARY_RANGE', payload: [50000, 100000] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_IS_REMOTE', payload: true });
  });

  it('should provide utility functions', () => {
    const { result } = renderHook(() => useUrlFilters(), {
      wrapper: ({ children }) => <TestWrapper>{children}</TestWrapper>,
    });

    expect(typeof result.current.clearUrlParams).toBe('function');
    expect(typeof result.current.getUrlParams).toBe('function');
    expect(typeof result.current.hasUrlParams).toBe('function');
  });

  it('should handle URL parameters with special characters', () => {
    const initialUrl = '/?q=software%20engineer&locations=San%20Francisco';
    
    renderHook(() => useUrlFilters(), {
      wrapper: ({ children }) => <TestWrapper initialUrl={initialUrl}>{children}</TestWrapper>,
    });

    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_SEARCH_QUERY', payload: 'software engineer' });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_LOCATIONS', payload: ['San Francisco'] });
  });

  it('should handle empty and invalid URL parameters', () => {
    const initialUrl = '/?q=&categories=&experience=invalid&salary_min=abc&remote=maybe';
    
    renderHook(() => useUrlFilters(), {
      wrapper: ({ children }) => <TestWrapper initialUrl={initialUrl}>{children}</TestWrapper>,
    });

    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_SEARCH_QUERY', payload: '' });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_CATEGORIES', payload: [] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_EXPERIENCE_LEVELS', payload: ['invalid'] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_SALARY_RANGE', payload: [0, 200000] });
    expect(mockDispatch).toHaveBeenCalledWith({ type: 'SET_IS_REMOTE', payload: false });
  });
});