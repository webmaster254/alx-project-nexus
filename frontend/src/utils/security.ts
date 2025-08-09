import { config } from '../config/environment';

// Content Security Policy configuration
export const generateCSP = (): string => {
  const baseCSP = {
    'default-src': ["'self'"],
    'script-src': [
      "'self'",
      ...(config.enableDebugMode ? ["'unsafe-inline'", "'unsafe-eval'"] : []),
      ...(config.enableAnalytics && config.googleAnalyticsId ? [
        'https://www.google-analytics.com',
        'https://www.googletagmanager.com'
      ] : []),
    ],
    'style-src': [
      "'self'",
      "'unsafe-inline'", // Required for Tailwind CSS
      'https://fonts.googleapis.com'
    ],
    'font-src': [
      "'self'",
      'https://fonts.gstatic.com'
    ],
    'img-src': [
      "'self'",
      'data:',
      'https:',
      'blob:'
    ],
    'connect-src': [
      "'self'",
      config.apiBaseUrl,
      ...(config.enableAnalytics && config.googleAnalyticsId ? [
        'https://www.google-analytics.com'
      ] : []),
      ...(config.enableErrorTracking && config.sentryDsn ? [
        'https://*.sentry.io'
      ] : []),
    ],
    'frame-ancestors': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'object-src': ["'none'"],
    'media-src': ["'self'"],
  };

  // Convert CSP object to string
  return Object.entries(baseCSP)
    .map(([directive, sources]) => `${directive} ${sources.join(' ')}`)
    .join('; ');
};

// Security headers configuration
export const securityHeaders = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
  ...(config.isProduction && {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
  }),
  ...(config.enableCSP && {
    'Content-Security-Policy': generateCSP()
  }),
};

// Apply security headers to meta tags (for client-side enforcement)
export const applySecurityHeaders = (): void => {
  if (typeof document === 'undefined') return;

  // Apply CSP via meta tag if enabled
  if (config.enableCSP) {
    const cspMeta = document.createElement('meta');
    cspMeta.httpEquiv = 'Content-Security-Policy';
    cspMeta.content = generateCSP();
    document.head.appendChild(cspMeta);
  }

  // Apply other security headers via meta tags where possible
  const referrerMeta = document.createElement('meta');
  referrerMeta.name = 'referrer';
  referrerMeta.content = 'strict-origin-when-cross-origin';
  document.head.appendChild(referrerMeta);
};

// Sanitize user input to prevent XSS
export const sanitizeInput = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};

// Validate URLs to prevent open redirects
export const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return config.allowedOrigins.some(origin => 
      urlObj.origin === origin || urlObj.origin === window.location.origin
    );
  } catch {
    return false;
  }
};

// Safe redirect function
export const safeRedirect = (url: string): void => {
  if (isValidUrl(url)) {
    window.location.href = url;
  } else {
    console.warn('Attempted redirect to invalid URL:', url);
  }
};

export default {
  generateCSP,
  securityHeaders,
  applySecurityHeaders,
  sanitizeInput,
  isValidUrl,
  safeRedirect,
};