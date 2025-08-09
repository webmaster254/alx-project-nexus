import { renderHook, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { useUrlFilters } from '../useUrlFilters';

// Mock useNavigate and useLocation
const mockNavigate = vi.fn();
const mockLocation = {
  search: '',
  pathname: '/jobs',
  hash: '',
  state: null,
  key: 'default',
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('useUrlFilters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocation.search = '';
  });

  it('initializes with empty filters when no URL params', () => {
    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters).toEqual({
      searchQuery: '',
      categories: [],
      locations: [],
      experienceLevels: [],
      salaryRange: [0, 200000],
      jobTypes: [],
      isRemote: null,
      isActive: true,
    });
  });

  it('parses URL parameters correctly', () => {
    mockLocation.search = '?search=developer&category=1,2&location=New York&experience_level=mid,senior&is_remote=true&salary_min=50000&salary_max=100000';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters).toEqual({
      searchQuery: 'developer',
      categories: [1, 2],
      locations: ['New York'],
      experienceLevels: ['mid', 'senior'],
      salaryRange: [50000, 100000],
      jobTypes: [],
      isRemote: true,
      isActive: true,
    });
  });

  it('updates URL when filters change', () => {
    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    act(() => {
      result.current.updateFilters({
        searchQuery: 'engineer',
        categories: [1],
        locations: ['San Francisco'],
        experienceLevels: ['senior'],
        salaryRange: [80000, 150000],
        jobTypes: [1, 2],
        isRemote: true,
        isActive: true,
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/jobs',
      search: '?search=engineer&category=1&location=San%20Francisco&experience_level=senior&salary_min=80000&salary_max=150000&job_type=1%2C2&is_remote=true',
    });
  });

  it('removes empty parameters from URL', () => {
    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    act(() => {
      result.current.updateFilters({
        searchQuery: '',
        categories: [],
        locations: [],
        experienceLevels: [],
        salaryRange: [0, 200000],
        jobTypes: [],
        isRemote: null,
        isActive: true,
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/jobs',
      search: '',
    });
  });

  it('handles special characters in search query', () => {
    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    act(() => {
      result.current.updateFilters({
        searchQuery: 'C++ developer & architect',
        categories: [],
        locations: [],
        experienceLevels: [],
        salaryRange: [0, 200000],
        jobTypes: [],
        isRemote: null,
        isActive: true,
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/jobs',
      search: '?search=C%2B%2B%20developer%20%26%20architect',
    });
  });

  it('handles multiple locations correctly', () => {
    mockLocation.search = '?location=New York,San Francisco,Boston';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters.locations).toEqual(['New York', 'San Francisco', 'Boston']);
  });

  it('handles invalid salary range gracefully', () => {
    mockLocation.search = '?salary_min=invalid&salary_max=also_invalid';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters.salaryRange).toEqual([0, 200000]);
  });

  it('handles boolean parameters correctly', () => {
    mockLocation.search = '?is_remote=false';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters.isRemote).toBe(false);
  });

  it('clears filters correctly', () => {
    mockLocation.search = '?search=developer&category=1&is_remote=true';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    act(() => {
      result.current.clearFilters();
    });

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/jobs',
      search: '',
    });
  });

  it('preserves pathname when updating filters', () => {
    mockLocation.pathname = '/jobs/search';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    act(() => {
      result.current.updateFilters({
        searchQuery: 'developer',
        categories: [],
        locations: [],
        experienceLevels: [],
        salaryRange: [0, 200000],
        jobTypes: [],
        isRemote: null,
        isActive: true,
      });
    });

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/jobs/search',
      search: '?search=developer',
    });
  });

  it('handles array parameters with single values', () => {
    mockLocation.search = '?category=1&experience_level=senior';

    const { result } = renderHook(() => useUrlFilters(), { wrapper });

    expect(result.current.filters.categories).toEqual([1]);
    expect(result.current.filters.experienceLevels).toEqual(['senior']);
  });
});