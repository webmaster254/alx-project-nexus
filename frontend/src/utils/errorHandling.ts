import type { ApiError } from '../types';

// Enhanced error types
export interface EnhancedApiError extends ApiError {
  code?: string;
  retryable?: boolean;
  timestamp: number;
}

// Error codes for different scenarios
export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  OFFLINE: 'OFFLINE',
} as const;

// User-friendly error messages
export const ERROR_MESSAGES = {
  [ERROR_CODES.NETWORK_ERROR]: 'Unable to connect to the server. Please check your internet connection.',
  [ERROR_CODES.TIMEOUT]: 'The request took too long to complete. Please try again.',
  [ERROR_CODES.UNAUTHORIZED]: 'You need to log in to access this feature.',
  [ERROR_CODES.FORBIDDEN]: 'You don\'t have permission to perform this action.',
  [ERROR_CODES.NOT_FOUND]: 'The requested resource was not found.',
  [ERROR_CODES.VALIDATION_ERROR]: 'Please check your input and try again.',
  [ERROR_CODES.SERVER_ERROR]: 'A server error occurred. Please try again later.',
  [ERROR_CODES.OFFLINE]: 'You appear to be offline. Please check your connection.',
} as const;

// Determine if an error is retryable
export const isRetryableError = (error: EnhancedApiError): boolean => {
  if (error.retryable !== undefined) {
    return error.retryable;
  }

  // Network errors and timeouts are retryable
  if (error.code === ERROR_CODES.NETWORK_ERROR || error.code === ERROR_CODES.TIMEOUT) {
    return true;
  }

  // Server errors (5xx) are retryable
  if (error.status >= 500) {
    return true;
  }

  // Client errors (4xx) are generally not retryable, except for 408 (timeout)
  if (error.status >= 400 && error.status < 500) {
    return error.status === 408; // Request Timeout
  }

  return false;
};

// Enhanced error creation
export const createEnhancedError = (
  originalError: any,
  customMessage?: string
): EnhancedApiError => {
  let code: string;
  let message: string;
  let status: number;
  let retryable: boolean;

  // Handle different error types
  if (originalError.response) {
    // HTTP error response
    status = originalError.response.status;
    
    switch (status) {
      case 401:
        code = ERROR_CODES.UNAUTHORIZED;
        break;
      case 403:
        code = ERROR_CODES.FORBIDDEN;
        break;
      case 404:
        code = ERROR_CODES.NOT_FOUND;
        break;
      case 408:
        code = ERROR_CODES.TIMEOUT;
        break;
      case 422:
        code = ERROR_CODES.VALIDATION_ERROR;
        break;
      default:
        if (status >= 500) {
          code = ERROR_CODES.SERVER_ERROR;
        } else if (status >= 400) {
          code = ERROR_CODES.VALIDATION_ERROR; // Generic client error
        } else {
          code = ERROR_CODES.NETWORK_ERROR;
        }
    }
  } else if (originalError.code === 'ECONNABORTED') {
    // Timeout error
    code = ERROR_CODES.TIMEOUT;
    status = 408;
  } else if (!originalError.response) {
    // Network error
    code = ERROR_CODES.NETWORK_ERROR;
    status = 0;
  } else {
    // Unknown error
    code = ERROR_CODES.SERVER_ERROR;
    status = 500;
  }

  message = customMessage || ERROR_MESSAGES[code as keyof typeof ERROR_MESSAGES] || originalError.message;
  retryable = isRetryableError({ code, status } as EnhancedApiError);

  return {
    message,
    status,
    code,
    retryable,
    timestamp: Date.now(),
    details: originalError.response?.data,
  };
};

// Retry configuration
export interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffFactor: number;
}

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  backoffFactor: 2,
};

// Calculate delay for retry attempt
export const calculateRetryDelay = (
  attempt: number,
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): number => {
  const delay = config.baseDelay * Math.pow(config.backoffFactor, attempt - 1);
  return Math.min(delay, config.maxDelay);
};

// Retry function with exponential backoff
export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): Promise<T> => {
  let lastError: EnhancedApiError;

  for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = createEnhancedError(error);

      // Don't retry if error is not retryable
      if (!isRetryableError(lastError)) {
        throw lastError;
      }

      // Don't retry on last attempt
      if (attempt === config.maxAttempts) {
        throw lastError;
      }

      // Wait before retrying
      const delay = calculateRetryDelay(attempt, config);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
};

// Format error for display
export const formatErrorForDisplay = (error: EnhancedApiError): string => {
  // Use custom message if available
  if (error.message && error.message !== 'An error occurred') {
    return error.message;
  }

  // Use predefined message based on code
  if (error.code && ERROR_MESSAGES[error.code as keyof typeof ERROR_MESSAGES]) {
    return ERROR_MESSAGES[error.code as keyof typeof ERROR_MESSAGES];
  }

  // Fallback to generic message
  return 'An unexpected error occurred. Please try again.';
};

// Extract validation errors from API response
export const extractValidationErrors = (error: EnhancedApiError): Record<string, string[]> => {
  if (error.details && typeof error.details === 'object') {
    return error.details;
  }
  return {};
};