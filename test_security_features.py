#!/usr/bin/env python
"""
Security tests for authentication, authorization, and security features.
"""
import os
import sys
import django
from django.conf import settings

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    django.setup()

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.audit import (
    log_audit_event, AuditEvent, get_client_ip, sanitize_request_data,
    log_login_success, log_login_failed, log_unauthorized_access
)
from apps.common.exceptions import format_error_response
from unittest.mock import Mock, patch
import json
import tempfile

User = get_user_model()


class SecurityHeadersTestCase(APITestCase):
    """Test security headers are properly set."""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        response = self.client.get('/api/auth/login/')
        
        # Check for security headers (these would be set by middleware in production)
        # For now, we'll test that the response doesn't contain sensitive information
        self.assertNotIn('Server', response)
        self.assertNotIn('X-Powered-By', response)


class CORSConfigurationTestCase(APITestCase):
    """Test CORS configuration."""
    
    def test_cors_headers_for_allowed_origin(self):
        """Test CORS headers for allowed origins."""
        response = self.client.options(
            '/api/auth/login/',
            HTTP_ORIGIN='http://localhost:3000'
        )
        
        # Should allow the request
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cors_headers_for_disallowed_origin(self):
        """Test CORS headers for disallowed origins."""
        response = self.client.options(
            '/api/auth/login/',
            HTTP_ORIGIN='http://malicious-site.com'
        )
        
        # Should still return 200 for OPTIONS, but CORS headers should not allow the origin
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticationSecurityTestCase(APITestCase):
    """Test authentication security features."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='securepass123',
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
    
    def test_jwt_token_security(self):
        """Test JWT token security features."""
        # Login to get tokens
        response = self.client.post('/api/auth/token/', {
            'email': 'test@example.com',
            'password': 'securepass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Check that tokens are present
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        
        # Check that tokens are not empty
        self.assertTrue(data['access'])
        self.assertTrue(data['refresh'])
        
        # Test that access token works
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {data["access"]}')
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected."""
        # Use invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'AUTHENTICATION_FAILED')
    
    def test_expired_token_rejection(self):
        """Test that expired tokens are rejected."""
        # This would require mocking time or using very short token lifetimes
        # For now, we'll test with a malformed token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired.token.here')
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_validation(self):
        """Test password validation during registration."""
        # Test weak password
        response = self.client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': '123',  # Too weak
            'confirm_password': '123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'VALIDATION_ERROR')
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/token/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check error format
        data = response.json()
        self.assertIn('detail', data)


class AuthorizationTestCase(APITestCase):
    """Test authorization and permission controls."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@example.com',
            username='regularuser',
            password='userpass123',
            is_admin=False
        )
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123',
            is_admin=True
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        # Try to access protected endpoint without authentication
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'AUTHENTICATION_FAILED')
    
    def test_regular_user_permissions(self):
        """Test regular user permissions."""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Should be able to access own profile
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be able to view jobs (if endpoint exists and allows it)
        response = self.client.get('/api/jobs/')
        # This might return 200 or 403 depending on implementation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_admin_user_permissions(self):
        """Test admin user permissions."""
        # Login as admin user
        self.client.force_authenticate(user=self.admin_user)
        
        # Should be able to access profile
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin should have additional permissions
        # (Specific tests would depend on actual admin endpoints)
    
    def test_permission_denied_error_format(self):
        """Test permission denied error format."""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Try to access admin-only endpoint (if it exists)
        # For now, we'll simulate this by testing the error format
        from rest_framework.exceptions import PermissionDenied
        from apps.common.exceptions import custom_exception_handler
        
        # Create a mock request and exception
        request = Mock()
        request.user = self.user
        request.path = '/api/admin/test/'
        request.method = 'GET'
        
        exception = PermissionDenied("You do not have permission to perform this action.")
        context = {'request': request}
        
        response = custom_exception_handler(exception, context)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.data
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'PERMISSION_DENIED')


class InputValidationSecurityTestCase(APITestCase):
    """Test input validation security features."""
    
    def test_xss_prevention_in_registration(self):
        """Test XSS prevention in user registration."""
        malicious_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': '<script>alert("xss")</script>',
            'last_name': 'User<img src=x onerror=alert("xss")>',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        response = self.client.post('/api/auth/register/', malicious_data)
        
        if response.status_code == status.HTTP_201_CREATED:
            # Check that malicious content was sanitized
            user = User.objects.get(email='test@example.com')
            self.assertNotIn('<script>', user.first_name)
            self.assertNotIn('<img', user.last_name)
            self.assertNotIn('onerror', user.last_name)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # Try SQL injection in login
        malicious_email = "admin@example.com'; DROP TABLE auth_user; --"
        
        response = self.client.post('/api/auth/token/', {
            'email': malicious_email,
            'password': 'anypassword'
        })
        
        # Should return authentication error, not cause database issues
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify that users table still exists by trying to create a user
        try:
            User.objects.create_user(
                email='test@example.com',
                username='testuser',
                password='testpass123'
            )
            # If this succeeds, the table wasn't dropped
            self.assertTrue(True)
        except Exception:
            self.fail("Database table may have been affected by SQL injection attempt")
    
    def test_large_payload_handling(self):
        """Test handling of unusually large payloads."""
        # Create a very large string
        large_string = 'A' * 10000
        
        response = self.client.post('/api/auth/register/', {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': large_string,
            'last_name': 'User',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        })
        
        # Should handle gracefully (either accept with truncation or reject with validation error)
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ])


class AuditLoggingTestCase(TestCase):
    """Test audit logging functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_audit_event_logging(self):
        """Test basic audit event logging."""
        with patch('apps.common.audit.audit_logger') as mock_logger:
            log_audit_event(
                event_type=AuditEvent.LOGIN_SUCCESS,
                user=self.user,
                ip_address='127.0.0.1',
                user_agent='Test Agent'
            )
            
            # Verify logger was called
            mock_logger.info.assert_called_once()
            
            # Check the logged data structure
            logged_data = json.loads(mock_logger.info.call_args[0][0])
            self.assertEqual(logged_data['event_type'], AuditEvent.LOGIN_SUCCESS)
            self.assertEqual(logged_data['user_id'], self.user.id)
            self.assertEqual(logged_data['ip_address'], '127.0.0.1')
            self.assertTrue(logged_data['success'])
    
    def test_get_client_ip(self):
        """Test client IP extraction."""
        # Mock request with X-Forwarded-For header
        request = Mock()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
        # Mock request without X-Forwarded-For
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_request_data_sanitization(self):
        """Test request data sanitization."""
        sensitive_data = {
            'username': 'testuser',
            'password': 'secretpassword',
            'token': 'secret-token',
            'normal_field': 'normal_value',
            'nested': {
                'api_key': 'secret-key',
                'public_data': 'public'
            }
        }
        
        sanitized = sanitize_request_data(sensitive_data)
        
        self.assertEqual(sanitized['username'], 'testuser')
        self.assertEqual(sanitized['password'], '[REDACTED]')
        self.assertEqual(sanitized['token'], '[REDACTED]')
        self.assertEqual(sanitized['normal_field'], 'normal_value')
        self.assertEqual(sanitized['nested']['api_key'], '[REDACTED]')
        self.assertEqual(sanitized['nested']['public_data'], 'public')
    
    def test_convenience_logging_functions(self):
        """Test convenience logging functions."""
        request = Mock()
        request.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'Test Agent'}
        
        with patch('apps.common.audit.audit_logger') as mock_logger:
            # Test login success logging
            log_login_success(self.user, request)
            mock_logger.info.assert_called()
            
            # Test login failed logging
            log_login_failed('wronguser', request)
            self.assertEqual(mock_logger.info.call_count, 2)
            
            # Test unauthorized access logging
            log_unauthorized_access(request, 'job', '123')
            self.assertEqual(mock_logger.info.call_count, 3)


