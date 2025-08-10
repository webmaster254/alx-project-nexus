// Common reusable components
export { default as Header } from './Header';
export { default as Footer } from './Footer';
export { default as Breadcrumb } from './Breadcrumb';
export type { BreadcrumbItem } from './Breadcrumb';
export { default as BottomNavigation } from './BottomNavigation';
export { LoadingSpinner, ButtonSpinner, LoadingOverlay } from './LoadingSpinner';
export { ErrorBoundary, useErrorHandler } from './ErrorBoundary';
export { 
  ErrorDisplay, 
  NetworkErrorDisplay, 
  NotFoundErrorDisplay, 
  ValidationErrorDisplay 
} from './ErrorDisplay';
export { 
  EmptyState, 
  NoJobsFound, 
  NoSearchResults, 
  NoApplications 
} from './EmptyState';
export { OfflineIndicator, OfflineBanner } from './OfflineIndicator';
export { default as ResponsiveButton } from './ResponsiveButton';
export { default as LazyImage } from './LazyImage';
export { default as PerformanceMonitor } from './PerformanceMonitor';
