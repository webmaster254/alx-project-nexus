"""
Production settings for job board backend project.
"""

from .base import *
import os
import logging.config
from decouple import config


DEBUG = config('DEBUG', default=False, cast=bool)

# Environment validation
REQUIRED_ENV_VARS = [
    'SECRET_KEY',
    'DB_NAME',
    'DB_USER', 
    'DB_PASSWORD',
    'DB_HOST',
    'ALLOWED_HOSTS',
]

# Validate required environment variables
missing_vars = []
for var in REQUIRED_ENV_VARS:
    if not config(var, default=None):
        missing_vars.append(var)

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Override base settings for production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
SECRET_KEY = config('SECRET_KEY')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Cookie security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600  # 1 hour

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Frame options
X_FRAME_OPTIONS = 'DENY'

# Additional security headers
SECURE_PERMISSIONS_POLICY = {
    'accelerometer': [],
    'ambient-light-sensor': [],
    'autoplay': [],
    'battery': [],
    'camera': [],
    'cross-origin-isolated': [],
    'display-capture': [],
    'document-domain': [],
    'encrypted-media': [],
    'execution-while-not-rendered': [],
    'execution-while-out-of-viewport': [],
    'fullscreen': [],
    'geolocation': [],
    'gyroscope': [],
    'magnetometer': [],
    'microphone': [],
    'midi': [],
    'navigation-override': [],
    'payment': [],
    'picture-in-picture': [],
    'publickey-credentials-get': [],
    'screen-wake-lock': [],
    'sync-xhr': [],
    'usb': [],
    'web-share': [],
    'xr-spatial-tracking': [],
}

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# Rate limiting for production
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Database configuration with connection pooling for production
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use DATABASE_URL if provided (recommended for cloud deployments)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=config('DB_CONN_MAX_AGE', default=600, cast=int),
            ssl_require=True
        )
    }
    # Add connection pooling options
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': config('DB_MAX_CONNECTIONS', default=20, cast=int),
        'MIN_CONNS': config('DB_MIN_CONNECTIONS', default=5, cast=int),
        'connect_timeout': config('DB_CONNECT_TIMEOUT', default=10, cast=int),
        'application_name': config('DB_APPLICATION_NAME', default='job_board_backend'),
    })
else:
    # Individual database parameters with connection pooling
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': 'require',
                'MAX_CONNS': config('DB_MAX_CONNECTIONS', default=20, cast=int),
                'MIN_CONNS': config('DB_MIN_CONNECTIONS', default=5, cast=int),
                'connect_timeout': config('DB_CONNECT_TIMEOUT', default=10, cast=int),
                'application_name': config('DB_APPLICATION_NAME', default='job_board_backend'),
                # Connection pooling settings
                'server_side_binding': True,
                'prepared_statement_cache_size': config('DB_PREPARED_STATEMENT_CACHE_SIZE', default=100, cast=int),
            },
            'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
            'CONN_HEALTH_CHECKS': config('DB_CONN_HEALTH_CHECKS', default=True, cast=bool),
        }
    }

# Database optimization settings
DATABASE_ROUTERS = []
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Query optimization
DATABASES['default']['OPTIONS'].update({
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
}) if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql' else None

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Static files configuration for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Production logging configuration with monitoring support
LOG_DIR = config('LOG_DIR', default='/var/log/django')
LOG_LEVEL = config('LOG_LEVEL', default='INFO')
ENABLE_STRUCTURED_LOGGING = config('ENABLE_STRUCTURED_LOGGING', default=True, cast=bool)

# Ensure log directory exists
import os
os.makedirs(LOG_DIR, exist_ok=True)

