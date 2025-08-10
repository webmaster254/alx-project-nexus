import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import type { FilterState, FilterAction, ExperienceLevel } from '../types';

// Initial state
const initialFilterState: FilterState = {
  searchQuery: '',
  categories: [],
  locations: [],
  experienceLevels: [],
  salaryRange: [0, 200000], // Default salary range
  jobTypes: [],
  isRemote: null, // null means no preference
  isActive: true,
};

// Reducer function
function filterReducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_SEARCH_QUERY':
      return {
        ...state,
        searchQuery: action.payload,
        isActive: action.payload.length > 0 || hasActiveFilters({ ...state, searchQuery: action.payload }),
      };

    case 'SET_CATEGORIES':
      return {
        ...state,
        categories: action.payload,
        isActive: action.payload.length > 0 || hasActiveFilters({ ...state, categories: action.payload }),
      };

    case 'SET_LOCATIONS':
      return {
        ...state,
        locations: action.payload,
        isActive: action.payload.length > 0 || hasActiveFilters({ ...state, locations: action.payload }),
      };

    case 'SET_EXPERIENCE_LEVELS':
      return {
        ...state,
        experienceLevels: action.payload,
        isActive: action.payload.length > 0 || hasActiveFilters({ ...state, experienceLevels: action.payload }),
      };

    case 'SET_SALARY_RANGE':
      return {
        ...state,
        salaryRange: action.payload,
        isActive: (action.payload[0] > 0 || action.payload[1] < 200000) || hasActiveFilters({ ...state, salaryRange: action.payload }),
      };

    case 'SET_JOB_TYPES':
      return {
        ...state,
        jobTypes: action.payload,
        isActive: action.payload.length > 0 || hasActiveFilters({ ...state, jobTypes: action.payload }),
      };

    case 'SET_IS_REMOTE':
      return {
        ...state,
        isRemote: action.payload,
        isActive: action.payload !== null || hasActiveFilters({ ...state, isRemote: action.payload }),
      };

    case 'SET_IS_ACTIVE':
      return {
        ...state,
        isActive: action.payload,
      };

    case 'CLEAR_FILTERS':
      return {
        ...initialFilterState,
        isActive: false,
      };

    case 'RESET_FILTERS':
      return initialFilterState;

    default:
      return state;
  }
}

// Helper function to check if any filters are active
function hasActiveFilters(state: FilterState): boolean {
  return (
    state.searchQuery.length > 0 ||
    state.categories.length > 0 ||
    state.locations.length > 0 ||
    state.experienceLevels.length > 0 ||
    state.salaryRange[0] > 0 ||
    state.salaryRange[1] < 200000 ||
    state.jobTypes.length > 0 ||
    state.isRemote !== null
  );
}

// Context type
interface FilterContextType {
  state: FilterState;
  dispatch: React.Dispatch<FilterAction>;
  // Helper functions
  setSearchQuery: (query: string) => void;
  setCategories: (categories: number[]) => void;
  addCategory: (categoryId: number) => void;
  removeCategory: (categoryId: number) => void;
  setLocations: (locations: string[]) => void;
  addLocation: (location: string) => void;
  removeLocation: (location: string) => void;
  setExperienceLevels: (levels: ExperienceLevel[]) => void;
  addExperienceLevel: (level: ExperienceLevel) => void;
  removeExperienceLevel: (level: ExperienceLevel) => void;
  setSalaryRange: (range: [number, number]) => void;
  setJobTypes: (types: number[]) => void;
  addJobType: (typeId: number) => void;
  removeJobType: (typeId: number) => void;
  setIsRemote: (isRemote: boolean | null) => void;
  clearFilters: () => void;
  resetFilters: () => void;
  getActiveFiltersCount: () => number;
  hasActiveFilters: () => boolean;
}

// Create context
export const FilterContext = createContext<FilterContextType | undefined>(undefined);

// Provider component
interface FilterProviderProps {
  children: ReactNode;
}

