"""
Django management command to check production readiness.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
import os
import sys
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check production readiness and configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues automatically',
        )
    
    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.fix_issues = options['fix']
        
        self.stdout.write(
            self.style.SUCCESS('Checking production readiness...\n')
        )
        
        checks = [
            self.check_debug_setting,
            self.check_secret_key,
            self.check_allowed_hosts,
            self.check_database_connection,
            self.check_cache_connection,
            self.check_static_files,
            self.check_media_files,
            self.check_log_directories,
            self.check_security_settings,
            self.check_environment_variables,
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for check in checks:
            try:
                result = check()
                if result == 'PASS':
                    passed += 1
                elif result == 'FAIL':
                    failed += 1
                elif result == 'WARNING':
                    warnings += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Check failed with exception: {e}')
                )
                failed += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Production Readiness Summary:')
        self.stdout.write(f'  Passed: {passed}')
        self.stdout.write(f'  Failed: {failed}')
        self.stdout.write(f'  Warnings: {warnings}')
        
        if failed > 0:
            self.stdout.write(
                self.style.ERROR('\nProduction deployment NOT recommended!')
            )
            sys.exit(1)
        elif warnings > 0:
            self.stdout.write(
                self.style.WARNING('\nProduction deployment possible with warnings.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nProduction deployment ready!')
            )
    
    def check_debug_setting(self):
        """Check if DEBUG is disabled."""
        self.stdout.write('Checking DEBUG setting... ', ending='')
        
        if settings.DEBUG:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write('  DEBUG is enabled in production!')
            if self.fix_issues:
                self.stdout.write('  Set DEBUG=False in environment variables')
            return 'FAIL'
        else:
            self.stdout.write(self.style.SUCCESS('PASS'))
            return 'PASS'
    
    def check_secret_key(self):
        """Check if SECRET_KEY is properly configured."""
        self.stdout.write('Checking SECRET_KEY... ', ending='')
        
        if not settings.SECRET_KEY:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write('  SECRET_KEY is not set!')
            return 'FAIL'
        
        if settings.SECRET_KEY == 'django-insecure-change-me-in-production':
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write('  SECRET_KEY is using default insecure value!')
            return 'FAIL'
        
        if len(settings.SECRET_KEY) < 50:
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write('  SECRET_KEY should be at least 50 characters long')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        return 'PASS'
    
    def check_allowed_hosts(self):
        """Check ALLOWED_HOSTS configuration."""
        self.stdout.write('Checking ALLOWED_HOSTS... ', ending='')
        
        if not settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write('  ALLOWED_HOSTS is empty!')
            return 'FAIL'
        
        if '*' in settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write('  ALLOWED_HOSTS contains wildcard (*)')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        if self.verbose:
            self.stdout.write(f'  Allowed hosts: {", ".join(settings.ALLOWED_HOSTS)}')
        return 'PASS'
    
    def check_database_connection(self):
        """Check database connectivity."""
        self.stdout.write('Checking database connection... ', ending='')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            if result and result[0] == 1:
                self.stdout.write(self.style.SUCCESS('PASS'))
                if self.verbose:
                    db_name = settings.DATABASES['default']['NAME']
                    self.stdout.write(f'  Connected to database: {db_name}')
                return 'PASS'
            else:
                self.stdout.write(self.style.ERROR('FAIL'))
                self.stdout.write('  Database query returned unexpected result')
                return 'FAIL'
                
        except Exception as e:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write(f'  Database connection failed: {e}')
            return 'FAIL'
    
    def check_cache_connection(self):
        """Check cache connectivity."""
        self.stdout.write('Checking cache connection... ', ending='')
        
        try:
            test_key = 'production_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, timeout=60)
            cached_value = cache.get(test_key)
            cache.delete(test_key)
            
            if cached_value == test_value:
                self.stdout.write(self.style.SUCCESS('PASS'))
                return 'PASS'
            else:
                self.stdout.write(self.style.WARNING('WARNING'))
                self.stdout.write('  Cache read/write test failed')
                return 'WARNING'
                
        except Exception as e:
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write(f'  Cache connection failed: {e}')
            return 'WARNING'
    
    def check_static_files(self):
        """Check static files configuration."""
        self.stdout.write('Checking static files... ', ending='')
        
        if not settings.STATIC_ROOT:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write('  STATIC_ROOT is not configured')
            return 'FAIL'
        
        static_root = settings.STATIC_ROOT
        if not os.path.exists(static_root):
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write(f'  STATIC_ROOT directory does not exist: {static_root}')
            if self.fix_issues:
                try:
                    os.makedirs(static_root, exist_ok=True)
                    self.stdout.write(f'  Created directory: {static_root}')
                except Exception as e:
                    self.stdout.write(f'  Could not create directory: {e}')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        if self.verbose:
            self.stdout.write(f'  Static root: {static_root}')
        return 'PASS'
    
    def check_media_files(self):
        """Check media files configuration."""
        self.stdout.write('Checking media files... ', ending='')
        
        if not settings.MEDIA_ROOT:
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write('  MEDIA_ROOT is not configured')
            return 'WARNING'
        
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write(f'  MEDIA_ROOT directory does not exist: {media_root}')
            if self.fix_issues:
                try:
                    os.makedirs(media_root, exist_ok=True)
                    self.stdout.write(f'  Created directory: {media_root}')
                except Exception as e:
                    self.stdout.write(f'  Could not create directory: {e}')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        if self.verbose:
            self.stdout.write(f'  Media root: {media_root}')
        return 'PASS'
    
    def check_log_directories(self):
        """Check log directories."""
        self.stdout.write('Checking log directories... ', ending='')
        
        log_dir = getattr(settings, 'LOG_DIR', '/var/log/django')
        
        if not os.path.exists(log_dir):
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write(f'  Log directory does not exist: {log_dir}')
            if self.fix_issues:
                try:
                    os.makedirs(log_dir, exist_ok=True)
                    self.stdout.write(f'  Created directory: {log_dir}')
                except Exception as e:
                    self.stdout.write(f'  Could not create directory: {e}')
            return 'WARNING'
        
        # Check if directory is writable
        test_file = os.path.join(log_dir, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            writable = True
        except Exception:
            writable = False
        
        if not writable:
            self.stdout.write(self.style.WARNING('WARNING'))
            self.stdout.write(f'  Log directory is not writable: {log_dir}')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        if self.verbose:
            self.stdout.write(f'  Log directory: {log_dir}')
        return 'PASS'
    
    def check_security_settings(self):
        """Check security settings."""
        self.stdout.write('Checking security settings... ', ending='')
        
        issues = []
        
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            issues.append('SECURE_SSL_REDIRECT is disabled')
        
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            issues.append('SESSION_COOKIE_SECURE is disabled')
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            issues.append('CSRF_COOKIE_SECURE is disabled')
        
        if issues:
            self.stdout.write(self.style.WARNING('WARNING'))
            for issue in issues:
                self.stdout.write(f'  {issue}')
            return 'WARNING'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        return 'PASS'
    
    def check_environment_variables(self):
        """Check required environment variables."""
        self.stdout.write('Checking environment variables... ', ending='')
        
        required_vars = [
            'SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_HOST',
            'ALLOWED_HOSTS',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.stdout.write(self.style.ERROR('FAIL'))
            self.stdout.write(f'  Missing variables: {", ".join(missing_vars)}')
            return 'FAIL'
        
        self.stdout.write(self.style.SUCCESS('PASS'))
        return 'PASS'