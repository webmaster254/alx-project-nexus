// API service layer
import axios from 'axios';
import type { ApiResponse } from '../types';
import { 
  createEnhancedError, 
  retryWithBackoff, 
  DEFAULT_RETRY_CONFIG,
  type RetryConfig
} from '../utils/errorHandling';

// HTTP Client Configuration
class HttpClient {
  private client: any;
  private retryConfig: RetryConfig;

  constructor(retryConfig: RetryConfig = DEFAULT_RETRY_CONFIG) {
    this.retryConfig = retryConfig;
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: any) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // Add request timestamp for debugging
        config.metadata = { startTime: Date.now() };
        
        // Log request in development
        if (import.meta.env.DEV) {
          console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }
        
        return config;
      },
      (error: any) => {
        console.error('[API Request Error]', error);
        return Promise.reject(createEnhancedError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: any) => {
        // Calculate request duration
        const duration = Date.now() - response.config.metadata?.startTime;
        
        // Log response in development
        if (import.meta.env.DEV) {
          console.log(`[API Response] ${response.status} ${response.config.url} (${duration}ms)`, response.data);
        }
        
        return response;
      },
      (error: any) => {
        const enhancedError = createEnhancedError(error);

        // Handle specific error cases
        if (error.response?.status === 401) {
          // Clear auth token on 401
          localStorage.removeItem('auth_token');
          // Dispatch logout event
          window.dispatchEvent(new CustomEvent('auth:logout'));
        }

        console.error('[API Response Error]', enhancedError);
        return Promise.reject(enhancedError);
      }
    );
  }

  // HTTP methods with retry functionality
  async get<T>(url: string, params?: Record<string, any>, enableRetry: boolean = true): Promise<ApiResponse<T>> {
    const makeRequest = async () => {
      const response = await this.client.get(url, { params });
      return {
        data: response.data,
        status: response.status,
      };
    };

    return enableRetry ? retryWithBackoff(makeRequest, this.retryConfig) : makeRequest();
  }

  async post<T>(url: string, data?: any, enableRetry: boolean = false): Promise<ApiResponse<T>> {
    const makeRequest = async () => {
      const response = await this.client.post(url, data);
      return {
        data: response.data,
        status: response.status,
      };
    };

    // POST requests are generally not retried by default to avoid duplicate operations
    return enableRetry ? retryWithBackoff(makeRequest, this.retryConfig) : makeRequest();
  }

  async put<T>(url: string, data?: any, enableRetry: boolean = false): Promise<ApiResponse<T>> {
    const makeRequest = async () => {
      const response = await this.client.put(url, data);
      return {
        data: response.data,
        status: response.status,
      };
    };

    return enableRetry ? retryWithBackoff(makeRequest, this.retryConfig) : makeRequest();
  }

  async patch<T>(url: string, data?: unknown, enableRetry: boolean = false): Promise<ApiResponse<T>> {
    const makeRequest = async () => {
      const response = await this.client.patch(url, data);
      return {
        data: response.data,
        status: response.status,
      };
    };

    return enableRetry ? retryWithBackoff(makeRequest, this.retryConfig) : makeRequest();
  }

  async delete<T>(url: string, enableRetry: boolean = false): Promise<ApiResponse<T>> {
    const makeRequest = async () => {
      const response = await this.client.delete(url);
      return {
        data: response.data,
        status: response.status,
      };
    };

    return enableRetry ? retryWithBackoff(makeRequest, this.retryConfig) : makeRequest();
  }

  // File upload method
  async uploadFile<T>(url: string, file: File, additionalData?: Record<string, unknown>): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        const value = additionalData[key];
        if (typeof value === 'string' || value instanceof Blob) {
          formData.append(key, value);
        } else if (value !== null && value !== undefined) {
          formData.append(key, String(value));
        }
      });
    }

    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return {
      data: response.data,
      status: response.status,
    };
  }

  // Multipart form data method
  async postMultipart<T>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return {
      data: response.data,
      status: response.status,
    };
  }
}

// Create and export HTTP client instance
export const httpClient = new HttpClient();

// Export services
export { jobService, JobService } from './jobService';
export { categoryService, CategoryService } from './categoryService';
export { authService, AuthService } from './authService';
export { applicationService, ApplicationService } from './applicationService';

// Export types for use in services
export type { ApiResponse } from '../types';
