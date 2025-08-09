import React from 'react';
import { useResponsive } from '../../hooks';

interface ResponsiveButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  fullWidth?: boolean;
  mobileFullWidth?: boolean;
}

const ResponsiveButton: React.FC<ResponsiveButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  fullWidth = false,
  mobileFullWidth = false
}) => {
  const { isMobile } = useResponsive();

  const getVariantClasses = () => {
    const variants = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 focus:ring-blue-500',
      secondary: 'bg-gray-600 text-white hover:bg-gray-700 active:bg-gray-800 focus:ring-gray-500',
      outline: 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 active:bg-gray-100 focus:ring-blue-500',
      ghost: 'text-gray-700 hover:bg-gray-100 active:bg-gray-200 focus:ring-blue-500'
    };
    return variants[variant];
  };

  const getSizeClasses = () => {
    if (isMobile) {
      // Mobile-optimized sizes with larger touch targets
      const mobileSizes = {
        sm: 'px-3 py-3 text-sm min-h-[44px]',
        md: 'px-4 py-3 text-base min-h-[48px]',
        lg: 'px-6 py-4 text-lg min-h-[52px]'
      };
      return mobileSizes[size];
    }

    const desktopSizes = {
      sm: 'px-3 py-2 text-sm min-h-[36px]',
      md: 'px-4 py-2 text-sm min-h-[40px]',
      lg: 'px-6 py-3 text-base min-h-[44px]'
    };
    return desktopSizes[size];
  };

  const getWidthClasses = () => {
    if (fullWidth) return 'w-full';
    if (mobileFullWidth && isMobile) return 'w-full sm:w-auto';
    return '';
  };

  const baseClasses = `
    inline-flex items-center justify-center font-medium rounded-md
    focus:outline-none focus:ring-2 focus:ring-offset-2
    transition-all duration-200 touch-manipulation
    disabled:opacity-50 disabled:cursor-not-allowed
    ${getVariantClasses()}
    ${getSizeClasses()}
    ${getWidthClasses()}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={baseClasses}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

export default ResponsiveButton;