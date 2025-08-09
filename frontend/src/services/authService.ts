import { httpClient } from './index';
import type { User, ApiResponse } from '../types';

// Authentication request/response types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

export interface RefreshTokenRequest {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  password: string;
  password_confirm: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  profile?: {
    phone?: string;
    location?: string;
    bio?: string;
    experience_years?: number;
    skills?: string[];
  };
}

class AuthService {
  private refreshTokenTimeout: NodeJS.Timeout | null = null;

  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>('/auth/login/', credentials);
    
    if (response.data.access) {
      this.setTokens(response.data.access, response.data.refresh);
      this.scheduleTokenRefresh(response.data.access);
    }
    
    return response;
  }

  /**
   * Register new user
   */
  async register(userData: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    const response = await httpClient.post<AuthResponse>('/auth/register/', userData);
    
    if (response.data.access) {
      this.setTokens(response.data.access, response.data.refresh);
      this.scheduleTokenRefresh(response.data.access);
    }
    
    return response;
  }

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await httpClient.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearTokens();
      this.clearTokenRefreshTimeout();
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(): Promise<ApiResponse<RefreshTokenResponse>> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await httpClient.post<RefreshTokenResponse>('/auth/refresh/', {
        refresh: refreshToken,
      });

      if (response.data.access) {
        localStorage.setItem('auth_token', response.data.access);
        this.scheduleTokenRefresh(response.data.access);
      }

      return response;
    } catch (error) {
      // If refresh fails, clear all tokens and redirect to login
      this.clearTokens();
      throw error;
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return await httpClient.get<User>('/auth/user/');
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: UpdateProfileRequest): Promise<ApiResponse<User>> {
    return await httpClient.patch<User>('/auth/user/', profileData);
  }

  /**
   * Change user password
   */
  async changePassword(passwordData: ChangePasswordRequest): Promise<ApiResponse<{ message: string }>> {
    return await httpClient.post<{ message: string }>('/auth/change-password/', passwordData);
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<ApiResponse<{ message: string }>> {
    return await httpClient.post<{ message: string }>('/auth/password-reset/', { email });
  }

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(resetData: PasswordResetConfirmRequest): Promise<ApiResponse<{ message: string }>> {
    return await httpClient.post<{ message: string }>('/auth/password-reset-confirm/', resetData);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  }

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  /**
   * Set tokens in localStorage
   */
  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('auth_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  /**
   * Clear all tokens from localStorage
   */
  private clearTokens(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  }

  /**
   * Schedule automatic token refresh
   */
  private scheduleTokenRefresh(token: string): void {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expirationTime = payload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      const refreshTime = expirationTime - currentTime - 60000; // Refresh 1 minute before expiry

      if (refreshTime > 0) {
        this.clearTokenRefreshTimeout();
        this.refreshTokenTimeout = setTimeout(() => {
          this.refreshToken().catch((error) => {
            console.error('Automatic token refresh failed:', error);
            // Could dispatch logout action here if needed
          });
        }, refreshTime);
      }
    } catch (error) {
      console.error('Error scheduling token refresh:', error);
    }
  }

  /**
   * Clear token refresh timeout
   */
  private clearTokenRefreshTimeout(): void {
    if (this.refreshTokenTimeout) {
      clearTimeout(this.refreshTokenTimeout);
      this.refreshTokenTimeout = null;
    }
  }

  /**
   * Initialize authentication state and schedule refresh if needed
   */
  initializeAuth(): void {
    const token = this.getAccessToken();
    if (token && this.isAuthenticated()) {
      this.scheduleTokenRefresh(token);
    } else {
      this.clearTokens();
    }
  }
}

// Create and export auth service instance
export const authService = new AuthService();
export { AuthService };