# Enhanced logging configuration for production monitoring
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "{asctime}", "level": "{levelname}", "module": "{module}", "process": {process}, "thread": {thread}, "message": "{message}"}',
            'style': '{',
        } if ENABLE_STRUCTURED_LOGGING else {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'audit': {
            'format': '{"timestamp": "{asctime}", "type": "AUDIT", "message": "{message}"}',
            'style': '{',
        } if ENABLE_STRUCTURED_LOGGING else {
            'format': '{asctime} AUDIT {message}',
            'style': '{',
        },
        'security': {
            'format': '{"timestamp": "{asctime}", "type": "SECURITY", "level": "{levelname}", "message": "{message}"}',
            'style': '{',
        } if ENABLE_STRUCTURED_LOGGING else {
            'format': '{asctime} SECURITY {levelname} {message}',
            'style': '{',
        },
        'performance': {
            'format': '{"timestamp": "{asctime}", "type": "PERFORMANCE", "message": "{message}"}',
            'style': '{',
        } if ENABLE_STRUCTURED_LOGGING else {
            'format': '{asctime} PERFORMANCE {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'json' if ENABLE_STRUCTURED_LOGGING else 'verbose',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'maxBytes': config('LOG_MAX_BYTES', default=50*1024*1024, cast=int),  # 50MB
            'backupCount': config('LOG_BACKUP_COUNT', default=10, cast=int),
            'formatter': 'json' if ENABLE_STRUCTURED_LOGGING else 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'audit.log'),
            'maxBytes': config('AUDIT_LOG_MAX_BYTES', default=100*1024*1024, cast=int),  # 100MB
            'backupCount': config('AUDIT_LOG_BACKUP_COUNT', default=20, cast=int),
            'formatter': 'audit',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'security.log'),
            'maxBytes': config('SECURITY_LOG_MAX_BYTES', default=100*1024*1024, cast=int),  # 100MB
            'backupCount': config('SECURITY_LOG_BACKUP_COUNT', default=20, cast=int),
            'formatter': 'security',
        },
        'performance_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'performance.log'),
            'maxBytes': config('PERFORMANCE_LOG_MAX_BYTES', default=50*1024*1024, cast=int),  # 50MB
            'backupCount': config('PERFORMANCE_LOG_BACKUP_COUNT', default=10, cast=int),
            'formatter': 'performance',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'maxBytes': config('ERROR_LOG_MAX_BYTES', default=100*1024*1024, cast=int),  # 100MB
            'backupCount': config('ERROR_LOG_BACKUP_COUNT', default=20, cast=int),
            'formatter': 'json' if ENABLE_STRUCTURED_LOGGING else 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'security_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['performance_file'],
            'level': config('DB_LOG_LEVEL', default='WARNING'),
            'propagate': False,
        },
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'performance': {
            'handlers': ['performance_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Add syslog handler if available (for centralized logging)
if config('ENABLE_SYSLOG', default=False, cast=bool):
    LOGGING['handlers']['syslog'] = {
        'level': 'INFO',
        'class': 'logging.handlers.SysLogHandler',
        'formatter': 'json' if ENABLE_STRUCTURED_LOGGING else 'verbose',
        'address': config('SYSLOG_ADDRESS', default='/dev/log'),
        'facility': config('SYSLOG_FACILITY', default='local0'),
    }
    # Add syslog to critical loggers
    LOGGING['loggers']['audit']['handlers'].append('syslog')
    LOGGING['loggers']['security']['handlers'].append('syslog')
    LOGGING['loggers']['django.request']['handlers'].append('syslog')

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://yourdomain.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Additional production optimizations
USE_TZ = True
TIME_ZONE = config('TIME_ZONE', default='UTC')

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_NAME = config('SESSION_COOKIE_NAME', default='sessionid')
SESSION_EXPIRE_AT_BROWSER_CLOSE = config('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=True, cast=bool)

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=2621440, cast=int)  # 2.5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=2621440, cast=int)  # 2.5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = config('DATA_UPLOAD_MAX_NUMBER_FIELDS', default=1000, cast=int)

# Performance settings
USE_ETAGS = config('USE_ETAGS', default=True, cast=bool)
PREPEND_WWW = config('PREPEND_WWW', default=False, cast=bool)
APPEND_SLASH = config('APPEND_SLASH', default=True, cast=bool)

# Internationalization
USE_I18N = config('USE_I18N', default=True, cast=bool)
USE_L10N = config('USE_L10N', default=True, cast=bool)
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

# Media files configuration for production
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))

# Static files configuration for production
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

# Whitenoise configuration for static files (if using)
if config('USE_WHITENOISE', default=False, cast=bool):
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = False

# Monitoring and health check settings
HEALTH_CHECK_ENABLED = config('HEALTH_CHECK_ENABLED', default=True, cast=bool)
HEALTH_CHECK_DATABASE = config('HEALTH_CHECK_DATABASE', default=True, cast=bool)
HEALTH_CHECK_CACHE = config('HEALTH_CHECK_CACHE', default=True, cast=bool)
HEALTH_CHECK_STORAGE = config('HEALTH_CHECK_STORAGE', default=True, cast=bool)

# Application monitoring
ENABLE_PERFORMANCE_MONITORING = config('ENABLE_PERFORMANCE_MONITORING', default=True, cast=bool)
SLOW_QUERY_THRESHOLD = config('SLOW_QUERY_THRESHOLD', default=1.0, cast=float)  # seconds

# Error reporting
ADMINS = config('ADMINS', default='', cast=lambda v: [tuple(admin.split(':')) for admin in v.split(',') if ':' in admin])
MANAGERS = ADMINS
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@jobboard.com')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@jobboard.com')

# Security enhancements
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Additional middleware for production
if config('ENABLE_SECURITY_MIDDLEWARE', default=True, cast=bool):
    MIDDLEWARE.insert(0, 'django.middleware.security.SecurityMiddleware')

# Custom error pages
CUSTOM_ERROR_PAGES = config('CUSTOM_ERROR_PAGES', default=True, cast=bool)