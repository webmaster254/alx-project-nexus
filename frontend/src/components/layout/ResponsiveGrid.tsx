import React from 'react';
import { useResponsive } from '../../hooks';

interface ResponsiveGridProps {
  children: React.ReactNode;
  className?: string;
  columns?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'sm' | 'md' | 'lg';
  mobileGap?: 'sm' | 'md' | 'lg';
}

const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  className = '',
  columns = { xs: 1, sm: 2, md: 2, lg: 3, xl: 4 },
  gap = 'md',
  mobileGap = 'sm'
}) => {
  const { isMobile } = useResponsive();

  const getGridColumnsClass = () => {
    const { xs = 1, sm = 2, md = 2, lg = 3, xl = 4 } = columns;
    
    // Ensure we don't exceed reasonable column limits
    const safeXs = Math.min(Math.max(xs, 1), 6);
    const safeSm = Math.min(Math.max(sm, 1), 6);
    const safeMd = Math.min(Math.max(md, 1), 6);
    const safeLg = Math.min(Math.max(lg, 1), 6);
    const safeXl = Math.min(Math.max(xl, 1), 6);
    
    return `grid-cols-${safeXs} sm:grid-cols-${safeSm} md:grid-cols-${safeMd} lg:grid-cols-${safeLg} xl:grid-cols-${safeXl}`;
  };

  const getGapClass = () => {
    const currentGap = isMobile ? mobileGap : gap;
    const gapMap = {
      'sm': 'gap-2 sm:gap-3',
      'md': 'gap-4 sm:gap-6',
      'lg': 'gap-6 sm:gap-8'
    };
    return gapMap[currentGap];
  };

  return (
    <div className={`grid ${getGridColumnsClass()} ${getGapClass()} ${className}`}>
      {children}
    </div>
  );
};

export default ResponsiveGrid;