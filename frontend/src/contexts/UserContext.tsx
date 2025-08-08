import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { authService } from '../services';
import type { UserState, UserAction, User } from '../types';

// Initial state
const initialUserState: UserState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  token: null,
};

// Reducer function
function userReducer(state: UserState, action: UserAction): UserState {
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

    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: action.payload,
        isLoading: false,
        error: null,
      };

    case 'SET_TOKEN':
      return {
        ...state,
        token: action.payload,
        isAuthenticated: !!action.payload,
      };

    case 'LOGOUT':
      // Clear all user data and token from localStorage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      return {
        ...initialUserState,
        isLoading: false,
      };

    case 'RESET_STATE':
      return initialUserState;

    default:
      return state;
  }
}

// Context type
interface UserContextType {
  state: UserState;
  dispatch: React.Dispatch<UserAction>;
  // Helper functions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setUser: (user: User | null) => void;
  setAuthenticated: (authenticated: boolean) => void;
  setToken: (token: string | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  resetState: () => void;
  initializeAuth: () => void;
}

// Create context
const UserContext = createContext<UserContextType | undefined>(undefined);

// Provider component
interface UserProviderProps {
  children: ReactNode;
}

export function UserProvider({ children }: UserProviderProps) {
  const [state, dispatch] = useReducer(userReducer, initialUserState);

  // Initialize authentication state from localStorage on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  // Helper functions
  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const setUser = (user: User | null) => {
    dispatch({ type: 'SET_USER', payload: user });
    
    // Persist user data to localStorage
    if (user) {
      localStorage.setItem('user_data', JSON.stringify(user));
    } else {
      localStorage.removeItem('user_data');
    }
  };

  const setAuthenticated = (authenticated: boolean) => {
    dispatch({ type: 'SET_AUTHENTICATED', payload: authenticated });
  };

  const setToken = (token: string | null) => {
    dispatch({ type: 'SET_TOKEN', payload: token });
    
    // Persist token to localStorage
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  };

  const login = (user: User, token: string) => {
    // Set both user and token
    setUser(user);
    setToken(token);
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (state.user) {
      const updatedUser = { ...state.user, ...userData };
      setUser(updatedUser);
    }
  };

  const resetState = () => {
    dispatch({ type: 'RESET_STATE' });
  };

  const initializeAuth = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('user_data');

      if (token && userData) {
        // Check if token is still valid
        if (authService.isAuthenticated()) {
          const user = JSON.parse(userData) as User;
          dispatch({ type: 'SET_TOKEN', payload: token });
          dispatch({ type: 'SET_USER', payload: user });
          
          // Initialize auth service for automatic token refresh
          authService.initializeAuth();
          
          // Fetch fresh user data to ensure it's up to date
          try {
            const response = await authService.getCurrentUser();
            setUser(response.data);
          } catch (error) {
            console.warn('Failed to fetch fresh user data:', error);
            // Continue with cached user data
          }
        } else {
          // Token is expired, try to refresh
          try {
            await authService.refreshToken();
            const refreshedToken = authService.getAccessToken();
            if (refreshedToken) {
              const user = JSON.parse(userData) as User;
              dispatch({ type: 'SET_TOKEN', payload: refreshedToken });
              dispatch({ type: 'SET_USER', payload: user });
              
              // Fetch fresh user data
              const response = await authService.getCurrentUser();
              setUser(response.data);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            // Clear invalid tokens
            localStorage.removeItem('auth_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_data');
          }
        }
      }
    } catch (error) {
      console.error('Error initializing auth state:', error);
      // Clear potentially corrupted data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
    } finally {
      setLoading(false);
    }
  };

  const value: UserContextType = {
    state,
    dispatch,
    setLoading,
    setError,
    setUser,
    setAuthenticated,
    setToken,
    login,
    logout,
    updateUser,
    resetState,
    initializeAuth,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

// Custom hook to use the UserContext
export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}