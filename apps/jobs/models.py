from django.db import models
from django.core.validators import URLValidator
from django.utils.text import slugify


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
        # Return 0 until Job model is implemented and related
        try:
            return self.job_set.filter(is_active=True).count()
        except AttributeError:
            return 0
