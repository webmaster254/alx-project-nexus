"""
Unit tests for common validators.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from apps.common.validators import (
    sanitize_html, sanitize_text, PhoneNumberValidator, URLValidator,
    FileExtensionValidator, FileSizeValidator, SalaryRangeValidator,
    NoScriptValidator, phone_validator, url_validator, no_script_validator,
    SanitizedCharField, SanitizedTextField, ValidatedEmailField,
    ValidatedURLField, validate_salary_range, validate_skills_list
)


class SanitizeHtmlTest(TestCase):
    """Test cases for sanitize_html function."""
    
    def test_sanitize_allowed_tags(self):
        """Test that allowed HTML tags are preserved."""
        html = '<p>This is a <strong>test</strong> with <em>emphasis</em>.</p>'
        result = sanitize_html(html)
        self.assertEqual(result, html)
    
    def test_sanitize_script_tags(self):
        """Test that script tags are removed."""
        html = '<p>Safe content</p><script>alert("xss")</script><p>More content</p>'
        result = sanitize_html(html)
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert("xss")', result)
        self.assertIn('<p>Safe content</p>', result)
        self.assertIn('<p>More content</p>', result)
    
    def test_sanitize_dangerous_attributes(self):
        """Test that dangerous attributes are removed."""
        html = '<p onclick="alert(1)">Click me</p>'
        result = sanitize_html(html)
        self.assertNotIn('onclick', result)
        self.assertIn('<p>Click me</p>', result)
    
    def test_sanitize_allowed_attributes(self):
        """Test that allowed attributes are preserved."""
        html = '<a href="https://example.com" title="Example">Link</a>'
        result = sanitize_html(html)
        self.assertEqual(result, html)
    
    def test_sanitize_empty_input(self):
        """Test sanitize_html with empty input."""
        self.assertEqual(sanitize_html(''), '')
        self.assertEqual(sanitize_html(None), None)


class SanitizeTextTest(TestCase):
    """Test cases for sanitize_text function."""
    
    def test_sanitize_control_characters(self):
        """Test that control characters are removed."""
        text = 'Normal text\x00\x01\x02with control chars'
        result = sanitize_text(text)
        self.assertEqual(result, 'Normal textwith control chars')
    
    def test_sanitize_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        text = '  \t  Normal text  \n  '
        result = sanitize_text(text)
        self.assertEqual(result, 'Normal text')
    
    def test_sanitize_empty_input(self):
        """Test sanitize_text with empty input."""
        self.assertEqual(sanitize_text(''), '')
        self.assertEqual(sanitize_text(None), None)


class PhoneNumberValidatorTest(TestCase):
    """Test cases for PhoneNumberValidator."""
    
    def setUp(self):
        self.validator = PhoneNumberValidator()
    
    def test_valid_phone_numbers(self):
        """Test valid phone numbers."""
        valid_phones = [
            '+1234567890',
            '+12345678901234',
            '1234567890',
            '+447700900123'
        ]
        
        for phone in valid_phones:
            try:
                self.validator(phone)
            except ValidationError:
                self.fail(f"Valid phone number {phone} was rejected")
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers."""
        invalid_phones = [
            '123',  # Too short
            '12345678901234567890',  # Too long
            'abc123',  # Contains letters
            '+0123456789',  # Starts with 0 after country code
            ''  # Empty (but this should be handled by required validation)
        ]
        
        for phone in invalid_phones:
            if phone:  # Skip empty string
                with self.assertRaises(ValidationError):
                    self.validator(phone)
    
    def test_empty_phone_number(self):
        """Test that empty phone number is allowed (for optional fields)."""
        try:
            self.validator('')
            self.validator(None)
        except ValidationError:
            self.fail("Empty phone number should be allowed")


class URLValidatorTest(TestCase):
    """Test cases for URLValidator."""
    
    def setUp(self):
        self.validator = URLValidator()
    
    def test_valid_urls(self):
        """Test valid URLs."""
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://subdomain.example.com',
            'https://example.com/path/to/page',
            'https://example.com:8080',
            'http://localhost:3000',
            'https://192.168.1.1'
        ]
        
        for url in valid_urls:
            try:
                self.validator(url)
            except ValidationError:
                self.fail(f"Valid URL {url} was rejected")
    
    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',
            'example.com',  # Missing protocol
            'https://',  # Incomplete
            'javascript:alert(1)',  # Dangerous protocol
            'data:text/html,<script>alert(1)</script>',  # Data URL
            'vbscript:msgbox(1)',  # VBScript
            'file:///etc/passwd'  # File protocol
        ]
        
        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                self.validator(url)
    
    def test_empty_url(self):
        """Test that empty URL is allowed (for optional fields)."""
        try:
            self.validator('')
            self.validator(None)
        except ValidationError:
            self.fail("Empty URL should be allowed")