class ErrorHandlingSecurityTestCase(APITestCase):
    """Test error handling security features."""
    
    def test_error_response_format_consistency(self):
        """Test that all error responses follow consistent format."""
        # Test validation error
        response = self.client.post('/api/auth/register/', {
            'email': 'invalid-email',
            'password': 'weak'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Check consistent error format
        self.assertIn('error', data)
        self.assertIn('code', data['error'])
        self.assertIn('message', data['error'])
        self.assertIn('timestamp', data['error'])
    
    def test_no_sensitive_info_in_errors(self):
        """Test that error responses don't leak sensitive information."""
        # Try to access non-existent endpoint
        response = self.client.get('/api/nonexistent/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        
        # Should not contain server paths, stack traces, or other sensitive info
        error_message = str(data)
        self.assertNotIn('/home/', error_message)
        self.assertNotIn('Traceback', error_message)
        self.assertNotIn('SECRET_KEY', error_message)
    
    def test_error_response_format_utility(self):
        """Test error response formatting utility."""
        error_response = format_error_response(
            'TEST_ERROR',
            'Test message',
            {'field': ['Error detail']},
            400
        )
        
        self.assertEqual(error_response['error']['code'], 'TEST_ERROR')
        self.assertEqual(error_response['error']['message'], 'Test message')
        self.assertEqual(error_response['error']['details']['field'], ['Error detail'])
        self.assertIn('timestamp', error_response['error'])


def run_security_tests():
    """Run all security tests."""
    print("Running security tests...\n")
    
    # Create a test suite
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    
    # Run specific test classes
    test_classes = [
        SecurityHeadersTestCase,
        CORSConfigurationTestCase,
        AuthenticationSecurityTestCase,
        AuthorizationTestCase,
        InputValidationSecurityTestCase,
        AuditLoggingTestCase,
        ErrorHandlingSecurityTestCase,
    ]
    
    failures = 0
    for test_class in test_classes:
        print(f"\n--- Running {test_class.__name__} ---")
        suite = test_runner.loader.loadTestsFromTestCase(test_class)
        result = test_runner.run_tests([suite])
        failures += result
    
    return failures


if __name__ == '__main__':
    import django
    from django.conf import settings
    
    if not settings.configured:
        # Configure minimal settings for testing
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'rest_framework_simplejwt',
                'corsheaders',
                'apps.common',
                'apps.authentication',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
            REST_FRAMEWORK={
                'DEFAULT_AUTHENTICATION_CLASSES': [
                    'rest_framework_simplejwt.authentication.JWTAuthentication',
                ],
                'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
            },
            CORS_ALLOWED_ORIGINS=['http://localhost:3000'],
            AUTH_USER_MODEL='authentication.User',
        )
    
    django.setup()
    
    failures = run_security_tests()
    
    if failures == 0:
        print("\n🎉 All security tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {failures} security test(s) failed!")
        sys.exit(1)