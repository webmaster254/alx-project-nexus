#!/usr/bin/env python
"""
Simple test script to verify validation utilities work correctly.
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

# Now we can import our modules
from apps.common.validators import (
    sanitize_html, sanitize_text, PhoneNumberValidator, 
    URLValidator, validate_salary_range, validate_skills_list
)
from apps.common.exceptions import format_error_response
from django.core.exceptions import ValidationError

def test_sanitize_html():
    """Test HTML sanitization."""
    print("Testing HTML sanitization...")
    
    # Test safe HTML
    safe_html = '<p>Hello <strong>world</strong></p>'
    result = sanitize_html(safe_html)
    assert result == safe_html, f"Expected {safe_html}, got {result}"
    
    # Test malicious HTML
    malicious_html = '<p>Hello</p><script>alert("xss")</script>'
    result = sanitize_html(malicious_html)
    expected = '<p>Hello</p>'
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ HTML sanitization works correctly")

def test_sanitize_text():
    """Test text sanitization."""
    print("Testing text sanitization...")
    
    # Test normal text
    normal_text = 'Hello world!'
    result = sanitize_text(normal_text)
    assert result == normal_text, f"Expected {normal_text}, got {result}"
    
    # Test control character removal
    text_with_control = 'Hello\x00world'
    result = sanitize_text(text_with_control)
    expected = 'Helloworld'
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Text sanitization works correctly")

def test_phone_validator():
    """Test phone number validation."""
    print("Testing phone number validation...")
    
    validator = PhoneNumberValidator()
    
    # Valid phone numbers
    valid_phones = ['+1234567890', '1234567890']
    for phone in valid_phones:
        try:
            validator(phone)
        except ValidationError:
            assert False, f"Valid phone number {phone} was rejected"
    
    # Invalid phone numbers
    invalid_phones = ['123', 'abc123']
    for phone in invalid_phones:
        try:
            validator(phone)
            assert False, f"Invalid phone number {phone} was accepted"
        except ValidationError:
            pass  # Expected
    
    print("✓ Phone number validation works correctly")

def test_url_validator():
    """Test URL validation."""
    print("Testing URL validation...")
    
    validator = URLValidator()
    
    # Valid URLs
    valid_urls = ['https://example.com', 'http://localhost:8000']
    for url in valid_urls:
        try:
            validator(url)
        except ValidationError:
            assert False, f"Valid URL {url} was rejected"
    
    # Invalid URLs
    invalid_urls = ['javascript:alert("xss")', 'not-a-url']
    for url in invalid_urls:
        try:
            validator(url)
            assert False, f"Invalid URL {url} was accepted"
        except ValidationError:
            pass  # Expected
    
    print("✓ URL validation works correctly")

def test_salary_range_validation():
    """Test salary range validation."""
    print("Testing salary range validation...")
    
    # Valid ranges
    try:
        validate_salary_range(50000, 100000)
        validate_salary_range(None, 100000)
        validate_salary_range(50000, None)
    except ValidationError:
        assert False, "Valid salary range was rejected"
    
    # Invalid ranges
    try:
        validate_salary_range(100000, 50000)  # Min > Max
        assert False, "Invalid salary range was accepted"
    except ValidationError:
        pass  # Expected
    
    print("✓ Salary range validation works correctly")

def test_skills_validation():
    """Test skills list validation."""
    print("Testing skills list validation...")
    
    # Valid skills
    valid_skills = ['Python', 'JavaScript', 'React']
    try:
        validate_skills_list(valid_skills)
    except ValidationError:
        assert False, "Valid skills list was rejected"
    
    # Invalid skills - not a list
    try:
        validate_skills_list('not a list')
        assert False, "Invalid skills list was accepted"
    except ValidationError:
        pass  # Expected
    
    print("✓ Skills list validation works correctly")

def test_error_response_format():
    """Test error response formatting."""
    print("Testing error response formatting...")
    
    response = format_error_response(
        'TEST_ERROR',
        'Test message',
        {'field': ['Error detail']},
        400
    )
    
    assert response['error']['code'] == 'TEST_ERROR'
    assert response['error']['message'] == 'Test message'
    assert response['error']['details']['field'] == ['Error detail']
    assert 'timestamp' in response['error']
    
    print("✓ Error response formatting works correctly")

def main():
    """Run all tests."""
    print("Running validation utility tests...\n")
    
    try:
        test_sanitize_html()
        test_sanitize_text()
        test_phone_validator()
        test_url_validator()
        test_salary_range_validation()
        test_skills_validation()
        test_error_response_format()
        
        print("\n🎉 All validation tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())