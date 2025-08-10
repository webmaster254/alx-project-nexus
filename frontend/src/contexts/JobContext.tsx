import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import type { JobState, JobAction, Job, PaginatedResponse, JobListParams } from '../types';
import { jobService } from '../services/jobService';

// Initial state
const initialJobState: JobState = {
  jobs: [],
  currentJob: null,
  featuredJobs: [],
  recentJobs: [],
  similarJobs: [],
  totalCount: 0,
  currentPage: 1,
  hasNextPage: false,
  hasPreviousPage: false,
  isLoading: false,
  error: null,
};

// Reducer function
function jobReducer(state: JobState, action: JobAction): JobState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
        error: action.payload ? null : state.error, // Clear error when starting to load
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case 'SET_JOBS':
      return {
        ...state,
        jobs: action.payload.jobs,
        totalCount: action.payload.totalCount,
        currentPage: action.payload.currentPage,
        hasNextPage: action.payload.hasNextPage,
        hasPreviousPage: action.payload.hasPreviousPage,
        isLoading: false,
        error: null,
      };

    case 'SET_CURRENT_JOB':
      return {
        ...state,
        currentJob: action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_FEATURED_JOBS':
      return {
        ...state,
        featuredJobs: action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_RECENT_JOBS':
      return {
        ...state,
        recentJobs: action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_SIMILAR_JOBS':
      return {
        ...state,
        similarJobs: action.payload,
        isLoading: false,
        error: null,
      };

    case 'APPEND_JOBS':
      return {
        ...state,
        jobs: [...state.jobs, ...action.payload],
        isLoading: false,
        error: null,
      };

    case 'CLEAR_JOBS':
      return {
        ...state,
        jobs: [],
        totalCount: 0,
        currentPage: 1,
        hasNextPage: false,
        hasPreviousPage: false,
      };

    case 'RESET_STATE':
      return initialJobState;

    default:
      return state;
  }
}

// Context type
interface JobContextType {
  state: JobState;
  dispatch: React.Dispatch<JobAction>;
  // Helper functions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setJobs: (response: PaginatedResponse<Job>, page?: number) => void;
  setCurrentJob: (job: Job | null) => void;
  setFeaturedJobs: (jobs: Job[]) => void;
  setRecentJobs: (jobs: Job[]) => void;
  setSimilarJobs: (jobs: Job[]) => void;
  appendJobs: (jobs: Job[]) => void;
  clearJobs: () => void;
  resetState: () => void;
  // API actions
  fetchJobs: (params: JobListParams, append?: boolean) => Promise<void>;
  fetchJob: (id: number) => Promise<void>;
  fetchSimilarJobs: (jobId: number) => Promise<void>;
}

// Create context
export const JobContext = createContext<JobContextType | undefined>(undefined);

// Provider component
interface JobProviderProps {
  children: ReactNode;
}

export function JobProvider({ children }: JobProviderProps) {
  const [state, dispatch] = useReducer(jobReducer, initialJobState);

  // Helper functions - memoized to prevent re-creation
  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const setJobs = useCallback((response: PaginatedResponse<Job>, page: number = 1) => {
    dispatch({
      type: 'SET_JOBS',
      payload: {
        jobs: response.results,
        totalCount: response.count,
        currentPage: page,
        hasNextPage: !!response.next,
        hasPreviousPage: !!response.previous,
      },
    });
  }, []);

  const setCurrentJob = useCallback((job: Job | null) => {
    dispatch({ type: 'SET_CURRENT_JOB', payload: job });
  }, []);

  const setFeaturedJobs = useCallback((jobs: Job[]) => {
    dispatch({ type: 'SET_FEATURED_JOBS', payload: jobs });
  }, []);

  const setRecentJobs = useCallback((jobs: Job[]) => {
    dispatch({ type: 'SET_RECENT_JOBS', payload: jobs });
  }, []);

  const setSimilarJobs = useCallback((jobs: Job[]) => {
    dispatch({ type: 'SET_SIMILAR_JOBS', payload: jobs });
  }, []);

  const appendJobs = useCallback((jobs: Job[]) => {
    dispatch({ type: 'APPEND_JOBS', payload: jobs });
  }, []);

  const clearJobs = useCallback(() => {
    dispatch({ type: 'CLEAR_JOBS' });
  }, []);

  const resetState = useCallback(() => {
    dispatch({ type: 'RESET_STATE' });
  }, []);

  // API actions - memoized to prevent infinite re-renders
  const fetchJobs = useCallback(async (params: JobListParams, append: boolean = false) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await jobService.getJobs(params);
      
      if (append) {
        dispatch({ type: 'APPEND_JOBS', payload: response.results });
      } else {
        dispatch({
          type: 'SET_JOBS',
          payload: {
            jobs: response.results,
            totalCount: response.count,
            currentPage: params.page || 1,
            hasNextPage: !!response.next,
            hasPreviousPage: !!response.previous,
          },
        });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to fetch jobs' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const fetchJob = useCallback(async (id: number) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const job = await jobService.getJob(id);
      dispatch({ type: 'SET_CURRENT_JOB', payload: job });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to fetch job details' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const fetchSimilarJobs = useCallback(async (jobId: number) => {
    try {
      const similarJobs = await jobService.getSimilarJobs(jobId);
      dispatch({ type: 'SET_SIMILAR_JOBS', payload: similarJobs });
    } catch (error) {
      // Don't set global error for similar jobs failure
      console.warn('Failed to fetch similar jobs:', error);
    }
  }, []);

  const value: JobContextType = {
    state,
    dispatch,
    setLoading,
    setError,
    setJobs,
    setCurrentJob,
    setFeaturedJobs,
    setRecentJobs,
    setSimilarJobs,
    appendJobs,
    clearJobs,
    resetState,
    fetchJobs,
    fetchJob,
    fetchSimilarJobs,
  };

  return <JobContext.Provider value={value}>{children}</JobContext.Provider>;
}

// Custom hook to use the JobContext
export function useJob() {
  const context = useContext(JobContext);
  if (context === undefined) {
    throw new Error('useJob must be used within a JobProvider');
  }
  return context;
}