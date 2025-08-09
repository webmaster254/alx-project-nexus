import React from 'react';
import { useResponsive } from '../../hooks';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '7xl';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  mobilePadding?: 'none' | 'sm' | 'md' | 'lg';
}

const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className = '',
  maxWidth = '7xl',
  padding = 'md',
  mobilePadding = 'sm'
}) => {
  const { isMobile } = useResponsive();

  const getMaxWidthClass = () => {
    const maxWidthMap = {
      'sm': 'max-w-sm',
      'md': 'max-w-md',
      'lg': 'max-w-lg',
      'xl': 'max-w-xl',
      '2xl': 'max-w-2xl',
      '7xl': 'max-w-7xl'
    };
    return maxWidthMap[maxWidth];
  };

  const getPaddingClass = () => {
    const currentPadding = isMobile ? mobilePadding : padding;
    const paddingMap = {
      'none': '',
      'sm': 'px-4 py-2',
      'md': 'px-4 sm:px-6 lg:px-8 py-4 sm:py-6',
      'lg': 'px-6 sm:px-8 lg:px-12 py-6 sm:py-8 lg:py-12'
    };
    return paddingMap[currentPadding];
  };

  return (
    <div className={`${getMaxWidthClass()} mx-auto ${getPaddingClass()} ${className}`}>
      {children}
    </div>
  );
};

export default ResponsiveContainer;