import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useInfiniteScroll } from '../useInfiniteScroll';

// Mock IntersectionObserver
const mockIntersectionObserver = vi.fn();
const mockObserve = vi.fn();
const mockUnobserve = vi.fn();
const mockDisconnect = vi.fn();

beforeEach(() => {
  mockIntersectionObserver.mockImplementation((callback) => ({
    observe: mockObserve,
    unobserve: mockUnobserve,
    disconnect: mockDisconnect,
    callback,
  }));

  global.IntersectionObserver = mockIntersectionObserver;
});

afterEach(() => {
  vi.clearAllMocks();
});

describe('useInfiniteScroll', () => {
  it('initializes with correct default values', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    expect(result.current.isLoading).toBe(false);
    expect(result.current.hasMore).toBe(true);
    expect(result.current.elementRef.current).toBe(null);
  });

  it('creates IntersectionObserver when element is set', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
    });

    expect(mockIntersectionObserver).toHaveBeenCalledWith(
      expect.any(Function),
      {
        root: null,
        rootMargin: '100px',
        threshold: 0.1,
      }
    );
    expect(mockObserve).toHaveBeenCalledWith(mockElement);
  });

  it('calls callback when element intersects and conditions are met', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
    });

    // Get the callback passed to IntersectionObserver
    const observerCallback = mockIntersectionObserver.mock.calls[0][0];

    // Simulate intersection
    act(() => {
      observerCallback([{ isIntersecting: true, target: mockElement }]);
    });

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('does not call callback when loading', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
      result.current.setIsLoading(true);
    });

    const observerCallback = mockIntersectionObserver.mock.calls[0][0];

    act(() => {
      observerCallback([{ isIntersecting: true, target: mockElement }]);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it('does not call callback when hasMore is false', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
      result.current.setHasMore(false);
    });

    const observerCallback = mockIntersectionObserver.mock.calls[0][0];

    act(() => {
      observerCallback([{ isIntersecting: true, target: mockElement }]);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it('does not call callback when element is not intersecting', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
    });

    const observerCallback = mockIntersectionObserver.mock.calls[0][0];

    act(() => {
      observerCallback([{ isIntersecting: false, target: mockElement }]);
    });

    expect(callback).not.toHaveBeenCalled();
  });

  it('uses custom options when provided', () => {
    const callback = vi.fn();
    const options = {
      root: document.body,
      rootMargin: '50px',
      threshold: 0.5,
    };

    renderHook(() => useInfiniteScroll(callback, options));

    expect(mockIntersectionObserver).toHaveBeenCalledWith(
      expect.any(Function),
      options
    );
  });

  it('disconnects observer on unmount', () => {
    const callback = vi.fn();
    const { result, unmount } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    act(() => {
      result.current.elementRef.current = mockElement;
    });

    unmount();

    expect(mockDisconnect).toHaveBeenCalledTimes(1);
  });

  it('updates observer when element changes', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement1 = document.createElement('div');
    const mockElement2 = document.createElement('div');
    
    // Set first element
    act(() => {
      result.current.elementRef.current = mockElement1;
    });

    expect(mockObserve).toHaveBeenCalledWith(mockElement1);

    // Change to second element
    act(() => {
      result.current.elementRef.current = mockElement2;
    });

    expect(mockUnobserve).toHaveBeenCalledWith(mockElement1);
    expect(mockObserve).toHaveBeenCalledWith(mockElement2);
  });

  it('handles null element gracefully', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    const mockElement = document.createElement('div');
    
    // Set element first
    act(() => {
      result.current.elementRef.current = mockElement;
    });

    // Then set to null
    act(() => {
      result.current.elementRef.current = null;
    });

    expect(mockUnobserve).toHaveBeenCalledWith(mockElement);
  });

  it('allows manual control of loading state', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.setIsLoading(true);
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.setIsLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('allows manual control of hasMore state', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useInfiniteScroll(callback));

    expect(result.current.hasMore).toBe(true);

    act(() => {
      result.current.setHasMore(false);
    });

    expect(result.current.hasMore).toBe(false);

    act(() => {
      result.current.setHasMore(true);
    });

    expect(result.current.hasMore).toBe(true);
  });
});