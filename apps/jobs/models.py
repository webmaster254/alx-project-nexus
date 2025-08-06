from django.db import models
from django.core.validators import URLValidator, MinValueValidator
from django.utils.text import slugify
from django.conf import settings
from apps.categories.models import Industry, JobType, Category


class Company(models.Model):
    """
    Company model for storing employer information.
    Contains company details and contact information.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Company name"
    )
    description = models.TextField(
        blank=True,
        help_text="Company description and overview"
    )
    website = models.URLField(
        blank=True,
        validators=[URLValidator()],
        help_text="Company website URL"
    )
    email = models.EmailField(
        blank=True,
        help_text="Company contact email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Company contact phone number"
    )
    address = models.TextField(
        blank=True,
        help_text="Company address"
    )
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Company logo image"
    )
    founded_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year the company was founded"
    )
    employee_count = models.CharField(
        max_length=50,
        blank=True,
        help_text="Number of employees (e.g., '1-10', '50-100', '500+')"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="URL-friendly version of company name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the company is active and can post jobs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from company name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this company."""
        return f"/companies/{self.slug}/"

    @property
    def job_count(self):
        """Return the number of active jobs for this company."""
        return self.jobs.filter(is_active=True).count()


class Job(models.Model):
    """
    Comprehensive Job model for job postings.
    Contains all job details, relationships, and metadata.
    """
    SALARY_TYPES = [
        ('hourly', 'Hourly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]

    # Basic job information
    title = models.CharField(
        max_length=200,
        help_text="Job title (e.g., Senior Software Engineer)"
    )
    description = models.TextField(
        help_text="Detailed job description including responsibilities and requirements"
    )
    summary = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief job summary for listings"
    )
    
    # Company and location
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Company posting this job"
    )
    location = models.CharField(
        max_length=200,
        help_text="Job location (city, state/country or 'Remote')"
    )
    is_remote = models.BooleanField(
        default=False,
        help_text="Whether this is a remote position"
    )
    
    # Salary information
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum salary amount"
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum salary amount"
    )
    salary_type = models.CharField(
        max_length=10,
        choices=SALARY_TYPES,
        default='yearly',
        help_text="Type of salary (hourly, monthly, yearly)"
    )
    salary_currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency code (e.g., USD, EUR, GBP)"
    )
    
    # Job classification
    job_type = models.ForeignKey(
        JobType,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Type of employment (full-time, part-time, etc.)"
    )
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Industry classification"
    )
    categories = models.ManyToManyField(
        Category,
        related_name='jobs',
        blank=True,
        help_text="Job categories for classification"
    )
    
    # Experience and skills
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default='mid',
        help_text="Required experience level"
    )
    required_skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of required skills"
    )
    preferred_skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of preferred skills"
    )
    
    # Application details
    application_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Deadline for job applications"
    )
    external_url = models.URLField(
        blank=True,
        help_text="External URL for job application (if not handled internally)"
    )
    
    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this job is active and accepting applications"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this job should be featured in listings"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this job has been viewed"
    )
    applications_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of applications received for this job"
    )
    
    # User and timestamp tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_jobs',
        help_text="User who created this job posting"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updated_jobs',
        null=True,
        blank=True,
        help_text="User who last updated this job posting"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['location']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['industry', 'job_type']),
            models.Index(fields=['location', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def clean(self):
        """Validate job data before saving."""
        from django.core.exceptions import ValidationError
        
        # Validate salary range
        if self.salary_min and self.salary_max:
            if self.salary_min > self.salary_max:
                raise ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        # Validate application deadline
        if self.application_deadline:
            from django.utils import timezone
            if self.application_deadline <= timezone.now():
                raise ValidationError("Application deadline must be in the future.")

    def save(self, *args, **kwargs):
        """Override save to run validation and update metadata."""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this job."""
        return f"/jobs/{self.pk}/"

    def get_salary_display(self):
        """Return formatted salary range display."""
        if not self.salary_min and not self.salary_max:
            return "Salary not specified"
        
        currency_symbol = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
        }.get(self.salary_currency, self.salary_currency)
        
        if self.salary_min and self.salary_max:
            return f"{currency_symbol}{self.salary_min:,.0f} - {currency_symbol}{self.salary_max:,.0f} {self.get_salary_type_display().lower()}"
        elif self.salary_min:
            return f"From {currency_symbol}{self.salary_min:,.0f} {self.get_salary_type_display().lower()}"
        elif self.salary_max:
            return f"Up to {currency_symbol}{self.salary_max:,.0f} {self.get_salary_type_display().lower()}"

    def get_required_skills_list(self):
        """Return required skills as a list."""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
        return []

    def get_preferred_skills_list(self):
        """Return preferred skills as a list."""
        if self.preferred_skills:
            return [skill.strip() for skill in self.preferred_skills.split(',') if skill.strip()]
        return []

    def set_required_skills_list(self, skills_list):
        """Set required skills from a list."""
        self.required_skills = ', '.join(skills_list) if skills_list else ''

    def set_preferred_skills_list(self, skills_list):
        """Set preferred skills from a list."""
        self.preferred_skills = ', '.join(skills_list) if skills_list else ''

    def increment_views(self):
        """Increment the views count for this job."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_applications(self):
        """Increment the applications count for this job."""
        self.applications_count += 1
        self.save(update_fields=['applications_count'])

    def is_application_deadline_passed(self):
        """Check if the application deadline has passed."""
        if not self.application_deadline:
            return False
        from django.utils import timezone
        return self.application_deadline <= timezone.now()

    def can_apply(self):
        """Check if applications are still being accepted for this job."""
        return (
            self.is_active and 
            not self.is_application_deadline_passed()
        )

    @property
    def category_names(self):
        """Return a list of category names for this job."""
        return [category.name for category in self.categories.all()]

    @property
    def days_since_posted(self):
        """Return the number of days since this job was posted."""
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.days

    @property
    def is_new(self):
        """Check if this job was posted within the last 7 days."""
        return self.days_since_posted <= 7

    @property
    def is_urgent(self):
        """Check if this job has an application deadline within 7 days."""
        if not self.application_deadline:
            return False
        from django.utils import timezone
        days_until_deadline = (self.application_deadline - timezone.now()).days
        return 0 <= days_until_deadline <= 7