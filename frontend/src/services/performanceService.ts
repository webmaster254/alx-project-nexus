import { config } from '../config/environment';

// Performance metrics interface
export interface PerformanceMetrics {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
}

// Core Web Vitals thresholds
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 }, // Largest Contentful Paint
  FID: { good: 100, poor: 300 },   // First Input Delay
  CLS: { good: 0.1, poor: 0.25 },  // Cumulative Layout Shift
  FCP: { good: 1800, poor: 3000 }, // First Contentful Paint
  TTFB: { good: 800, poor: 1800 }, // Time to First Byte
};

// Get performance rating based on thresholds
const getPerformanceRating = (name: string, value: number): 'good' | 'needs-improvement' | 'poor' => {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';
  
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
};

// Performance observer for Core Web Vitals
class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private observers: PerformanceObserver[] = [];

  constructor() {
    if (!config.enablePerformanceMonitoring || typeof window === 'undefined') {
      return;
    }

    this.initializeObservers();
  }

  private initializeObservers(): void {
    // Largest Contentful Paint (LCP)
    this.observeMetric('largest-contentful-paint', (entries) => {
      const lastEntry = entries[entries.length - 1];
      this.recordMetric('LCP', lastEntry.startTime);
    });

    // First Input Delay (FID)
    this.observeMetric('first-input', (entries) => {
      const firstEntry = entries[0];
      this.recordMetric('FID', firstEntry.processingStart - firstEntry.startTime);
    });

    // Cumulative Layout Shift (CLS)
    this.observeMetric('layout-shift', (entries) => {
      let clsValue = 0;
      for (const entry of entries) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      this.recordMetric('CLS', clsValue);
    });

    // Navigation timing metrics
    this.observeNavigationTiming();
  }

  private observeMetric(type: string, callback: (entries: PerformanceEntry[]) => void): void {
    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries());
      });
      observer.observe({ type, buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn(`Failed to observe ${type}:`, error);
    }
  }

  private observeNavigationTiming(): void {
    if (typeof window !== 'undefined' && window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const navigationStart = timing.navigationStart;

      // First Contentful Paint
      if (window.performance.getEntriesByType) {
        const paintEntries = window.performance.getEntriesByType('paint');
        const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.recordMetric('FCP', fcpEntry.startTime);
        }
      }

      // Time to First Byte
      const ttfb = timing.responseStart - navigationStart;
      this.recordMetric('TTFB', ttfb);

      // DOM Content Loaded
      const domContentLoaded = timing.domContentLoadedEventEnd - navigationStart;
      this.recordMetric('DCL', domContentLoaded);

      // Load Complete
      const loadComplete = timing.loadEventEnd - navigationStart;
      this.recordMetric('Load', loadComplete);
    }
  }

  private recordMetric(name: string, value: number): void {
    const metric: PerformanceMetrics = {
      name,
      value,
      rating: getPerformanceRating(name, value),
      timestamp: Date.now(),
    };

    this.metrics.push(metric);
    
    if (config.enableDebugMode) {
      console.log(`Performance Metric - ${name}:`, metric);
    }

    // Send to analytics if enabled
    this.sendToAnalytics(metric);
  }

  private sendToAnalytics(metric: PerformanceMetrics): void {
    if (!config.enableAnalytics) return;

    // Send to Google Analytics if configured
    if (config.googleAnalyticsId && typeof gtag !== 'undefined') {
      gtag('event', 'web_vitals', {
        event_category: 'Performance',
        event_label: metric.name,
        value: Math.round(metric.value),
        custom_map: { metric_rating: metric.rating },
      });
    }

    // Send to custom analytics endpoint
    this.sendToCustomAnalytics(metric);
  }

  private async sendToCustomAnalytics(metric: PerformanceMetrics): Promise<void> {
    try {
      await fetch(`${config.apiBaseUrl}/analytics/performance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metric: metric.name,
          value: metric.value,
          rating: metric.rating,
          timestamp: metric.timestamp,
          url: window.location.href,
          userAgent: navigator.userAgent,
        }),
      });
    } catch (error) {
      if (config.enableDebugMode) {
        console.warn('Failed to send performance metric to analytics:', error);
      }
    }
  }

  public getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  public getMetricsByName(name: string): PerformanceMetrics[] {
    return this.metrics.filter(metric => metric.name === name);
  }

  public getAverageMetric(name: string): number | null {
    const metrics = this.getMetricsByName(name);
    if (metrics.length === 0) return null;
    
    const sum = metrics.reduce((acc, metric) => acc + metric.value, 0);
    return sum / metrics.length;
  }

  public disconnect(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Hook for React components to access performance data
export const usePerformanceMetrics = () => {
  return {
    getMetrics: () => performanceMonitor.getMetrics(),
    getMetricsByName: (name: string) => performanceMonitor.getMetricsByName(name),
    getAverageMetric: (name: string) => performanceMonitor.getAverageMetric(name),
  };
};

// Initialize Google Analytics
export const initializeAnalytics = (): void => {
  if (!config.enableAnalytics || !config.googleAnalyticsId || typeof window === 'undefined') {
    return;
  }

  // Load Google Analytics script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${config.googleAnalyticsId}`;
  document.head.appendChild(script);

  // Initialize gtag
  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }
  (window as any).gtag = gtag;

  gtag('js', new Date());
  gtag('config', config.googleAnalyticsId, {
    send_page_view: false, // We'll send page views manually
  });
};

// Track page views
export const trackPageView = (path: string): void => {
  if (!config.enableAnalytics || typeof gtag === 'undefined') return;

  gtag('config', config.googleAnalyticsId, {
    page_path: path,
  });
};

// Track custom events
export const trackEvent = (action: string, category: string, label?: string, value?: number): void => {
  if (!config.enableAnalytics || typeof gtag === 'undefined') return;

  gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

export default {
  performanceMonitor,
  usePerformanceMetrics,
  initializeAnalytics,
  trackPageView,
  trackEvent,
};