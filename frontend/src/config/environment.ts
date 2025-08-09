// Environment configuration utility
export interface EnvironmentConfig {
  apiBaseUrl: string;
  apiTimeout: number;
  appName: string;
  appVersion: string;
  environment: 'development' | 'staging' | 'production';
  enableAnalytics: boolean;
  enableErrorTracking: boolean;
  enablePerformanceMonitoring: boolean;
  enableDebugMode: boolean;
  enableCSP: boolean;
  enableServiceWorker: boolean;
  sentryDsn?: string;
  googleAnalyticsId?: string;
  hotjarId?: string;
  allowedOrigins: string[];
  cacheDuration: number;
  defaultTheme: 'light' | 'dark';
  enableDarkMode: boolean;
  itemsPerPage: number;
}

// Helper function to parse boolean environment variables
const parseBoolean = (value: string | undefined, defaultValue: boolean = false): boolean => {
  if (!value) return defaultValue;
  return value.toLowerCase() === 'true';
};

// Helper function to parse array environment variables
const parseArray = (value: string | undefined, defaultValue: string[] = []): string[] => {
  if (!value) return defaultValue;
  return value.split(',').map(item => item.trim());
};

// Helper function to parse number environment variables
const parseNumber = (value: string | undefined, defaultValue: number): number => {
  if (!value) return defaultValue;
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? defaultValue : parsed;
};

// Environment configuration
export const config: EnvironmentConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api',
  apiTimeout: parseNumber(import.meta.env.VITE_API_TIMEOUT, 10000),
  appName: import.meta.env.VITE_APP_NAME || 'Job Board',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  environment: (import.meta.env.VITE_APP_ENVIRONMENT as EnvironmentConfig['environment']) || 'development',
  enableAnalytics: parseBoolean(import.meta.env.VITE_ENABLE_ANALYTICS),
  enableErrorTracking: parseBoolean(import.meta.env.VITE_ENABLE_ERROR_TRACKING),
  enablePerformanceMonitoring: parseBoolean(import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING),
  enableDebugMode: parseBoolean(import.meta.env.VITE_ENABLE_DEBUG_MODE, true),
  enableCSP: parseBoolean(import.meta.env.VITE_ENABLE_CSP),
  enableServiceWorker: parseBoolean(import.meta.env.VITE_ENABLE_SERVICE_WORKER),
  sentryDsn: import.meta.env.VITE_SENTRY_DSN,
  googleAnalyticsId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID,
  hotjarId: import.meta.env.VITE_HOTJAR_ID,
  allowedOrigins: parseArray(import.meta.env.VITE_ALLOWED_ORIGINS, ['http://localhost:3000']),
  cacheDuration: parseNumber(import.meta.env.VITE_CACHE_DURATION, 300000),
  defaultTheme: (import.meta.env.VITE_DEFAULT_THEME as 'light' | 'dark') || 'light',
  enableDarkMode: parseBoolean(import.meta.env.VITE_ENABLE_DARK_MODE, true),
  itemsPerPage: parseNumber(import.meta.env.VITE_ITEMS_PER_PAGE, 20),
};

// Development helpers
export const isDevelopment = config.environment === 'development';
export const isProduction = config.environment === 'production';
export const isStaging = config.environment === 'staging';

// Debug logging (only in development)
if (isDevelopment && config.enableDebugMode) {
  console.log('Environment Configuration:', config);
}

export default config;