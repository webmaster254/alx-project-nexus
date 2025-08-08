import React, { useState } from 'react';
import { useUser } from '../../contexts/UserContext';
import { authService } from '../../services';
import type { LoginRequest } from '../../services/authService';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister }) => {
  const { login, setLoading, setError } = useUser();
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(formData);
      login(response.data.user, response.data.access);
      onSuccess?.();
    } catch (error: any) {
      console.error('Login error:', error);
      
      if (error.details) {
        // Handle field-specific errors from API
        const apiErrors: FormErrors = {};
        if (error.details.email) {
          apiErrors.email = error.details.email[0];
        }
        if (error.details.password) {
          apiErrors.password = error.details.password[0];
        }
        if (error.details.non_field_errors) {
          apiErrors.general = error.details.non_field_errors[0];
        }
        setErrors(apiErrors);
      } else {
        setErrors({ general: error.message || 'Login failed. Please try again.' });
      }
      setError(error.message || 'Login failed');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-md rounded-lg px-8 pt-6 pb-8 mb-4">
        <div className="mb-6 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Sign In</h2>
          <p className="text-gray-600">Welcome back! Please sign in to your account.</p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {errors.general && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded" role="alert">
              {errors.general}
            </div>
          )}

          <div className="mb-4">
            <label 
              htmlFor="email" 
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                errors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your email"
              aria-describedby={errors.email ? 'email-error' : undefined}
              aria-invalid={!!errors.email}
              autoComplete="email"
              required
            />
            {errors.email && (
              <p id="email-error" className="text-red-500 text-xs italic mt-1" role="alert">
                {errors.email}
              </p>
            )}
          </div>

          <div className="mb-6">
            <label 
              htmlFor="password" 
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your password"
              aria-describedby={errors.password ? 'password-error' : undefined}
              aria-invalid={!!errors.password}
              autoComplete="current-password"
              required
            />
            {errors.password && (
              <p id="password-error" className="text-red-500 text-xs italic mt-1" role="alert">
                {errors.password}
              </p>
            )}
          </div>

          <div className="flex items-center justify-between mb-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors ${
                isSubmitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-700 text-white'
              }`}
              aria-describedby="submit-status"
            >
              {isSubmitting ? 'Signing In...' : 'Sign In'}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-blue-500 hover:text-blue-700 text-sm font-medium transition-colors"
            >
              Don't have an account? Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};