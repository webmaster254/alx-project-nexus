from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.jobs.models import Job


class ApplicationStatus(models.Model):
    """
    Model for managing application status types.
    Defines the possible states an application can be in.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        unique=True,
        help_text="Status name (pending, reviewed, accepted, rejected, withdrawn)"
    )
    display_name = models.CharField(
        max_length=50,
        help_text="Human-readable status name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this status means"
    )
    is_final = models.BooleanField(
        default=False,
        help_text="Whether this status represents a final decision"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'application_status'
        verbose_name = 'Application Status'
        verbose_name_plural = 'Application Statuses'
        ordering = ['name']

    def __str__(self):
        return self.display_name

    @classmethod
    def get_default_status(cls):
        """Get the default status for new applications."""
        status, created = cls.objects.get_or_create(
            name='pending',
            defaults={
                'display_name': 'Pending Review',
                'description': 'Application has been submitted and is awaiting review',
                'is_final': False
            }
        )
        return status


class Application(models.Model):
    """
    Model linking users to jobs for job applications.
    Tracks application status and includes application-specific data.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="User who submitted the application"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="Job being applied for"
    )
    status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.PROTECT,
        related_name='applications',
        help_text="Current status of the application"
    )
    cover_letter = models.TextField(
        blank=True,
        help_text="Cover letter text submitted with the application"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the application (admin only)"
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the application was submitted"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the application was last updated"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the application was first reviewed"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
        help_text="Admin user who reviewed the application"
    )

    class Meta:
        db_table = 'application'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        unique_together = ['user', 'job']
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applied_at']),
            models.Index(fields=['status', 'applied_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.job.title} at {self.job.company.name}"

    def clean(self):
        """Validate application data before saving."""
        # Check if job is still accepting applications
        if not self.job.can_apply():
            raise ValidationError("This job is no longer accepting applications.")
        
        # Check if user is not applying to their own job posting
        if self.job.created_by == self.user:
            raise ValidationError("You cannot apply to your own job posting.")

    def save(self, *args, **kwargs):
        """Override save to set default status and run validation."""
        # Set default status for new applications
        if not self.status_id:
            self.status = ApplicationStatus.get_default_status()
        
        # Set reviewed_at timestamp when status changes from pending
        if self.pk:  # Existing application
            old_application = Application.objects.get(pk=self.pk)
            if (old_application.status.name == 'pending' and 
                self.status.name != 'pending' and 
                not self.reviewed_at):
                self.reviewed_at = timezone.now()
        
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this application."""
        return f"/applications/{self.pk}/"

    def can_withdraw(self):
        """Check if the application can be withdrawn by the user."""
        return self.status.name in ['pending', 'reviewed']

    def can_update_status(self):
        """Check if the application status can be updated."""
        return not self.status.is_final

    def withdraw(self):
        """Withdraw the application (user action)."""
        if not self.can_withdraw():
            raise ValidationError("This application cannot be withdrawn.")
        
        withdrawn_status, _ = ApplicationStatus.objects.get_or_create(
            name='withdrawn',
            defaults={
                'display_name': 'Withdrawn',
                'description': 'Application was withdrawn by the applicant',
                'is_final': True
            }
        )
        self.status = withdrawn_status
        self.save()

    def update_status(self, new_status, reviewed_by=None, notes=None):
        """Update application status (admin action)."""
        if not self.can_update_status():
            raise ValidationError("This application status cannot be updated.")
        
        self.status = new_status
        if reviewed_by:
            self.reviewed_by = reviewed_by
        if notes:
            self.notes = notes
        
        self.save()

    @property
    def days_since_applied(self):
        """Return the number of days since the application was submitted."""
        delta = timezone.now() - self.applied_at
        return delta.days

    @property
    def is_recent(self):
        """Check if the application was submitted within the last 7 days."""
        return self.days_since_applied <= 7


class Document(models.Model):
    """
    Model for storing documents associated with job applications.
    Handles resume uploads and cover letter attachments.
    """
    DOCUMENT_TYPES = [
        ('resume', 'Resume/CV'),
        ('cover_letter', 'Cover Letter'),
        ('portfolio', 'Portfolio'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Application this document belongs to"
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        help_text="Type of document"
    )
    title = models.CharField(
        max_length=200,
        help_text="Document title or name"
    )
    file = models.FileField(
        upload_to='application_documents/',
        help_text="Uploaded document file"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    content_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the uploaded file"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the document"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the document was uploaded"
    )

    class Meta:
        db_table = 'application_document'
        verbose_name = 'Application Document'
        verbose_name_plural = 'Application Documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['application', 'document_type']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()}) - {self.application}"

    def save(self, *args, **kwargs):
        """Override save to set file metadata."""
        if self.file:
            self.file_size = self.file.size
            # Set content type if available
            if hasattr(self.file.file, 'content_type'):
                self.content_type = self.file.file.content_type
        
        super().save(*args, **kwargs)

    def get_file_extension(self):
        """Get the file extension from the uploaded file."""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ''

    def get_file_size_display(self):
        """Return human-readable file size."""
        if not self.file_size:
            return "Unknown size"
        
        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def is_pdf(self):
        """Check if the document is a PDF file."""
        return self.get_file_extension() == 'pdf' or self.content_type == 'application/pdf'

    @property
    def is_image(self):
        """Check if the document is an image file."""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return (self.get_file_extension() in image_extensions or 
                self.content_type.startswith('image/'))

    @property
    def is_document(self):
        """Check if the document is a text document."""
        doc_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf']
        doc_types = ['application/pdf', 'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain', 'application/rtf']
        return (self.get_file_extension() in doc_extensions or 
                self.content_type in doc_types)
