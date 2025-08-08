import React, { useState } from 'react';
import { useUser } from '../../contexts/UserContext';
import { authService } from '../../services';
import type { RegisterRequest } from '../../services/authService';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

interface FormErrors {
  email?: string;
  password?: string;
  password_confirm?: string;
  first_name?: string;
  last_name?: string;
  general?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { login, setLoading, setError } = useUser();
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // First name validation
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = 'First name must be at least 2 characters';
    }

    // Last name validation
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = 'Last name must be at least 2 characters';
    }

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    // Password confirmation validation
    if (!formData.password_confirm) {
      newErrors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
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
      const response = await authService.register(formData);
      login(response.data.user, response.data.access);
      onSuccess?.();
    } catch (error: any) {
      console.error('Registration error:', error);
      
      if (error.details) {
        // Handle field-specific errors from API
        const apiErrors: FormErrors = {};
        if (error.details.email) {
          apiErrors.email = error.details.email[0];
        }
        if (error.details.password) {
          apiErrors.password = error.details.password[0];
        }
        if (error.details.first_name) {
          apiErrors.first_name = error.details.first_name[0];
        }
        if (error.details.last_name) {
          apiErrors.last_name = error.details.last_name[0];
        }
        if (error.details.non_field_errors) {
          apiErrors.general = error.details.non_field_errors[0];
        }
        setErrors(apiErrors);
      } else {
        setErrors({ general: error.message || 'Registration failed. Please try again.' });
      }
      setError(error.message || 'Registration failed');
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-md rounded-lg px-8 pt-6 pb-8 mb-4">
        <div className="mb-6 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Account</h2>
          <p className="text-gray-600">Join us to start your job search journey.</p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {errors.general && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded" role="alert">
              {errors.general}
            </div>
          )}

          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <label 
                htmlFor="first_name" 
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                First Name
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  errors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="First name"
                aria-describedby={errors.first_name ? 'first-name-error' : undefined}
                aria-invalid={!!errors.first_name}
                autoComplete="given-name"
                required
              />
              {errors.first_name && (
                <p id="first-name-error" className="text-red-500 text-xs italic mt-1" role="alert">
                  {errors.first_name}
                </p>
              )}
            </div>

            <div className="flex-1">
              <label 
                htmlFor="last_name" 
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Last Name
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                  errors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Last name"
                aria-describedby={errors.last_name ? 'last-name-error' : undefined}
                aria-invalid={!!errors.last_name}
                autoComplete="family-name"
                required
              />
              {errors.last_name && (
                <p id="last-name-error" className="text-red-500 text-xs italic mt-1" role="alert">
                  {errors.last_name}
                </p>
              )}
            </div>
          </div>

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

          <div className="mb-4">
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
              placeholder="Create a password"
              aria-describedby={errors.password ? 'password-error' : 'password-help'}
              aria-invalid={!!errors.password}
              autoComplete="new-password"
              required
            />
            {errors.password ? (
              <p id="password-error" className="text-red-500 text-xs italic mt-1" role="alert">
                {errors.password}
              </p>
            ) : (
              <p id="password-help" className="text-gray-500 text-xs mt-1">
                Must be at least 8 characters with uppercase, lowercase, and number
              </p>
            )}
          </div>

          <div className="mb-6">
            <label 
              htmlFor="password_confirm" 
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Confirm Password
            </label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleInputChange}
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${
                errors.password_confirm ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Confirm your password"
              aria-describedby={errors.password_confirm ? 'password-confirm-error' : undefined}
              aria-invalid={!!errors.password_confirm}
              autoComplete="new-password"
              required
            />
            {errors.password_confirm && (
              <p id="password-confirm-error" className="text-red-500 text-xs italic mt-1" role="alert">
                {errors.password_confirm}
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
            >
              {isSubmitting ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-blue-500 hover:text-blue-700 text-sm font-medium transition-colors"
            >
              Already have an account? Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};