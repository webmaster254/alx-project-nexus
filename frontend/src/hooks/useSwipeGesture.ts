import { useRef, useCallback, useEffect } from 'react';

interface SwipeGestureOptions {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number; // Minimum distance for a swipe
  preventDefaultTouchmove?: boolean;
}

interface TouchPosition {
  x: number;
  y: number;
}

export const useSwipeGesture = (options: SwipeGestureOptions = {}) => {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    threshold = 50,
    preventDefaultTouchmove = false,
  } = options;

  const touchStartRef = useRef<TouchPosition | null>(null);
  const touchEndRef = useRef<TouchPosition | null>(null);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    const touch = e.touches[0];
    touchStartRef.current = {
      x: touch.clientX,
      y: touch.clientY,
    };
    touchEndRef.current = null;
  }, []);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    if (preventDefaultTouchmove) {
      e.preventDefault();
    }
    
    const touch = e.touches[0];
    touchEndRef.current = {
      x: touch.clientX,
      y: touch.clientY,
    };
  }, [preventDefaultTouchmove]);

  const handleTouchEnd = useCallback(() => {
    if (!touchStartRef.current || !touchEndRef.current) {
      return;
    }

    const deltaX = touchEndRef.current.x - touchStartRef.current.x;
    const deltaY = touchEndRef.current.y - touchStartRef.current.y;
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);

    // Determine if this is a horizontal or vertical swipe
    if (absDeltaX > absDeltaY) {
      // Horizontal swipe
      if (absDeltaX > threshold) {
        if (deltaX > 0) {
          onSwipeRight?.();
        } else {
          onSwipeLeft?.();
        }
      }
    } else {
      // Vertical swipe
      if (absDeltaY > threshold) {
        if (deltaY > 0) {
          onSwipeDown?.();
        } else {
          onSwipeUp?.();
        }
      }
    }

    // Reset touch positions
    touchStartRef.current = null;
    touchEndRef.current = null;
  }, [onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, threshold]);

  const attachSwipeListeners = useCallback((element: HTMLElement | null) => {
    if (!element) return;

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: !preventDefaultTouchmove });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, preventDefaultTouchmove]);

  return { attachSwipeListeners };
};

// Hook for detecting pull-to-refresh gesture
export const usePullToRefresh = (onRefresh: () => void, threshold: number = 100) => {
  const startY = useRef<number>(0);
  const currentY = useRef<number>(0);
  const isRefreshing = useRef<boolean>(false);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    startY.current = e.touches[0].clientY;
    isRefreshing.current = false;
  }, []);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    currentY.current = e.touches[0].clientY;
    const deltaY = currentY.current - startY.current;

    // Only trigger if we're at the top of the page and pulling down
    if (window.scrollY === 0 && deltaY > 0) {
      if (deltaY > threshold && !isRefreshing.current) {
        isRefreshing.current = true;
        onRefresh();
      }
    }
  }, [onRefresh, threshold]);

  const attachPullToRefreshListeners = useCallback((element: HTMLElement | null) => {
    if (!element) return;

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
    };
  }, [handleTouchStart, handleTouchMove]);

  return { attachPullToRefreshListeners };
};