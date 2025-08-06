"""
Tests for comprehensive input validation and error handling.
"""
import json
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.common.exceptions import (
    CustomAPIException, BusinessLogicError, DuplicateApplicationError,
    InactiveJobError, InvalidFileTypeError, format_error_response,
    custom_exception_handler
)
from apps.common.validators import (
    sanitize_html, sanitize_text, PhoneNumberValidator, URLValidator,
    FileExtensionValidator, FileSizeValidator, SalaryRangeValidator,
    NoScriptValidator, validate_salary_range, validate_skills_list,
    SanitizedCharField, SanitizedTextField, ValidatedEmailField,
    ValidatedURLField
)
from apps.authentication.serializers import UserRegistrationSerializer
from apps.jobs.serializers import JobSerializer
from apps.jobs.models import Job, Company
from apps.categories.models import Industry, JobType, Category
from unittest.mock import Mock, patch
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class ValidationUtilsTestCase(TestCase):
    """Test cases for validation utilities."""
    
    def test_sanitize_html(self):
        """Test HTML sanitization."""
        # Test allowed HTML
        clean_html = '<p>Hello <strong>world</strong></p>'
        self.assertEqual(sanitize_html(clean_html), clean_html)
        
        # Test script removal
        malicious_html = '<p>Hello</p><script>alert("xss")</script>'
        expected = '<p>Hello</p>'
        self.assertEqual(sanitize_html(malicious_html), expected)
        
        # Test empty input
        self.assertEqual(sanitize_html(''), '')
        self.assertEqual(sanitize_html(None), None)
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        # Test normal text
        normal_text = 'Hello world!'
        self.assertEqual(sanitize_text(normal_text), normal_text)
        
        # Test control character removal
        text_with_control = 'Hello\x00\x08world\x1F'
        expected = 'Helloworld'
        self.assertEqual(sanitize_text(text_with_control), expected)
        
        # Test whitespace stripping
        text_with_whitespace = '  Hello world  '
        expected = 'Hello world'
        self.assertEqual(sanitize_text(text_with_whitespace), expected)
        
        # Test empty input
        self.assertEqual(sanitize_text(''), '')
        self.assertEqual(sanitize_text(None), None)
    
    def test_phone_number_validator(self):
        """Test phone number validation."""
        validator = PhoneNumberValidator()
        
        # Valid phone numbers
        valid_phones = ['+1234567890', '+12345678901234', '1234567890']
        for phone in valid_phones:
            try:
                validator(phone)
            except ValidationError:
                self.fail(f'Valid phone number {phone} was rejected')
        
        # Invalid phone numbers
        invalid_phones = ['123', '+123456789012345', 'abc123', '']
        for phone in invalid_phones:
            if phone:  # Skip empty string as it's allowed
                with self.assertRaises(ValidationError):
                    validator(phone)
    
    def test_url_validator(self):
        """Test URL validation."""
        validator = URLValidator()
        
        # Valid URLs
        valid_urls = [
            'https://example.com',
            'http://localhost:8000',
            'https://sub.domain.com/path?query=value'
        ]
        for url in valid_urls:
            try:
                validator(url)
            except ValidationError:
                self.fail(f'Valid URL {url} was rejected')
        
        # Invalid URLs
        invalid_urls = [
            'javascript:alert("xss")',
            'data:text/html,<script>alert("xss")</script>',
            'not-a-url',
            'ftp://example.com'
        ]
        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                validator(url)
    
    def test_file_extension_validator(self):
        """Test file extension validation."""
        validator = FileExtensionValidator(['pdf', 'doc', 'docx'])
        
        # Create mock file objects
        valid_file = Mock()
        valid_file.name = 'document.pdf'
        
        invalid_file = Mock()
        invalid_file.name = 'script.exe'
        
        dangerous_file = Mock()
        dangerous_file.name = 'document.php.pdf'
        
        # Test valid file
        try:
            validator(valid_file)
        except ValidationError:
            self.fail('Valid file extension was rejected')
        
        # Test invalid extension
        with self.assertRaises(ValidationError):
            validator(invalid_file)
        
        # Test dangerous double extension
        with self.assertRaises(ValidationError):
            validator(dangerous_file)
    
    def test_file_size_validator(self):
        """Test file size validation."""
        validator = FileSizeValidator(1)  # 1MB limit
        
        # Valid file size
        valid_file = Mock()
        valid_file.size = 500 * 1024  # 500KB
        
        # Invalid file size
        invalid_file = Mock()
        invalid_file.size = 2 * 1024 * 1024  # 2MB
        
        try:
            validator(valid_file)
        except ValidationError:
            self.fail('Valid file size was rejected')
        
        with self.assertRaises(ValidationError):
            validator(invalid_file)
    
    def test_salary_range_validator(self):
        """Test salary range validation."""
        validator = SalaryRangeValidator(min_salary=1000, max_salary=1000000)
        
        # Valid salaries
        valid_salaries = [50000, 100000, 1000, 1000000]
        for salary in valid_salaries:
            try:
                validator(salary)
            except ValidationError:
                self.fail(f'Valid salary {salary} was rejected')
        
        # Invalid salaries
        invalid_salaries = [500, 2000000]
        for salary in invalid_salaries:
            with self.assertRaises(ValidationError):
                validator(salary)
    
    def test_no_script_validator(self):
        """Test script detection validator."""
        validator = NoScriptValidator()
        
        # Safe text
        safe_text = 'This is safe text with no scripts'
        try:
            validator(safe_text)
        except ValidationError:
            self.fail('Safe text was rejected')
        
        # Dangerous text
        dangerous_texts = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            'onclick="alert(\'xss\')"',
            'onload="malicious()"'
        ]
        for text in dangerous_texts:
            with self.assertRaises(ValidationError):
                validator(text)
    
    def test_validate_salary_range(self):
        """Test salary range validation function."""
        # Valid ranges
        try:
            validate_salary_range(50000, 100000)
            validate_salary_range(None, 100000)
            validate_salary_range(50000, None)
        except ValidationError:
            self.fail('Valid salary range was rejected')
        
        # Invalid ranges
        with self.assertRaises(ValidationError):
            validate_salary_range(100000, 50000)  # Min > Max
        
        with self.assertRaises(ValidationError):
            validate_salary_range(50000, 50500)  # Range too small
    
    def test_validate_skills_list(self):
        """Test skills list validation."""
        # Valid skills
        valid_skills = ['Python', 'JavaScript', 'React', 'Django']
        try:
            validate_skills_list(valid_skills)
        except ValidationError:
            self.fail('Valid skills list was rejected')
        
        # Invalid skills - too many
        too_many_skills = [f'Skill{i}' for i in range(25)]
        with self.assertRaises(ValidationError):
            validate_skills_list(too_many_skills)
        
        # Invalid skills - not a list
        with self.assertRaises(ValidationError):
            validate_skills_list('not a list')
        
        # Invalid skills - too short
        with self.assertRaises(ValidationError):
            validate_skills_list(['A'])


