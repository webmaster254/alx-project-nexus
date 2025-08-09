import React, { createContext, useContext, useReducer, ReactNode, useCallback } from 'react';
import { bookmarkService, BookmarkedJob } from '../services/bookmarkService';
import type { BookmarkState } from '../types';

// Initial state
const initialBookmarkState: BookmarkState = {
  bookmarkedJobs: [],
  isLoading: false,
  error: null,
};

// Action types
type BookmarkAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_BOOKMARKED_JOBS'; payload: number[] }
  | { type: 'ADD_BOOKMARK'; payload: number }
  | { type: 'REMOVE_BOOKMARK'; payload: number }
  | { type: 'RESET_STATE' };

// Reducer function
function bookmarkReducer(state: BookmarkState, action: BookmarkAction): BookmarkState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
        error: action.payload ? null : state.error,
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case 'SET_BOOKMARKED_JOBS':
      return {
        ...state,
        bookmarkedJobs: action.payload,
        isLoading: false,
        error: null,
      };

    case 'ADD_BOOKMARK':
      return {
        ...state,
        bookmarkedJobs: [...state.bookmarkedJobs, action.payload],
        isLoading: false,
        error: null,
      };

    case 'REMOVE_BOOKMARK':
      return {
        ...state,
        bookmarkedJobs: state.bookmarkedJobs.filter(id => id !== action.payload),
        isLoading: false,
        error: null,
      };

    case 'RESET_STATE':
      return initialBookmarkState;

    default:
      return state;
  }
}

// Context type
interface BookmarkContextType {
  state: BookmarkState;
  dispatch: React.Dispatch<BookmarkAction>;
  // Helper functions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  isJobBookmarked: (jobId: number) => boolean;
  // API actions
  loadBookmarkedJobs: () => Promise<void>;
  toggleBookmark: (jobId: number) => Promise<boolean>;
  addBookmark: (jobId: number) => Promise<void>;
  removeBookmark: (jobId: number) => Promise<void>;
}

// Create context
export const BookmarkContext = createContext<BookmarkContextType | undefined>(undefined);

// Provider component
interface BookmarkProviderProps {
  children: ReactNode;
}

export function BookmarkProvider({ children }: BookmarkProviderProps) {
  const [state, dispatch] = useReducer(bookmarkReducer, initialBookmarkState);

  // Helper functions
  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const isJobBookmarked = useCallback((jobId: number): boolean => {
    return state.bookmarkedJobs.includes(jobId);
  }, [state.bookmarkedJobs]);

  // API actions
  const loadBookmarkedJobs = useCallback(async () => {
    try {
      setLoading(true);
      const bookmarkedJobs = await bookmarkService.getBookmarkedJobs();
      const jobIds = bookmarkedJobs.map((bookmark: BookmarkedJob) => bookmark.job.id);
      dispatch({ type: 'SET_BOOKMARKED_JOBS', payload: jobIds });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load bookmarked jobs');
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  const toggleBookmark = useCallback(async (jobId: number): Promise<boolean> => {
    try {
      const result = await bookmarkService.toggleBookmark(jobId);
      
      if (result.bookmarked) {
        dispatch({ type: 'ADD_BOOKMARK', payload: jobId });
      } else {
        dispatch({ type: 'REMOVE_BOOKMARK', payload: jobId });
      }
      
      return result.bookmarked;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to toggle bookmark');
      throw error;
    }
  }, [setError]);

  const addBookmark = useCallback(async (jobId: number) => {
    try {
      setLoading(true);
      await bookmarkService.bookmarkJob(jobId);
      dispatch({ type: 'ADD_BOOKMARK', payload: jobId });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to bookmark job');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  const removeBookmark = useCallback(async (jobId: number) => {
    try {
      setLoading(true);
      await bookmarkService.removeBookmark(jobId);
      dispatch({ type: 'REMOVE_BOOKMARK', payload: jobId });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to remove bookmark');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  const value: BookmarkContextType = {
    state,
    dispatch,
    setLoading,
    setError,
    isJobBookmarked,
    loadBookmarkedJobs,
    toggleBookmark,
    addBookmark,
    removeBookmark,
  };

  return <BookmarkContext.Provider value={value}>{children}</BookmarkContext.Provider>;
}

// Custom hook to use the BookmarkContext
export function useBookmark() {
  const context = useContext(BookmarkContext);
  if (context === undefined) {
    throw new Error('useBookmark must be used within a BookmarkProvider');
  }
  return context;
}