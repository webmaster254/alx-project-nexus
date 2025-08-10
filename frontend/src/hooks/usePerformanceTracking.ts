import { useEffect, useRef, useCallback } from 'react';
import { config } from '../config/environment';
import { trackEvent } from '../services/performanceService';

// Hook for tracking component render performance
export const usePerformanceTracking = (componentName: string) => {
  const renderStartTime = useRef<number>(0);
  const mountTime = useRef<number>(0);

  useEffect(() => {
    if (!config.enablePerformanceMonitoring) return;

    // Track component mount time
    mountTime.current = performance.now();
    
    return () => {
      // Track component unmount
      const unmountTime = performance.now();
      const totalMountTime = unmountTime - mountTime.current;
      
      if (config.enableDebugMode) {
        console.log(`Component ${componentName} was mounted for ${totalMountTime.toFixed(2)}ms`);
      }
      
      // Track long-lived components
      if (totalMountTime > 10000) { // 10 seconds
        trackEvent('component_long_mount', 'Performance', componentName, Math.round(totalMountTime));
      }
    };
  }, [componentName]);

  // Function to track render performance
  const trackRender = () => {
    if (!config.enablePerformanceMonitoring) return;
    
    renderStartTime.current = performance.now();
    
    // Use setTimeout to measure after render
    setTimeout(() => {
      const renderTime = performance.now() - renderStartTime.current;
      
      if (config.enableDebugMode && renderTime > 16) { // Slower than 60fps
        console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
      
      // Track slow renders
      if (renderTime > 100) { // 100ms threshold
        trackEvent('slow_render', 'Performance', componentName, Math.round(renderTime));
      }
    }, 0);
  };

  return { trackRender };
};

// Hook for tracking user interactions
export const useInteractionTracking = () => {
  const trackClick = useCallback((elementName: string, additionalData?: Record<string, any>) => {
    if (!config.enableAnalytics) return;
    
    trackEvent('click', 'User Interaction', elementName);
    
    if (config.enableDebugMode) {
      console.log(`User clicked: ${elementName}`, additionalData);
    }
  }, []);

  const trackFormSubmit = useCallback((formName: string, success: boolean) => {
    if (!config.enableAnalytics) return;
    
    trackEvent('form_submit', 'User Interaction', `${formName}_${success ? 'success' : 'error'}`);
  }, []);

  const trackSearch = useCallback((query: string, resultsCount: number) => {
    if (!config.enableAnalytics) return;
    
    trackEvent('search', 'User Interaction', 'search_query', resultsCount);
    
    // Track empty searches
    if (resultsCount === 0) {
      trackEvent('search_no_results', 'User Interaction', query);
    }
  }, []);

  const trackPageView = useCallback((pageName: string) => {
    if (!config.enableAnalytics) return;
    
    trackEvent('page_view', 'Navigation', pageName);
  }, []);

  return {
    trackClick,
    trackFormSubmit,
    trackSearch,
    trackPageView,
  };
};

// Hook for tracking API performance
export const useApiPerformanceTracking = () => {
  const trackApiCall = useCallback(async <T>(
    apiName: string,
    apiCall: () => Promise<T>
  ): Promise<T> => {
    const startTime = performance.now();
    
    try {
      const result = await apiCall();
      const duration = performance.now() - startTime;
      
      // Track successful API calls
      trackEvent('api_call_success', 'API Performance', apiName, Math.round(duration));
      
      if (config.enableDebugMode) {
        console.log(`API call ${apiName} completed in ${duration.toFixed(2)}ms`);
      }
      
      // Track slow API calls
      if (duration > 2000) { // 2 second threshold
        trackEvent('api_call_slow', 'API Performance', apiName, Math.round(duration));
      }
      
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      // Track failed API calls
      trackEvent('api_call_error', 'API Performance', apiName, Math.round(duration));
      
      if (config.enableDebugMode) {
        console.error(`API call ${apiName} failed after ${duration.toFixed(2)}ms:`, error);
      }
      
      throw error;
    }
  }, []);

  return { trackApiCall };
};

export default {
  usePerformanceTracking,
  useInteractionTracking,
  useApiPerformanceTracking,
};