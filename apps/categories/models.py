from django.db import models
from django.utils.text import slugify


class Industry(models.Model):
    """
    Industry model for job industry classification.
    Used to categorize jobs by industry sector.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Industry name (e.g., Technology, Healthcare, Finance)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the industry sector"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of industry name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this industry is active for job classification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'industry'
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from industry name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def job_count(self):
        """Return the number of active jobs in this industry."""
        return self.job_set.filter(is_active=True).count()


class JobType(models.Model):
    """
    JobType model for employment type classification.
    Defines different types of employment arrangements.
    """
    EMPLOYMENT_TYPES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Job type name (e.g., Full-time, Part-time, Contract)"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        choices=EMPLOYMENT_TYPES,
        help_text="Standardized code for the job type"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the employment type"
    )
    slug = models.SlugField(
        max_length=70,
        unique=True,
        blank=True,
        help_text="URL-friendly version of job type name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this job type is active for job classification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_type'
        verbose_name = 'Job Type'
        verbose_name_plural = 'Job Types'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from job type name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def job_count(self):
        """Return the number of active jobs of this type."""
        return self.job_set.filter(is_active=True).count()