export function FilterProvider({ children }: FilterProviderProps) {
  const [state, dispatch] = useReducer(filterReducer, initialFilterState);

  // Helper functions - memoized to prevent re-creation
  const setSearchQuery = useCallback((query: string) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: query });
  }, []);

  const setCategories = useCallback((categories: number[]) => {
    dispatch({ type: 'SET_CATEGORIES', payload: categories });
  }, []);

  const addCategory = useCallback((categoryId: number) => {
    if (!state.categories.includes(categoryId)) {
      dispatch({ type: 'SET_CATEGORIES', payload: [...state.categories, categoryId] });
    }
  }, [state.categories]);

  const removeCategory = useCallback((categoryId: number) => {
    dispatch({ type: 'SET_CATEGORIES', payload: state.categories.filter(id => id !== categoryId) });
  }, [state.categories]);

  const setLocations = useCallback((locations: string[]) => {
    dispatch({ type: 'SET_LOCATIONS', payload: locations });
  }, []);

  const addLocation = useCallback((location: string) => {
    if (!state.locations.includes(location)) {
      dispatch({ type: 'SET_LOCATIONS', payload: [...state.locations, location] });
    }
  }, [state.locations]);

  const removeLocation = useCallback((location: string) => {
    dispatch({ type: 'SET_LOCATIONS', payload: state.locations.filter(loc => loc !== location) });
  }, [state.locations]);

  const setExperienceLevels = useCallback((levels: ExperienceLevel[]) => {
    dispatch({ type: 'SET_EXPERIENCE_LEVELS', payload: levels });
  }, []);

  const addExperienceLevel = useCallback((level: ExperienceLevel) => {
    if (!state.experienceLevels.includes(level)) {
      dispatch({ type: 'SET_EXPERIENCE_LEVELS', payload: [...state.experienceLevels, level] });
    }
  }, [state.experienceLevels]);

  const removeExperienceLevel = useCallback((level: ExperienceLevel) => {
    dispatch({ type: 'SET_EXPERIENCE_LEVELS', payload: state.experienceLevels.filter(l => l !== level) });
  }, [state.experienceLevels]);

  const setSalaryRange = useCallback((range: [number, number]) => {
    dispatch({ type: 'SET_SALARY_RANGE', payload: range });
  }, []);

  const setJobTypes = useCallback((types: number[]) => {
    dispatch({ type: 'SET_JOB_TYPES', payload: types });
  }, []);

  const addJobType = useCallback((typeId: number) => {
    if (!state.jobTypes.includes(typeId)) {
      dispatch({ type: 'SET_JOB_TYPES', payload: [...state.jobTypes, typeId] });
    }
  }, [state.jobTypes]);

  const removeJobType = useCallback((typeId: number) => {
    dispatch({ type: 'SET_JOB_TYPES', payload: state.jobTypes.filter(id => id !== typeId) });
  }, [state.jobTypes]);

  const setIsRemote = useCallback((isRemote: boolean | null) => {
    dispatch({ type: 'SET_IS_REMOTE', payload: isRemote });
  }, []);

  const clearFilters = useCallback(() => {
    dispatch({ type: 'CLEAR_FILTERS' });
  }, []);

  const resetFilters = useCallback(() => {
    dispatch({ type: 'RESET_FILTERS' });
  }, []);

  const getActiveFiltersCount = useCallback((): number => {
    let count = 0;
    if ((state.searchQuery || '').length > 0) count++;
    if ((state.categories || []).length > 0) count++;
    if ((state.locations || []).length > 0) count++;
    if ((state.experienceLevels || []).length > 0) count++;
    if ((state.salaryRange || [0, 200000])[0] > 0 || (state.salaryRange || [0, 200000])[1] < 200000) count++;
    if ((state.jobTypes || []).length > 0) count++;
    if (state.isRemote !== null) count++;
    return count;
  }, [state.searchQuery, state.categories, state.locations, state.experienceLevels, state.salaryRange, state.jobTypes, state.isRemote]);

  const hasActiveFiltersFunc = useCallback((): boolean => {
    return hasActiveFilters(state);
  }, [state]);

  const value: FilterContextType = {
    state,
    dispatch,
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
    hasActiveFilters: hasActiveFiltersFunc,
  };

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

// Custom hook to use the FilterContext
export function useFilter() {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilter must be used within a FilterProvider');
  }
  return context;
}