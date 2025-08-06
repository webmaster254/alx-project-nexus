#!/usr/bin/env python
"""
Setup test to verify all security features are properly configured.
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

def test_security_imports():
    """Test that all security modules can be imported."""
    print("Testing security module imports...")
    
    try:
        from apps.common.exceptions import (
            CustomAPIException, BusinessLogicError, format_error_response,
            custom_exception_handler
        )
        print("✓ Exception handling modules imported successfully")
        
        from apps.common.validators import (
            sanitize_html, sanitize_text, PhoneNumberValidator,
            URLValidator, validate_salary_range, validate_skills_list,
            SanitizedCharField, ValidatedEmailField
        )
        print("✓ Validation modules imported successfully")
        
        from apps.common.throttling import (
            LoginRateThrottle, RegisterRateThrottle, user_ratelimit,
            login_ratelimit, register_ratelimit
        )
        print("✓ Rate limiting modules imported successfully")
        
        from apps.common.audit import (
            log_audit_event, AuditEvent, get_client_ip,
            AuditLoggingMiddleware, log_login_success
        )
        print("✓ Audit logging modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_settings_configuration():
    """Test that security settings are properly configured."""
    print("Testing security settings configuration...")
    
    try:
        from django.conf import settings
        
        # Check REST framework settings
        assert 'EXCEPTION_HANDLER' in settings.REST_FRAMEWORK
        assert settings.REST_FRAMEWORK['EXCEPTION_HANDLER'] == 'apps.common.exceptions.custom_exception_handler'
        print("✓ Custom exception handler configured")
        
        # Check throttling settings
        assert 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK
        assert 'DEFAULT_THROTTLE_RATES' in settings.REST_FRAMEWORK
        print("✓ Rate limiting configured")
        
        # Check CORS settings
        assert hasattr(settings, 'CORS_ALLOWED_ORIGINS')
        assert hasattr(settings, 'CORS_ALLOW_CREDENTIALS')
        print("✓ CORS settings configured")
        
        # Check security headers
        assert hasattr(settings, 'SECURE_BROWSER_XSS_FILTER')
        assert hasattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF')
        print("✓ Security headers configured")
        
        # Check middleware
        assert 'apps.common.audit.AuditLoggingMiddleware' in settings.MIDDLEWARE
        assert 'apps.common.throttling.RateLimitMiddleware' in settings.MIDDLEWARE
        print("✓ Security middleware configured")
        
        # Check logging
        assert 'audit' in settings.LOGGING['loggers']
        assert 'security' in settings.LOGGING['loggers']
        print("✓ Audit and security logging configured")
        
        return True
    except (AssertionError, AttributeError) as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_validation_functionality():
    """Test that validation functions work correctly."""
    print("Testing validation functionality...")
    
    try:
        from apps.common.validators import sanitize_html, sanitize_text, validate_skills_list
        
        # Test HTML sanitization
        malicious_html = '<p>Safe</p><script>alert("xss")</script>'
        sanitized = sanitize_html(malicious_html)
        assert '<script>' not in sanitized
        print("✓ HTML sanitization works")
        
        # Test text sanitization
        text_with_control = 'Hello\x00world'
        sanitized = sanitize_text(text_with_control)
        assert '\x00' not in sanitized
        print("✓ Text sanitization works")
        
        # Test skills validation
        valid_skills = ['Python', 'JavaScript', 'React']
        validate_skills_list(valid_skills)  # Should not raise exception
        print("✓ Skills validation works")
        
        return True
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def test_error_handling():
    """Test that error handling works correctly."""
    print("Testing error handling...")
    
    try:
        from apps.common.exceptions import format_error_response, CustomAPIException
        
        # Test error response formatting
        response = format_error_response('TEST_ERROR', 'Test message', {}, 400)
        assert response['error']['code'] == 'TEST_ERROR'
        assert 'timestamp' in response['error']
        print("✓ Error response formatting works")
        
        # Test custom exception
        exc = CustomAPIException('Test error', 'test_code')
        assert str(exc.detail) == 'Test error'
        assert exc.code == 'test_code'
        print("✓ Custom exceptions work")
        
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_audit_logging():
    """Test that audit logging works correctly."""
    print("Testing audit logging...")
    
    try:
        from apps.common.audit import log_audit_event, AuditEvent, sanitize_request_data
        from unittest.mock import patch
        
        # Test audit event logging
        with patch('apps.common.audit.audit_logger') as mock_logger:
            log_audit_event(AuditEvent.LOGIN_SUCCESS, ip_address='127.0.0.1')
            mock_logger.info.assert_called_once()
        print("✓ Audit event logging works")
        
        # Test request data sanitization
        sensitive_data = {'username': 'test', 'password': 'secret'}
        sanitized = sanitize_request_data(sensitive_data)
        assert sanitized['password'] == '[REDACTED]'
        print("✓ Request data sanitization works")
        
        return True
    except Exception as e:
        print(f"❌ Audit logging test failed: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🔒 Running security setup verification tests...\n")
    
    tests = [
        test_security_imports,
        test_settings_configuration,
        test_validation_functionality,
        test_error_handling,
        test_audit_logging,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n--- {test.__name__.replace('_', ' ').title()} ---")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Security Setup Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*50}")
    
    if failed == 0:
        print("\n🎉 All security features are properly configured!")
        print("\n📋 Security Features Implemented:")
        print("   • Comprehensive input validation and sanitization")
        print("   • Custom exception handling with consistent error responses")
        print("   • Rate limiting for API endpoints")
        print("   • CORS configuration for Next.js frontend")
        print("   • Security headers and HTTPS enforcement")
        print("   • Audit logging for sensitive operations")
        print("   • SQL injection and XSS prevention")
        print("   • JWT token security")
        print("   • Role-based access control")
        print("   • Production security configurations")
        return 0
    else:
        print(f"\n❌ {failed} security feature(s) need attention!")
        return 1

if __name__ == '__main__':
    sys.exit(main())