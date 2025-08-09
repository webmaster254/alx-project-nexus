import React from 'react';
import { AlertCircle, RefreshCw, Wifi } from 'lucide-react';
import type { EnhancedApiError } from '../../utils/errorHandling';
import { formatErrorForDisplay, isRetryableError } from '../../utils/errorHandling';

interface ErrorDisplayProps {
  error: EnhancedApiError | string | null;
  onRetry?: () => void;
  className?: string;
  variant?: 'inline' | 'card' | 'banner';
  showRetryButton?: boolean;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  className = '',
  variant = 'inline',
  showRetryButton = true,
}) => {
  if (!error) return null;

  const errorMessage = typeof error === 'string' ? error : formatErrorForDisplay(error);
  const canRetry = typeof error === 'object' && isRetryableError(error);
  const showRetry = showRetryButton && canRetry && onRetry;

  const baseClasses = 'flex items-start space-x-3';
  const variantClasses = {
    inline: 'text-red-600',
    card: 'bg-red-50 border border-red-200 rounded-lg p-4',
    banner: 'bg-red-600 text-white px-4 py-3',
  };

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      role="alert"
      aria-live="polite"
    >
      <AlertCircle className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
        variant === 'banner' ? 'text-white' : 'text-red-500'
      }`} />
      
      <div className="flex-1 min-w-0">
        <p className={`text-sm ${
          variant === 'banner' ? 'text-white' : 'text-red-800'
        }`}>
          {errorMessage}
        </p>
        
        {showRetry && (
          <button
            onClick={onRetry}
            className={`mt-2 inline-flex items-center text-sm font-medium ${
              variant === 'banner' 
                ? 'text-white hover:text-red-100' 
                : 'text-red-600 hover:text-red-500'
            } focus:outline-none focus:underline`}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Try again
          </button>
        )}
      </div>
    </div>
  );
};

// Specific error components for common scenarios
export const NetworkErrorDisplay: React.FC<{
  onRetry?: () => void;
  className?: string;
}> = ({ onRetry, className = '' }) => (
  <div className={`text-center py-8 ${className}`}>
    <Wifi className="h-12 w-12 text-gray-400 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      Connection Problem
    </h3>
    <p className="text-gray-600 mb-4">
      Unable to connect to the server. Please check your internet connection.
    </p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        <RefreshCw className="h-4 w-4 mr-2" />
        Try Again
      </button>
    )}
  </div>
);

export const NotFoundErrorDisplay: React.FC<{
  resource?: string;
  onGoBack?: () => void;
  className?: string;
}> = ({ resource = 'page', onGoBack, className = '' }) => (
  <div className={`text-center py-8 ${className}`}>
    <div className="text-6xl font-bold text-gray-300 mb-4">404</div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      {resource.charAt(0).toUpperCase() + resource.slice(1)} Not Found
    </h3>
    <p className="text-gray-600 mb-4">
      The {resource} you're looking for doesn't exist or has been moved.
    </p>
    {onGoBack && (
      <button
        onClick={onGoBack}
        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Go Back
      </button>
    )}
  </div>
);

// Form validation error display
export const ValidationErrorDisplay: React.FC<{
  errors: Record<string, string[]>;
  className?: string;
}> = ({ errors, className = '' }) => {
  const errorEntries = Object.entries(errors);
  
  if (errorEntries.length === 0) return null;

  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start">
        <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800 mb-2">
            Please correct the following errors:
          </h3>
          <ul className="text-sm text-red-700 space-y-1">
            {errorEntries.map(([field, fieldErrors]) => (
              <li key={field}>
                <strong className="capitalize">{field.replace('_', ' ')}:</strong>{' '}
                {fieldErrors.join(', ')}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};