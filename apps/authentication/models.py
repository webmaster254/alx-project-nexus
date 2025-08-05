from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with email as username.
    Includes admin role tracking and timestamp fields.
    """
    email = models.EmailField(unique=True, help_text="Email address used for authentication")
    is_admin = models.BooleanField(
        default=False, 
        help_text="Designates whether the user has admin privileges"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    @property
    def is_job_seeker(self):
        """Check if user is a regular job seeker (not admin)."""
        return not self.is_admin


class UserProfile(models.Model):
    """
    Extended user profile model for additional user data storage.
    Contains professional information and contact details.
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        help_text="Associated user account"
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Contact phone number"
    )
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Brief professional biography"
    )
    location = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Current location (city, state/country)"
    )
    website = models.URLField(
        blank=True,
        help_text="Personal or professional website URL"
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        help_text="Upload resume file (PDF preferred)"
    )
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of skills"
    )
    experience_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Years of professional experience"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.email} - Profile"

    def get_skills_list(self):
        """Return skills as a list."""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
        return []

    def set_skills_list(self, skills_list):
        """Set skills from a list."""
        self.skills = ', '.join(skills_list) if skills_list else ''