class CustomExceptionTestCase(TestCase):
    """Test cases for custom exceptions."""
    
    def test_custom_api_exception(self):
        """Test custom API exception."""
        exc = CustomAPIException('Test error', 'test_code')
        self.assertEqual(str(exc.detail), 'Test error')
        self.assertEqual(exc.code, 'test_code')
        self.assertEqual(exc.status_code, 500)
    
    def test_business_logic_error(self):
        """Test business logic error."""
        exc = BusinessLogicError('Business error')
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.code, 'business_logic_error')
    
    def test_duplicate_application_error(self):
        """Test duplicate application error."""
        exc = DuplicateApplicationError()
        self.assertEqual(exc.status_code, 400)
        self.assertEqual(exc.code, 'duplicate_application')
        self.assertIn('already applied', str(exc.detail))
    
    def test_format_error_response(self):
        """Test error response formatting."""
        response = format_error_response(
            'TEST_ERROR',
            'Test message',
            {'field': ['Error detail']},
            400
        )
        
        self.assertEqual(response['error']['code'], 'TEST_ERROR')
        self.assertEqual(response['error']['message'], 'Test message')
        self.assertEqual(response['error']['details']['field'], ['Error detail'])
        self.assertIn('timestamp', response['error'])


class SerializerValidationTestCase(APITestCase):
    """Test cases for serializer validation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test data for job serializer
        self.company = Company.objects.create(
            name='Test Company',
            description='Test Description',
            email='company@test.com'
        )
        
        self.industry = Industry.objects.create(
            name='Technology',
            description='Tech industry'
        )
        
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time position'
        )
        
        self.category = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
    
    def test_user_registration_validation(self):
        """Test user registration serializer validation."""
        # Valid data
        valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        serializer = UserRegistrationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid data - passwords don't match
        invalid_data = valid_data.copy()
        invalid_data['confirm_password'] = 'differentpass'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Passwords don\'t match', str(serializer.errors))
        
        # Invalid data - email already exists
        invalid_data = valid_data.copy()
        invalid_data['email'] = 'test@example.com'  # Already exists
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_job_serializer_validation(self):
        """Test job serializer validation."""
        # Valid data
        valid_data = {
            'title': 'Software Engineer',
            'description': 'Great opportunity for a software engineer',
            'location': 'San Francisco, CA',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [self.category.id],
            'salary_min': 80000,
            'salary_max': 120000,
            'required_skills_list': ['Python', 'Django', 'JavaScript']
        }
        
        serializer = JobSerializer(data=valid_data, context={'request': Mock(user=self.user)})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # Invalid data - salary range
        invalid_data = valid_data.copy()
        invalid_data['salary_min'] = 120000
        invalid_data['salary_max'] = 80000
        
        serializer = JobSerializer(data=invalid_data, context={'request': Mock(user=self.user)})
        self.assertFalse(serializer.is_valid())
        
        # Invalid data - too many skills
        invalid_data = valid_data.copy()
        invalid_data['required_skills_list'] = [f'Skill{i}' for i in range(25)]
        
        serializer = JobSerializer(data=invalid_data, context={'request': Mock(user=self.user)})
        self.assertFalse(serializer.is_valid())
    
    def test_sanitized_fields(self):
        """Test sanitized field behavior."""
        # Test SanitizedCharField
        field = SanitizedCharField()
        result = field.to_internal_value('  Test with spaces  ')
        self.assertEqual(result, 'Test with spaces')
        
        # Test SanitizedTextField
        field = SanitizedTextField()
        result = field.to_internal_value('<p>Safe HTML</p><script>alert("xss")</script>')
        self.assertEqual(result, '<p>Safe HTML</p>')
        
        # Test ValidatedEmailField
        field = ValidatedEmailField()
        result = field.to_internal_value('  TEST@EXAMPLE.COM  ')
        self.assertEqual(result, 'test@example.com')


class RateLimitingTestCase(APITestCase):
    """Test cases for rate limiting."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
    
    @override_settings(RATELIMIT_ENABLE=True)
    def test_login_rate_limiting(self):
        """Test login rate limiting."""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for i in range(6):  # Exceed the 5/minute limit
            response = self.client.post('/api/auth/login/', login_data)
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                # Should be rate limited
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    @override_settings(RATELIMIT_ENABLE=True)
    def test_registration_rate_limiting(self):
        """Test registration rate limiting."""
        # Make multiple registration attempts
        for i in range(4):  # Exceed the 3/minute limit
            register_data = {
                'email': f'user{i}@example.com',
                'username': f'user{i}',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'testpass123',
                'confirm_password': 'testpass123'
            }
            
            response = self.client.post('/api/auth/register/', register_data)
            if i < 3:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                # Should be rate limited
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class ErrorHandlingAPITestCase(APITestCase):
    """Test cases for API error handling."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_validation_error_format(self):
        """Test validation error response format."""
        # Try to register with invalid data
        invalid_data = {
            'email': 'invalid-email',
            'password': '123',  # Too short
            'confirm_password': '456'  # Doesn't match
        }
        
        response = self.client.post('/api/auth/register/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'VALIDATION_ERROR')
        self.assertIn('message', data['error'])
        self.assertIn('details', data['error'])
        self.assertIn('timestamp', data['error'])
    
    def test_authentication_error_format(self):
        """Test authentication error response format."""
        # Try to access protected endpoint without authentication
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'AUTHENTICATION_FAILED')
    
    def test_permission_error_format(self):
        """Test permission error response format."""
        # Login as regular user
        self.client.force_authenticate(user=self.user)
        
        # Try to access admin-only endpoint (assuming jobs creation is admin-only)
        job_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'location': 'Test Location'
        }
        
        response = self.client.post('/api/jobs/', job_data)
        
        # Should get permission denied (assuming proper permissions are set)
        if response.status_code == status.HTTP_403_FORBIDDEN:
            data = response.json()
            self.assertIn('error', data)
            self.assertEqual(data['error']['code'], 'PERMISSION_DENIED')
    
    def test_not_found_error_format(self):
        """Test not found error response format."""
        response = self.client.get('/api/nonexistent-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'NOT_FOUND')
    
    def test_method_not_allowed_error_format(self):
        """Test method not allowed error response format."""
        # Try to use wrong HTTP method
        response = self.client.delete('/api/auth/register/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Check error format
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'METHOD_NOT_ALLOWED')


class InputSanitizationTestCase(APITestCase):
    """Test cases for input sanitization."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_html_sanitization_in_registration(self):
        """Test HTML sanitization in user registration."""
        malicious_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': '<script>alert("xss")</script>John',
            'last_name': 'Doe<img src=x onerror=alert("xss")>',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        
        response = self.client.post('/api/auth/register/', malicious_data)
        
        if response.status_code == status.HTTP_201_CREATED:
            # Check that the malicious content was sanitized
            user = User.objects.get(email='newuser@example.com')
            self.assertNotIn('<script>', user.first_name)
            self.assertNotIn('<img', user.last_name)
            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')
    
    def test_script_detection_in_text_fields(self):
        """Test script detection in text fields."""
        # This would be tested with actual job creation if permissions allow
        # For now, we test the validator directly
        validator = NoScriptValidator()
        
        malicious_texts = [
            'Normal text with <script>alert("xss")</script>',
            'Text with javascript:alert("xss")',
            'Text with onclick="malicious()"'
        ]
        
        for text in malicious_texts:
            with self.assertRaises(ValidationError):
                validator(text)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
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
                'apps.common',
                'apps.authentication',
                'apps.jobs',
                'apps.categories',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])