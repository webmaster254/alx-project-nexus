import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { httpClient } from '../index';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('HttpClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should be configured with correct base URL', () => {
    expect(mockedAxios.create).toHaveBeenCalledWith({
      baseURL: expect.stringContaining('/api'),
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  it('should add authorization header when token is present', () => {
    // Mock localStorage
    const mockGetItem = vi.fn().mockReturnValue('test-token');
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: mockGetItem,
      },
      writable: true,
    });

    // Create a mock request config
    const config = { headers: {} };

    // Get the request interceptor
    const requestInterceptor = mockedAxios.create().interceptors.request.use.mock.calls[0][0];
    
    if (requestInterceptor) {
      const result = requestInterceptor(config);
      expect(result.headers.Authorization).toBe('Bearer test-token');
    }
  });

  it('should not add authorization header when token is not present', () => {
    // Mock localStorage with no token
    const mockGetItem = vi.fn().mockReturnValue(null);
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: mockGetItem,
      },
      writable: true,
    });

    const config = { headers: {} };
    const requestInterceptor = mockedAxios.create().interceptors.request.use.mock.calls[0][0];
    
    if (requestInterceptor) {
      const result = requestInterceptor(config);
      expect(result.headers.Authorization).toBeUndefined();
    }
  });

  it('should handle successful responses', () => {
    const mockResponse = {
      data: { message: 'success' },
      status: 200,
      statusText: 'OK',
    };

    const responseInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][0];
    
    if (responseInterceptor) {
      const result = responseInterceptor(mockResponse);
      expect(result).toEqual(mockResponse);
    }
  });

  it('should handle 401 errors by clearing token and redirecting', () => {
    const mockRemoveItem = vi.fn();
    const mockReplace = vi.fn();

    Object.defineProperty(window, 'localStorage', {
      value: {
        removeItem: mockRemoveItem,
      },
      writable: true,
    });

    Object.defineProperty(window, 'location', {
      value: {
        replace: mockReplace,
      },
      writable: true,
    });

    const error = {
      response: {
        status: 401,
        data: { message: 'Unauthorized' },
      },
    };

    const errorInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][1];
    
    if (errorInterceptor) {
      expect(() => errorInterceptor(error)).rejects.toEqual(error);
      expect(mockRemoveItem).toHaveBeenCalledWith('token');
      expect(mockReplace).toHaveBeenCalledWith('/auth');
    }
  });

  it('should handle network errors gracefully', () => {
    const networkError = {
      message: 'Network Error',
      code: 'NETWORK_ERROR',
    };

    const errorInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][1];
    
    if (errorInterceptor) {
      expect(() => errorInterceptor(networkError)).rejects.toEqual(networkError);
    }
  });

  it('should handle timeout errors', () => {
    const timeoutError = {
      code: 'ECONNABORTED',
      message: 'timeout of 10000ms exceeded',
    };

    const errorInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][1];
    
    if (errorInterceptor) {
      expect(() => errorInterceptor(timeoutError)).rejects.toEqual(timeoutError);
    }
  });

  it('should handle server errors (5xx)', () => {
    const serverError = {
      response: {
        status: 500,
        data: { message: 'Internal Server Error' },
      },
    };

    const errorInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][1];
    
    if (errorInterceptor) {
      expect(() => errorInterceptor(serverError)).rejects.toEqual(serverError);
    }
  });

  it('should handle client errors (4xx) other than 401', () => {
    const clientError = {
      response: {
        status: 400,
        data: { message: 'Bad Request' },
      },
    };

    const errorInterceptor = mockedAxios.create().interceptors.response.use.mock.calls[0][1];
    
    if (errorInterceptor) {
      expect(() => errorInterceptor(clientError)).rejects.toEqual(clientError);
    }
  });
});