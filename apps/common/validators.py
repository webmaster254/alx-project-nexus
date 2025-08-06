"""
Custom validators for input sanitization and validation.
"""
import re
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from rest_framework import serializers


# Allowed HTML tags and attributes for rich text fields
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'a', 'img'
]

ALLOWED_HTML_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'width', 'height'],
    '*': ['class']
}


def sanitize_html(value):
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        value (str): HTML content to sanitize
    
    Returns:
        str: Sanitized HTML content
    """
    if not value:
        return value
    
    # First pass: remove script tags and their content
    import re
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Second pass: use bleach to clean remaining HTML
    return bleach.clean(
        value,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        strip=True
    )


def sanitize_text(value):
    """
    Sanitize plain text input by removing potentially harmful characters.
    
    Args:
        value (str): Text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not value:
        return value
    
    # Remove null bytes and other control characters
    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    return value


@deconstructible
class PhoneNumberValidator:
    """
    Validator for phone numbers with international format support.
    """
    message = 'Enter a valid phone number (e.g., +1234567890 or (123) 456-7890).'
    code = 'invalid_phone'
    
    def __call__(self, value):
        if not value:
            return
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', value)
        
        # Check if it's a valid international format
        if not re.match(r'^\+?[1-9]\d{6,14}$', cleaned):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class URLValidator:
    """
    Enhanced URL validator with additional security checks.
    """
    message = 'Enter a valid URL.'
    code = 'invalid_url'
    
    def __call__(self, value):
        if not value:
            return
        
        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            raise ValidationError(self.message, code=self.code)
        
        # Check for potentially malicious URLs
        suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'file:',
            r'ftp:',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError(
                    'URL contains potentially unsafe protocol.',
                    code='unsafe_url'
                )


@deconstructible
class FileExtensionValidator:
    """
    Validator for file extensions with security checks.
    """
    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def __call__(self, value):
        if not value:
            return
        
        extension = value.name.split('.')[-1].lower() if '.' in value.name else ''
        
        if extension not in self.allowed_extensions:
            raise ValidationError(
                f'File extension "{extension}" is not allowed. '
                f'Allowed extensions: {", ".join(self.allowed_extensions)}',
                code='invalid_extension'
            )
        
        # Check for double extensions (e.g., file.php.jpg)
        if value.name.count('.') > 1:
            parts = value.name.split('.')
            for part in parts[1:-1]:  # Check all extensions except the last one
                if part.lower() in ['php', 'jsp', 'asp', 'aspx', 'exe', 'bat', 'cmd', 'sh']:
                    raise ValidationError(
                        'File contains potentially dangerous extension.',
                        code='dangerous_extension'
                    )


@deconstructible
class FileSizeValidator:
    """
    Validator for file size limits.
    """
    def __init__(self, max_size_mb):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_size_mb = max_size_mb
    
    def __call__(self, value):
        if not value:
            return
        
        if value.size > self.max_size_bytes:
            raise ValidationError(
                f'File size exceeds maximum allowed size of {self.max_size_mb}MB.',
                code='file_too_large'
            )


@deconstructible
class SalaryRangeValidator:
    """
    Validator for salary range fields.
    """
    def __init__(self, min_salary=0, max_salary=10000000):
        self.min_salary = min_salary
        self.max_salary = max_salary
    
    def __call__(self, value):
        if value is None:
            return
        
        if value < self.min_salary:
            raise ValidationError(
                f'Salary cannot be less than ${self.min_salary:,}.',
                code='salary_too_low'
            )
        
        if value > self.max_salary:
            raise ValidationError(
                f'Salary cannot exceed ${self.max_salary:,}.',
                code='salary_too_high'
            )


@deconstructible
class NoScriptValidator:
    """
    Validator to prevent script injection in text fields.
    """
    message = 'Text contains potentially harmful script content.'
    code = 'script_detected'
    
    def __call__(self, value):
        if not value:
            return
        
        # Check for script tags and javascript
        script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                raise ValidationError(self.message, code=self.code)


# Common regex validators
phone_validator = PhoneNumberValidator()
url_validator = URLValidator()
no_script_validator = NoScriptValidator()

# File validators
resume_file_validator = FileExtensionValidator(['pdf', 'doc', 'docx'])
image_file_validator = FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])
document_size_validator = FileSizeValidator(5)  # 5MB limit
image_size_validator = FileSizeValidator(2)  # 2MB limit

# Salary validators
salary_validator = SalaryRangeValidator()

# Username validator (alphanumeric, underscore, hyphen)
username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_-]+$',
    message='Username can only contain letters, numbers, underscores, and hyphens.',
    code='invalid_username'
)


class SanitizedCharField(serializers.CharField):
    """
    CharField that automatically sanitizes input text.
    """
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return sanitize_text(value)


class SanitizedTextField(serializers.CharField):
    """
    TextField that allows HTML but sanitizes it.
    """
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return sanitize_html(value)


class ValidatedEmailField(serializers.EmailField):
    """
    EmailField with additional validation and sanitization.
    """
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        # Convert to lowercase for consistency
        return value.lower().strip()


class ValidatedURLField(serializers.URLField):
    """
    URLField with enhanced security validation.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(url_validator)
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.strip()


def validate_salary_range(min_salary, max_salary):
    """
    Validate that salary range is logical.
    
    Args:
        min_salary: Minimum salary value
        max_salary: Maximum salary value
    
    Raises:
        ValidationError: If salary range is invalid
    """
    if min_salary is not None and max_salary is not None:
        if min_salary > max_salary:
            raise ValidationError(
                'Minimum salary cannot be greater than maximum salary.',
                code='invalid_salary_range'
            )
        
        if max_salary - min_salary < 1000:
            raise ValidationError(
                'Salary range should be at least $1,000.',
                code='salary_range_too_small'
            )


def validate_skills_list(skills):
    """
    Validate a list of skills.
    
    Args:
        skills (list): List of skill strings
    
    Raises:
        ValidationError: If skills list is invalid
    """
    if not isinstance(skills, list):
        raise ValidationError('Skills must be provided as a list.')
    
    if len(skills) > 20:
        raise ValidationError('Maximum 20 skills allowed.')
    
    for skill in skills:
        if not isinstance(skill, str):
            raise ValidationError('Each skill must be a string.')
        
        skill = skill.strip()
        if len(skill) < 2:
            raise ValidationError('Each skill must be at least 2 characters long.')
        
        if len(skill) > 50:
            raise ValidationError('Each skill must be no more than 50 characters long.')
        
        # Check for potentially harmful content
        no_script_validator(skill)