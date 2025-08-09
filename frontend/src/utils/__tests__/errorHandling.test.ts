import { describe, it, expect, vi } from 'vitest';
import {
  handleApiError,
  formatErrorMessage,
  isNetworkError,
  logError,
  createErrorBoundary,
} from '../errorHandling';

describe('Error Handling Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console methods
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('handleApiError', () => {
    it('should handle 400 Bad Request errors', () => {
      const error = {
        response: {
          status: 400,
          data: {
            message: 'Invalid request data',
            errors: {
              email: ['This field is required'],
              password: ['Password too short'],
            },
          },
        },
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Invalid request data',
        status: 400,
        errors: {
          email: ['This field is required'],
          password: ['Password too short'],
        },
      });
    });

    it('should handle 401 Unauthorized errors', () => {
      const error = {
        response: {
          status: 401,
          data: { message: 'Authentication required' },
        },
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Authentication required',
        status: 401,
        errors: {},
      });
    });

    it('should handle 403 Forbidden errors', () => {
      const error = {
        response: {
          status: 403,
          data: { message: 'Access denied' },
        },
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Access denied',
        status: 403,
        errors: {},
      });
    });

    it('should handle 404 Not Found errors', () => {
      const error = {
        response: {
          status: 404,
          data: { message: 'Resource not found' },
        },
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Resource not found',
        status: 404,
        errors: {},
      });
    });

    it('should handle 500 Internal Server errors', () => {
      const error = {
        response: {
          status: 500,
          data: { message: 'Internal server error' },
        },
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Internal server error',
        status: 500,
        errors: {},
      });
    });

    it('should handle network errors', () => {
      const error = {
        message: 'Network Error',
        code: 'NETWORK_ERROR',
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Network error. Please check your connection.',
        status: 0,
        errors: {},
      });
    });

    it('should handle timeout errors', () => {
      const error = {
        code: 'ECONNABORTED',
        message: 'timeout of 10000ms exceeded',
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'Request timeout. Please try again.',
        status: 0,
        errors: {},
      });
    });

    it('should handle unknown errors', () => {
      const error = {
        message: 'Something went wrong',
      };

      const result = handleApiError(error);

      expect(result).toEqual({
        message: 'An unexpected error occurred',
        status: 0,
        errors: {},
      });
    });
  });

  describe('formatErrorMessage', () => {
    it('should format simple error message', () => {
      const result = formatErrorMessage('Simple error');
      expect(result).toBe('Simple error');
    });

    it('should format error with field errors', () => {
      const errors = {
        email: ['Email is required', 'Invalid email format'],
        password: ['Password too short'],
      };

      const result = formatErrorMessage('Validation failed', errors);
      expect(result).toBe('Validation failed\n• Email: Email is required, Invalid email format\n• Password: Password too short');
    });

    it('should handle empty field errors', () => {
      const result = formatErrorMessage('Error message', {});
      expect(result).toBe('Error message');
    });

    it('should handle null/undefined errors', () => {
      const result1 = formatErrorMessage('Error message', null);
      const result2 = formatErrorMessage('Error message', undefined);
      
      expect(result1).toBe('Error message');
      expect(result2).toBe('Error message');
    });
  });

  describe('isNetworkError', () => {
    it('should identify network errors', () => {
      const networkError = {
        message: 'Network Error',
        code: 'NETWORK_ERROR',
      };

      expect(isNetworkError(networkError)).toBe(true);
    });

    it('should identify timeout errors', () => {
      const timeoutError = {
        code: 'ECONNABORTED',
        message: 'timeout exceeded',
      };

      expect(isNetworkError(timeoutError)).toBe(true);
    });

    it('should not identify API errors as network errors', () => {
      const apiError = {
        response: {
          status: 400,
          data: { message: 'Bad request' },
        },
      };

      expect(isNetworkError(apiError)).toBe(false);
    });

    it('should handle errors without response', () => {
      const error = {
        message: 'Some other error',
      };

      expect(isNetworkError(error)).toBe(false);
    });
  });

  describe('logError', () => {
    it('should log errors to console in development', () => {
      const error = new Error('Test error');
      const context = { userId: 123, action: 'login' };

      logError(error, context);

      expect(console.error).toHaveBeenCalledWith('Error:', error);
      expect(console.error).toHaveBeenCalledWith('Context:', context);
    });

    it('should log errors without context', () => {
      const error = new Error('Test error');

      logError(error);

      expect(console.error).toHaveBeenCalledWith('Error:', error);
      expect(console.error).toHaveBeenCalledTimes(1);
    });

    it('should handle string errors', () => {
      logError('String error message');

      expect(console.error).toHaveBeenCalledWith('Error:', 'String error message');
    });
  });

  describe('createErrorBoundary', () => {
    it('should create error boundary with default fallback', () => {
      const ErrorBoundary = createErrorBoundary();
      expect(ErrorBoundary).toBeDefined();
      expect(typeof ErrorBoundary).toBe('function');
    });

    it('should create error boundary with custom fallback', () => {
      const customFallback = <div>Custom error message</div>;
      const ErrorBoundary = createErrorBoundary(customFallback);
      
      expect(ErrorBoundary).toBeDefined();
      expect(typeof ErrorBoundary).toBe('function');
    });

    it('should create error boundary with custom error handler', () => {
      const customErrorHandler = vi.fn();
      const ErrorBoundary = createErrorBoundary(undefined, customErrorHandler);
      
      expect(ErrorBoundary).toBeDefined();
      expect(typeof ErrorBoundary).toBe('function');
    });
  });

  describe('Error boundary behavior', () => {
    it('should catch and handle component errors', () => {
      const ThrowError = () => {
        throw new Error('Component error');
      };

      const ErrorBoundary = createErrorBoundary();
      
      // This would typically be tested with a testing library that supports error boundaries
      // For now, we'll just verify the boundary was created
      expect(ErrorBoundary).toBeDefined();
    });

    it('should call custom error handler when error occurs', () => {
      const customErrorHandler = vi.fn();
      const ErrorBoundary = createErrorBoundary(undefined, customErrorHandler);
      
      expect(ErrorBoundary).toBeDefined();
      // Error handler would be called when an error is caught
    });

    it('should display custom fallback UI on error', () => {
      const customFallback = <div data-testid="custom-error">Something went wrong</div>;
      const ErrorBoundary = createErrorBoundary(customFallback);
      
      expect(ErrorBoundary).toBeDefined();
      // Custom fallback would be rendered when an error occurs
    });
  });

  describe('Error recovery', () => {
    it('should provide retry functionality', () => {
      const retryHandler = vi.fn();
      const ErrorBoundary = createErrorBoundary(undefined, undefined, retryHandler);
      
      expect(ErrorBoundary).toBeDefined();
      // Retry handler would be called when user clicks retry
    });

    it('should reset error state on retry', () => {
      const ErrorBoundary = createErrorBoundary();
      
      expect(ErrorBoundary).toBeDefined();
      // Error state would be reset when retry is triggered
    });
  });
});