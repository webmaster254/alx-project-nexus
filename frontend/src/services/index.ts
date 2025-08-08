// API service layer
import axios from 'axios';
import type { ApiError, ApiResponse } from '../types';

// HTTP Client Configuration
class HttpClient {
  private client: any;

  constructor() {
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
        
        // Log request in development
        if (import.meta.env.DEV) {
          console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }
        
        return config;
      },
      (error: any) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: any) => {
        // Log response in development
        if (import.meta.env.DEV) {
          console.log(`[API Response] ${response.status} ${response.config.url}`, response.data);
        }
        
        return response;
      },
      (error: any) => {
        const apiError: ApiError = {
          message: 'An error occurred',
          status: error.response?.status || 500,
          details: error.response?.data as Record<string, string[]>,
        };

        // Handle specific error cases
        if (error.response?.status === 401) {
          apiError.message = 'Unauthorized access';
          // Clear auth token on 401
          localStorage.removeItem('auth_token');
        } else if (error.response?.status === 404) {
          apiError.message = 'Resource not found';
        } else if (error.response?.status === 500) {
          apiError.message = 'Server error occurred';
        } else if (error.code === 'ECONNABORTED') {
          apiError.message = 'Request timeout';
        } else if (!error.response) {
          apiError.message = 'Network error';
        } else {
          apiError.message = error.response?.data?.message || error.message;
        }

        console.error('[API Response Error]', apiError);
        return Promise.reject(apiError);
      }
    );
  }

  // HTTP methods
  async get<T>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    const response = await this.client.get(url, { params });
    return {
      data: response.data,
      status: response.status,
    };
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, data);
    return {
      data: response.data,
      status: response.status,
    };
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.put(url, data);
    return {
      data: response.data,
      status: response.status,
    };
  }

  async patch<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.client.patch(url, data);
    return {
      data: response.data,
      status: response.status,
    };
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.client.delete(url);
    return {
      data: response.data,
      status: response.status,
    };
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
export type { ApiError, ApiResponse } from '../types';
