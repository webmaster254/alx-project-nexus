import { vi } from 'vitest';
import {
  createEnhancedError,
  isRetryableError,
  retryWithBackoff,
  formatErrorForDisplay,
  extractValidationErrors,
  calculateRetryDelay,
  ERROR_CODES,
  ERROR_MESSAGES,
  DEFAULT_RETRY_CONFIG,
} from '../errorHandling';

describe('errorHandling utilities', () => {
  describe('createEnhancedError', () => {
    it('creates enhanced error from HTTP 401 response', () => {
      const originalError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      };

      const enhancedError = createEnhancedError(originalError);

      expect(enhancedError.code).toBe(ERROR_CODES.UNAUTHORIZED);
      expect(enhancedError.status).toBe(401);
      expect(enhancedError.retryable).toBe(false);
      expect(enhancedError.message).toBe(ERROR_MESSAGES.UNAUTHORIZED);
    });

    it('creates enhanced error from network error', () => {
      const originalError = {
        code: 'ECONNABORTED'
      };

      const enhancedError = createEnhancedError(originalError);

      expect(enhancedError.code).toBe(ERROR_CODES.TIMEOUT);
      expect(enhancedError.status).toBe(408);
      expect(enhancedError.retryable).toBe(true);
    });

    it('creates enhanced error from server error', () => {
      const originalError = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      };

      const enhancedError = createEnhancedError(originalError);

      expect(enhancedError.code).toBe(ERROR_CODES.SERVER_ERROR);
      expect(enhancedError.status).toBe(500);
      expect(enhancedError.retryable).toBe(true);
    });

    it('uses custom message when provided', () => {
      const originalError = {
        response: {
          status: 404,
          data: { message: 'Not found' }
        }
      };

      const enhancedError = createEnhancedError(originalError, 'Custom message');

      expect(enhancedError.message).toBe('Custom message');
    });
  });

  describe('isRetryableError', () => {
    it('returns true for server errors', () => {
      const error = { status: 500, retryable: undefined } as any;
      expect(isRetryableError(error)).toBe(true);
    });

    it('returns false for client errors', () => {
      const error = { status: 400, retryable: undefined } as any;
      expect(isRetryableError(error)).toBe(false);
    });

    it('returns true for timeout errors', () => {
      const error = { status: 408, retryable: undefined } as any;
      expect(isRetryableError(error)).toBe(true);
    });

    it('respects explicit retryable flag', () => {
      const error = { status: 400, retryable: true } as any;
      expect(isRetryableError(error)).toBe(true);
    });
  });

  describe('calculateRetryDelay', () => {
    it('calculates exponential backoff delay', () => {
      expect(calculateRetryDelay(1)).toBe(1000);
      expect(calculateRetryDelay(2)).toBe(2000);
      expect(calculateRetryDelay(3)).toBe(4000);
    });

    it('respects maximum delay', () => {
      const config = { ...DEFAULT_RETRY_CONFIG, maxDelay: 3000 };
      expect(calculateRetryDelay(3, config)).toBe(3000);
    });
  });

  describe('retryWithBackoff', () => {
    it('succeeds on first attempt', async () => {
      const fn = vi.fn().mockResolvedValue('success');
      
      const result = await retryWithBackoff(fn);
      
      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('retries on retryable error', async () => {
      const fn = vi.fn()
        .mockRejectedValueOnce({ status: 500, retryable: true })
        .mockResolvedValue('success');
      
      const result = await retryWithBackoff(fn, { ...DEFAULT_RETRY_CONFIG, maxAttempts: 2 });
      
      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('does not retry on non-retryable error', async () => {
      const error = { response: { status: 400 } };
      const fn = vi.fn().mockRejectedValue(error);
      
      await expect(retryWithBackoff(fn)).rejects.toMatchObject({
        status: 400,
        retryable: false
      });
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('throws last error after max attempts', async () => {
      const error = { response: { status: 500 } };
      const fn = vi.fn().mockRejectedValue(error);
      
      await expect(retryWithBackoff(fn, { ...DEFAULT_RETRY_CONFIG, maxAttempts: 2 }))
        .rejects.toMatchObject({
          status: 500,
          retryable: true
        });
      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('formatErrorForDisplay', () => {
    it('returns custom message when available', () => {
      const error = { message: 'Custom error message' } as any;
      expect(formatErrorForDisplay(error)).toBe('Custom error message');
    });

    it('returns predefined message for known error codes', () => {
      const error = { code: ERROR_CODES.NETWORK_ERROR, message: 'An error occurred' } as any;
      expect(formatErrorForDisplay(error)).toBe(ERROR_MESSAGES.NETWORK_ERROR);
    });

    it('returns fallback message for unknown errors', () => {
      const error = { code: 'UNKNOWN_ERROR' } as any;
      expect(formatErrorForDisplay(error)).toBe('An unexpected error occurred. Please try again.');
    });
  });

  describe('extractValidationErrors', () => {
    it('extracts validation errors from API response', () => {
      const error = {
        details: {
          email: ['This field is required'],
          password: ['Password too short', 'Password too weak']
        }
      } as any;

      const validationErrors = extractValidationErrors(error);

      expect(validationErrors).toEqual({
        email: ['This field is required'],
        password: ['Password too short', 'Password too weak']
      });
    });

    it('returns empty object when no details available', () => {
      const error = {} as any;
      expect(extractValidationErrors(error)).toEqual({});
    });
  });
});