class FileExtensionValidatorTest(TestCase):
    """Test cases for FileExtensionValidator."""
    
    def setUp(self):
        self.validator = FileExtensionValidator(['pdf', 'doc', 'docx'])
    
    def test_valid_extensions(self):
        """Test valid file extensions."""
        valid_files = [
            SimpleUploadedFile('resume.pdf', b'content'),
            SimpleUploadedFile('resume.doc', b'content'),
            SimpleUploadedFile('resume.docx', b'content'),
            SimpleUploadedFile('RESUME.PDF', b'content'),  # Case insensitive
        ]
        
        for file in valid_files:
            try:
                self.validator(file)
            except ValidationError:
                self.fail(f"Valid file {file.name} was rejected")
    
    def test_invalid_extensions(self):
        """Test invalid file extensions."""
        invalid_files = [
            SimpleUploadedFile('resume.txt', b'content'),
            SimpleUploadedFile('resume.jpg', b'content'),
            SimpleUploadedFile('resume', b'content'),  # No extension
        ]
        
        for file in invalid_files:
            with self.assertRaises(ValidationError):
                self.validator(file)
    
    def test_dangerous_double_extensions(self):
        """Test detection of dangerous double extensions."""
        dangerous_files = [
            SimpleUploadedFile('file.php.pdf', b'content'),
            SimpleUploadedFile('file.exe.doc', b'content'),
            SimpleUploadedFile('file.sh.docx', b'content'),
        ]
        
        for file in dangerous_files:
            with self.assertRaises(ValidationError):
                self.validator(file)


class FileSizeValidatorTest(TestCase):
    """Test cases for FileSizeValidator."""
    
    def setUp(self):
        self.validator = FileSizeValidator(1)  # 1MB limit
    
    def test_valid_file_size(self):
        """Test valid file sizes."""
        # 500KB file (under 1MB limit)
        small_file = SimpleUploadedFile('small.pdf', b'x' * (500 * 1024))
        
        try:
            self.validator(small_file)
        except ValidationError:
            self.fail("Valid file size was rejected")
    
    def test_invalid_file_size(self):
        """Test invalid file sizes."""
        # 2MB file (over 1MB limit)
        large_file = SimpleUploadedFile('large.pdf', b'x' * (2 * 1024 * 1024))
        
        with self.assertRaises(ValidationError):
            self.validator(large_file)
    
    def test_empty_file(self):
        """Test that empty file is allowed."""
        try:
            self.validator(None)
        except ValidationError:
            self.fail("Empty file should be allowed")


class SalaryRangeValidatorTest(TestCase):
    """Test cases for SalaryRangeValidator."""
    
    def setUp(self):
        self.validator = SalaryRangeValidator(min_salary=1000, max_salary=500000)
    
    def test_valid_salaries(self):
        """Test valid salary values."""
        valid_salaries = [50000, 100000, 1000, 500000]
        
        for salary in valid_salaries:
            try:
                self.validator(salary)
            except ValidationError:
                self.fail(f"Valid salary {salary} was rejected")
    
    def test_invalid_salaries(self):
        """Test invalid salary values."""
        # Too low
        with self.assertRaises(ValidationError):
            self.validator(500)
        
        # Too high
        with self.assertRaises(ValidationError):
            self.validator(1000000)
    
    def test_none_salary(self):
        """Test that None salary is allowed."""
        try:
            self.validator(None)
        except ValidationError:
            self.fail("None salary should be allowed")


class NoScriptValidatorTest(TestCase):
    """Test cases for NoScriptValidator."""
    
    def setUp(self):
        self.validator = NoScriptValidator()
    
    def test_safe_text(self):
        """Test safe text without scripts."""
        safe_texts = [
            'This is safe text',
            'HTML without scripts: <p>Hello</p>',
            'Some code: function test() { return true; }'
        ]
        
        for text in safe_texts:
            try:
                self.validator(text)
            except ValidationError:
                self.fail(f"Safe text was rejected: {text}")
    
    def test_dangerous_text(self):
        """Test text with dangerous script content."""
        dangerous_texts = [
            '<script>alert(1)</script>',
            'javascript:alert(1)',
            'vbscript:msgbox(1)',
            '<div onload="alert(1)">',
            '<img onerror="alert(1)" src="x">',
            '<a onclick="alert(1)">Click</a>',
            '<div onmouseover="alert(1)">Hover</div>'
        ]
        
        for text in dangerous_texts:
            with self.assertRaises(ValidationError):
                self.validator(text)


class SanitizedCharFieldTest(TestCase):
    """Test cases for SanitizedCharField."""
    
    def test_sanitization(self):
        """Test that input is sanitized."""
        field = SanitizedCharField()
        
        # Test control character removal
        result = field.to_internal_value('Text\x00with\x01control')
        self.assertEqual(result, 'Textwithcontrol')
        
        # Test whitespace stripping
        result = field.to_internal_value('  Text with spaces  ')
        self.assertEqual(result, 'Text with spaces')


