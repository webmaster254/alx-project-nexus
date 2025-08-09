import { useRef, useEffect, useCallback } from 'react';

interface UseInfiniteScrollOptions {
  hasNextPage: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  rootMargin?: string;
}

export const useInfiniteScroll = ({
  hasNextPage,
  isLoading,
  onLoadMore,
  rootMargin = '0px'
}: UseInfiniteScrollOptions) => {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      
      if (entry.isIntersecting && hasNextPage && !isLoading) {
        onLoadMore();
      }
    },
    [hasNextPage, isLoading, onLoadMore]
  );

  useEffect(() => {
    const element = loadMoreRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(handleIntersection, {
      rootMargin,
      threshold: 0.1,
    });

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [handleIntersection, rootMargin]);

  return { loadMoreRef };
};

// Hook for pull-to-refresh with visual feedback
export const usePullToRefreshWithFeedback = (
  onRefresh: () => Promise<void>,
  threshold: number = 100
) => {
  const startY = useRef<number>(0);
  const currentY = useRef<number>(0);
  const isRefreshing = useRef<boolean>(false);
  const pullDistance = useRef<number>(0);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    startY.current = e.touches[0].clientY;
    isRefreshing.current = false;
    pullDistance.current = 0;
  }, []);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    currentY.current = e.touches[0].clientY;
    const deltaY = currentY.current - startY.current;

    // Only trigger if we're at the top of the page and pulling down
    if (window.scrollY === 0 && deltaY > 0) {
      pullDistance.current = Math.min(deltaY, threshold * 1.5);
      
      // Provide visual feedback
      const pullIndicator = document.getElementById('pull-to-refresh-indicator');
      if (pullIndicator) {
        const progress = Math.min(pullDistance.current / threshold, 1);
        pullIndicator.style.transform = `translateY(${pullDistance.current * 0.5}px) rotate(${progress * 180}deg)`;
        pullIndicator.style.opacity = progress.toString();
      }

      if (deltaY > threshold && !isRefreshing.current) {
        isRefreshing.current = true;
        onRefresh().finally(() => {
          isRefreshing.current = false;
          pullDistance.current = 0;
          if (pullIndicator) {
            pullIndicator.style.transform = 'translateY(0) rotate(0deg)';
            pullIndicator.style.opacity = '0';
          }
        });
      }
    }
  }, [onRefresh, threshold]);

  const handleTouchEnd = useCallback(() => {
    const pullIndicator = document.getElementById('pull-to-refresh-indicator');
    if (pullIndicator && !isRefreshing.current) {
      pullIndicator.style.transform = 'translateY(0) rotate(0deg)';
      pullIndicator.style.opacity = '0';
    }
    pullDistance.current = 0;
  }, []);

  const attachPullToRefreshListeners = useCallback((element: HTMLElement | null) => {
    if (!element) return;

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: true });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return { attachPullToRefreshListeners, pullDistance: pullDistance.current };
};