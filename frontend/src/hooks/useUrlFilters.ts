import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFilter } from '../contexts/FilterContext';
import type { ExperienceLevel } from '../types';

/**
 * Custom hook to synchronize filter state with URL parameters
 */
export function useUrlFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { state, dispatch } = useFilter();

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();

    // Add search query
    if (state.searchQuery) {
      params.set('q', state.searchQuery);
    }

    // Add categories
    if (state.categories.length > 0) {
      params.set('categories', state.categories.join(','));
    }

    // Add locations
    if (state.locations.length > 0) {
      params.set('locations', state.locations.join(','));
    }

    // Add experience levels
    if (state.experienceLevels.length > 0) {
      params.set('experience', state.experienceLevels.join(','));
    }

    // Add salary range
    if (state.salaryRange[0] > 0) {
      params.set('salary_min', state.salaryRange[0].toString());
    }
    if (state.salaryRange[1] < 200000) {
      params.set('salary_max', state.salaryRange[1].toString());
    }

    // Add job types
    if (state.jobTypes.length > 0) {
      params.set('job_types', state.jobTypes.join(','));
    }

    // Add remote preference
    if (state.isRemote !== null) {
      params.set('remote', state.isRemote.toString());
    }

    // Update URL without triggering navigation
    setSearchParams(params, { replace: true });
  }, [
    state.searchQuery,
    state.categories,
    state.locations,
    state.experienceLevels,
    state.salaryRange,
    state.jobTypes,
    state.isRemote,
    setSearchParams
  ]);

  // Initialize filters from URL on mount
  useEffect(() => {
    const initializeFromUrl = () => {
      const searchQuery = searchParams.get('q') || '';
      const categories = searchParams.get('categories')?.split(',').map(Number).filter(Boolean) || [];
      const locations = searchParams.get('locations')?.split(',').filter(Boolean) || [];
      const experienceLevels = searchParams.get('experience')?.split(',').filter(Boolean) as ExperienceLevel[] || [];
      const salaryMin = Number(searchParams.get('salary_min')) || 0;
      const salaryMax = Number(searchParams.get('salary_max')) || 200000;
      const jobTypes = searchParams.get('job_types')?.split(',').map(Number).filter(Boolean) || [];
      const remoteParam = searchParams.get('remote');
      const isRemote = remoteParam === null ? null : remoteParam === 'true';

      // Only update if there are URL parameters to avoid overriding initial state
      const hasUrlParams = searchParams.toString().length > 0;
      
      if (hasUrlParams) {
        // Update all filters at once to avoid multiple re-renders
        dispatch({ type: 'SET_SEARCH_QUERY', payload: searchQuery });
        dispatch({ type: 'SET_CATEGORIES', payload: categories });
        dispatch({ type: 'SET_LOCATIONS', payload: locations });
        dispatch({ type: 'SET_EXPERIENCE_LEVELS', payload: experienceLevels });
        dispatch({ type: 'SET_SALARY_RANGE', payload: [salaryMin, salaryMax] });
        dispatch({ type: 'SET_JOB_TYPES', payload: jobTypes });
        dispatch({ type: 'SET_IS_REMOTE', payload: isRemote });
      }
    };

    initializeFromUrl();
  }, []); // Only run on mount

  return {
    /**
     * Clear all URL parameters
     */
    clearUrlParams: () => {
      setSearchParams({}, { replace: true });
    },

    /**
     * Get current URL parameters as an object
     */
    getUrlParams: () => {
      const params: Record<string, string> = {};
      searchParams.forEach((value, key) => {
        params[key] = value;
      });
      return params;
    },

    /**
     * Check if there are any active URL parameters
     */
    hasUrlParams: () => {
      return searchParams.toString().length > 0;
    }
  };
}