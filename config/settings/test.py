"""
Test settings for job board backend project.
"""

from .base import *
import tempfile
import os
import sys

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None

# Test-specific settings
DEBUG = True

# Use temporary directory for media files during tests
MEDIA_ROOT = tempfile.mkdtemp()

# Disable caching during tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable rate limiting during tests
RATELIMIT_ENABLE = False

# Factory Boy settings
FACTORY_FOR_DJANGO_MODELS = True

# Test runner configuration
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Disable CORS during tests
CORS_ALLOW_ALL_ORIGINS = True

# JWT settings for testing
from datetime import timedelta
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Longer for tests
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,  # Disable rotation for simpler tests
})

# Disable throttling during tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Test database settings
if 'test' in sys.argv:
    # Use faster database settings for tests
    DATABASES['default']['OPTIONS'] = {
        'timeout': 20,
    }