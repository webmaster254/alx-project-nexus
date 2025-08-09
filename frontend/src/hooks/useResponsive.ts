import { useState, useEffect } from 'react';

interface BreakpointConfig {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
}

interface ResponsiveState {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeDesktop: boolean;
  breakpoint: keyof BreakpointConfig;
  orientation: 'portrait' | 'landscape';
  isTouchDevice: boolean;
  devicePixelRatio: number;
}

const breakpoints: BreakpointConfig = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

const getBreakpoint = (width: number): keyof BreakpointConfig => {
  if (width >= breakpoints['2xl']) return '2xl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  if (width >= breakpoints.sm) return 'sm';
  return 'xs';
};

const isTouchDevice = (): boolean => {
  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    // @ts-ignore - for older browsers
    navigator.msMaxTouchPoints > 0
  );
};

export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1024;
    const height = typeof window !== 'undefined' ? window.innerHeight : 768;
    
    return {
      width,
      height,
      isMobile: width < breakpoints.md,
      isTablet: width >= breakpoints.md && width < breakpoints.lg,
      isDesktop: width >= breakpoints.lg && width < breakpoints.xl,
      isLargeDesktop: width >= breakpoints.xl,
      breakpoint: getBreakpoint(width),
      orientation: width > height ? 'landscape' : 'portrait',
      isTouchDevice: typeof window !== 'undefined' ? isTouchDevice() : false,
      devicePixelRatio: typeof window !== 'undefined' ? window.devicePixelRatio : 1,
    };
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setState({
        width,
        height,
        isMobile: width < breakpoints.md,
        isTablet: width >= breakpoints.md && width < breakpoints.lg,
        isDesktop: width >= breakpoints.lg && width < breakpoints.xl,
        isLargeDesktop: width >= breakpoints.xl,
        breakpoint: getBreakpoint(width),
        orientation: width > height ? 'landscape' : 'portrait',
        isTouchDevice: isTouchDevice(),
        devicePixelRatio: window.devicePixelRatio,
      });
    };

    // Debounce resize events for better performance
    let timeoutId: NodeJS.Timeout;
    const debouncedHandleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, 150);
    };

    window.addEventListener('resize', debouncedHandleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', debouncedHandleResize);
      window.removeEventListener('orientationchange', handleResize);
      clearTimeout(timeoutId);
    };
  }, []);

  return state;
};

// Hook for checking specific breakpoints
export const useBreakpoint = (breakpoint: keyof BreakpointConfig): boolean => {
  const { width } = useResponsive();
  return width >= breakpoints[breakpoint];
};

// Hook for media queries
export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [query]);

  return matches;
};

// Hook for detecting device capabilities
export const useDeviceCapabilities = () => {
  const [capabilities, setCapabilities] = useState({
    hasHover: false,
    hasPointer: false,
    prefersReducedMotion: false,
    prefersColorScheme: 'light' as 'light' | 'dark',
    prefersContrast: 'normal' as 'normal' | 'high',
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateCapabilities = () => {
      setCapabilities({
        hasHover: window.matchMedia('(hover: hover)').matches,
        hasPointer: window.matchMedia('(pointer: fine)').matches,
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        prefersColorScheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
        prefersContrast: window.matchMedia('(prefers-contrast: high)').matches ? 'high' : 'normal',
      });
    };

    updateCapabilities();

    // Listen for changes in media queries
    const mediaQueries = [
      '(hover: hover)',
      '(pointer: fine)',
      '(prefers-reduced-motion: reduce)',
      '(prefers-color-scheme: dark)',
      '(prefers-contrast: high)',
    ];

    const listeners = mediaQueries.map(query => {
      const mq = window.matchMedia(query);
      mq.addEventListener('change', updateCapabilities);
      return { mq, handler: updateCapabilities };
    });

    return () => {
      listeners.forEach(({ mq, handler }) => {
        mq.removeEventListener('change', handler);
      });
    };
  }, []);

  return capabilities;
};

// Hook for viewport dimensions with safe area insets
export const useViewport = () => {
  const [viewport, setViewport] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
    safeAreaTop: 0,
    safeAreaBottom: 0,
    safeAreaLeft: 0,
    safeAreaRight: 0,
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateViewport = () => {
      // Get safe area insets from CSS environment variables
      const computedStyle = getComputedStyle(document.documentElement);
      
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight,
        safeAreaTop: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-top)') || '0'),
        safeAreaBottom: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-bottom)') || '0'),
        safeAreaLeft: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-left)') || '0'),
        safeAreaRight: parseInt(computedStyle.getPropertyValue('env(safe-area-inset-right)') || '0'),
      });
    };

    updateViewport();

    let timeoutId: NodeJS.Timeout;
    const debouncedUpdate = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(updateViewport, 100);
    };

    window.addEventListener('resize', debouncedUpdate);
    window.addEventListener('orientationchange', updateViewport);

    return () => {
      window.removeEventListener('resize', debouncedUpdate);
      window.removeEventListener('orientationchange', updateViewport);
      clearTimeout(timeoutId);
    };
  }, []);

  return viewport;
};