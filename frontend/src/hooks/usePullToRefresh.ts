import { useEffect, useRef, useState } from 'react';

interface PullToRefreshOptions {
  onRefresh: () => Promise<void> | void;
  threshold?: number;
  resistance?: number;
  enabled?: boolean;
}

export const usePullToRefresh = ({
  onRefresh,
  threshold = 80,
  resistance = 2.5,
  enabled = true,
}: PullToRefreshOptions) => {
  const [isPulling, setIsPulling] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  
  const startY = useRef(0);
  const currentY = useRef(0);
  const containerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    const container = containerRef.current || document.body;
    let isAtTop = true;

    const checkScrollPosition = () => {
      isAtTop = container.scrollTop === 0;
    };

    const handleTouchStart = (e: TouchEvent) => {
      checkScrollPosition();
      if (!isAtTop || isRefreshing) return;

      startY.current = e.touches[0].clientY;
      setIsPulling(false);
      setPullDistance(0);
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isAtTop || isRefreshing) return;

      currentY.current = e.touches[0].clientY;
      const deltaY = currentY.current - startY.current;

      if (deltaY > 0) {
        // Prevent default scrolling when pulling down
        e.preventDefault();
        
        const distance = Math.min(deltaY / resistance, threshold * 1.5);
        setPullDistance(distance);
        setIsPulling(distance > 10);
      }
    };

    const handleTouchEnd = async () => {
      if (!isAtTop || isRefreshing) return;

      if (pullDistance >= threshold) {
        setIsRefreshing(true);
        try {
          await onRefresh();
        } catch (error) {
          console.error('Pull to refresh failed:', error);
        } finally {
          setIsRefreshing(false);
        }
      }

      setIsPulling(false);
      setPullDistance(0);
    };

    // Add event listeners
    container.addEventListener('scroll', checkScrollPosition, { passive: true });
    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      container.removeEventListener('scroll', checkScrollPosition);
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [enabled, onRefresh, threshold, resistance, pullDistance, isRefreshing]);

  const setContainer = (element: HTMLElement | null) => {
    containerRef.current = element;
  };

  return {
    isPulling,
    isRefreshing,
    pullDistance,
    setContainer,
    shouldShowIndicator: isPulling || isRefreshing,
    progress: Math.min(pullDistance / threshold, 1),
  };
};