class SanitizedTextFieldTest(TestCase):
    """Test cases for SanitizedTextField."""
    
    def test_html_sanitization(self):
        """Test that HTML is sanitized."""
        field = SanitizedTextField()
        
        # Test allowed HTML preservation
        result = field.to_internal_value('<p>Safe <strong>HTML</strong></p>')
        self.assertEqual(result, '<p>Safe <strong>HTML</strong></p>')
        
        # Test script removal
        result = field.to_internal_value('<p>Safe</p><script>alert(1)</script>')
        self.assertNotIn('<script>', result)
        self.assertIn('<p>Safe</p>', result)


class ValidatedEmailFieldTest(TestCase):
    """Test cases for ValidatedEmailField."""
    
    def test_email_normalization(self):
        """Test that email is normalized to lowercase."""
        field = ValidatedEmailField()
        
        result = field.to_internal_value('TEST@EXAMPLE.COM')
        self.assertEqual(result, 'test@example.com')
        
        result = field.to_internal_value('  test@example.com  ')
        self.assertEqual(result, 'test@example.com')


class ValidatedURLFieldTest(TestCase):
    """Test cases for ValidatedURLField."""
    
    def test_url_validation(self):
        """Test URL validation."""
        field = ValidatedURLField()
        
        # Valid URL
        result = field.to_internal_value('https://example.com')
        self.assertEqual(result, 'https://example.com')
        
        # URL with whitespace
        result = field.to_internal_value('  https://example.com  ')
        self.assertEqual(result, 'https://example.com')
        
        # Invalid URL
        with self.assertRaises(serializers.ValidationError):
            field.to_internal_value('not-a-url')


class ValidateSalaryRangeTest(TestCase):
    """Test cases for validate_salary_range function."""
    
    def test_valid_salary_ranges(self):
        """Test valid salary ranges."""
        # Valid range
        try:
            validate_salary_range(50000, 80000)
        except ValidationError:
            self.fail("Valid salary range was rejected")
        
        # Only min
        try:
            validate_salary_range(50000, None)
        except ValidationError:
            self.fail("Valid salary range with only min was rejected")
        
        # Only max
        try:
            validate_salary_range(None, 80000)
        except ValidationError:
            self.fail("Valid salary range with only max was rejected")
    
    def test_invalid_salary_ranges(self):
        """Test invalid salary ranges."""
        # Min > Max
        with self.assertRaises(ValidationError):
            validate_salary_range(80000, 50000)
        
        # Range too small
        with self.assertRaises(ValidationError):
            validate_salary_range(50000, 50500)  # Only $500 difference


class ValidateSkillsListTest(TestCase):
    """Test cases for validate_skills_list function."""
    
    def test_valid_skills_list(self):
        """Test valid skills lists."""
        valid_skills = [
            ['Python', 'JavaScript', 'React'],
            ['Java'],
            ['Skill with spaces', 'Another-skill']
        ]
        
        for skills in valid_skills:
            try:
                validate_skills_list(skills)
            except ValidationError:
                self.fail(f"Valid skills list was rejected: {skills}")
    
    def test_invalid_skills_list(self):
        """Test invalid skills lists."""
        # Not a list
        with self.assertRaises(ValidationError):
            validate_skills_list("not a list")
        
        # Too many skills
        with self.assertRaises(ValidationError):
            validate_skills_list(['Skill'] * 25)
        
        # Skill too short
        with self.assertRaises(ValidationError):
            validate_skills_list(['A'])
        
        # Skill too long
        with self.assertRaises(ValidationError):
            validate_skills_list(['x' * 51])
        
        # Non-string skill
        with self.assertRaises(ValidationError):
            validate_skills_list([123, 'Python'])
        
        # Script in skill
        with self.assertRaises(ValidationError):
            validate_skills_list(['<script>alert(1)</script>'])


class CommonValidatorsIntegrationTest(TestCase):
    """Integration tests for common validators."""
    
    def test_phone_validator_instance(self):
        """Test phone_validator instance."""
        # Valid phone
        try:
            phone_validator('+1234567890')
        except ValidationError:
            self.fail("Valid phone was rejected by phone_validator")
        
        # Invalid phone
        with self.assertRaises(ValidationError):
            phone_validator('invalid')
    
    def test_url_validator_instance(self):
        """Test url_validator instance."""
        # Valid URL
        try:
            url_validator('https://example.com')
        except ValidationError:
            self.fail("Valid URL was rejected by url_validator")
        
        # Invalid URL
        with self.assertRaises(ValidationError):
            url_validator('javascript:alert(1)')
    
    def test_no_script_validator_instance(self):
        """Test no_script_validator instance."""
        # Safe text
        try:
            no_script_validator('Safe text')
        except ValidationError:
            self.fail("Safe text was rejected by no_script_validator")
        
        # Dangerous text
        with self.assertRaises(ValidationError):
            no_script_validator('<script>alert(1)</script>')