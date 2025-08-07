"""
Unit tests for applications models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta

from apps.applications.models import ApplicationStatus, Application, Document
from tests.base import BaseModelTestCase
from tests.factories import (
    ApplicationStatusFactory, ApplicationFactory, DocumentFactory,
    UserFactory, JobFactory, AdminUserFactory
)


class ApplicationStatusModelTest(BaseModelTestCase):
    """Test cases for ApplicationStatus model."""
    
    def test_application_status_creation(self):
        """Test basic application status creation."""
        status = ApplicationStatusFactory()
        self.assertIsInstance(status, ApplicationStatus)
        self.assertIsNotNone(status.created_at)
        self.assertIsNotNone(status.updated_at)
    
    def test_application_status_str_representation(self):
        """Test application status string representation."""
        status = ApplicationStatusFactory(display_name='Pending Review')
        self.assertEqual(str(status), 'Pending Review')
    
    def test_status_name_uniqueness(self):
        """Test that status name must be unique."""
        name = 'pending'
        ApplicationStatusFactory(name=name)
        
        with self.assertRaises(IntegrityError):
            ApplicationStatusFactory(name=name)
    
    def test_status_choices_validation(self):
        """Test status choices validation."""
        valid_statuses = ['pending', 'reviewed', 'accepted', 'rejected', 'withdrawn']
        
        for status_name in valid_statuses:
            status = ApplicationStatusFactory.build(name=status_name)
            self.assertModelValid(status)
    
    def test_get_default_status(self):
        """Test get_default_status class method."""
        # Should create pending status if it doesn't exist
        default_status = ApplicationStatus.get_default_status()
        self.assertEqual(default_status.name, 'pending')
        self.assertEqual(default_status.display_name, 'Pending Review')
        self.assertFalse(default_status.is_final)
        
        # Should return existing pending status if it exists
        existing_status = ApplicationStatus.get_default_status()
        self.assertEqual(default_status.id, existing_status.id)
    
    def test_is_final_field(self):
        """Test is_final field behavior."""
        # Non-final statuses
        pending = ApplicationStatusFactory(name='pending', is_final=False)
        reviewed = ApplicationStatusFactory(name='reviewed', is_final=False)
        
        self.assertFalse(pending.is_final)
        self.assertFalse(reviewed.is_final)
        
        # Final statuses
        accepted = ApplicationStatusFactory(name='accepted', is_final=True)
        rejected = ApplicationStatusFactory(name='rejected', is_final=True)
        withdrawn = ApplicationStatusFactory(name='withdrawn', is_final=True)
        
        self.assertTrue(accepted.is_final)
        self.assertTrue(rejected.is_final)
        self.assertTrue(withdrawn.is_final)
    
    def test_application_status_meta_options(self):
        """Test application status model meta options."""
        self.assertEqual(ApplicationStatus._meta.db_table, 'application_status')
        self.assertEqual(ApplicationStatus._meta.verbose_name, 'Application Status')
        self.assertEqual(ApplicationStatus._meta.verbose_name_plural, 'Application Statuses')
        self.assertEqual(ApplicationStatus._meta.ordering, ['name'])


class ApplicationModelTest(BaseModelTestCase):
    """Test cases for Application model."""
    
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.job = JobFactory()
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted', is_final=True)
        self.rejected_status = ApplicationStatusFactory(name='rejected', is_final=True)
        self.withdrawn_status = ApplicationStatusFactory(name='withdrawn', is_final=True)
    
    def test_application_creation(self):
        """Test basic application creation."""
        application = ApplicationFactory()
        self.assertIsInstance(application, Application)
        self.assertIsNotNone(application.applied_at)
        self.assertIsNotNone(application.updated_at)
        self.assertIsNone(application.reviewed_at)
        self.assertIsNone(application.reviewed_by)
    
    def test_application_str_representation(self):
        """Test application string representation."""
        user = UserFactory(email='test@example.com')
        job = JobFactory(title='Software Engineer', company__name='Tech Corp')
        application = ApplicationFactory(user=user, job=job)
        
        expected_str = 'test@example.com - Software Engineer at Tech Corp'
        self.assertEqual(str(application), expected_str)
    
    def test_unique_together_user_job(self):
        """Test unique_together constraint on user and job."""
        user = UserFactory()
        job = JobFactory()
        
        # Create first application
        ApplicationFactory(user=user, job=job)
        
        # Try to create duplicate application
        with self.assertRaises(IntegrityError):
            ApplicationFactory(user=user, job=job)
    
    def test_default_status_assignment(self):
        """Test that default status is assigned on creation."""
        application = ApplicationFactory(status=None)
        self.assertEqual(application.status.name, 'pending')
    
    def test_clean_method_job_can_apply(self):
        """Test clean method validates job can accept applications."""
        # Active job should be valid
        active_job = JobFactory(is_active=True)
        application = ApplicationFactory.build(job=active_job)
        self.assertModelValid(application)
        
        # Inactive job should be invalid
        inactive_job = JobFactory(is_active=False)
        application_invalid = ApplicationFactory.build(job=inactive_job)
        self.assertModelInvalid(application_invalid)
    
    def test_clean_method_own_job_application(self):
        """Test clean method prevents applying to own job."""
        user = UserFactory()
        job = JobFactory(created_by=user)
        
        application = ApplicationFactory.build(user=user, job=job)
        self.assertModelInvalid(application)
    
    def test_reviewed_at_timestamp_setting(self):
        """Test that reviewed_at is set when status changes from pending."""
        application = ApplicationFactory(status=self.pending_status)
        self.assertIsNone(application.reviewed_at)
        
        # Change status to reviewed
        application.status = self.reviewed_status
        application.save()
        
        application.refresh_from_db()
        self.assertIsNotNone(application.reviewed_at)
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        application = ApplicationFactory()
        expected_url = f'/applications/{application.pk}/'
        self.assertEqual(application.get_absolute_url(), expected_url)
    
    def test_can_withdraw(self):
        """Test can_withdraw method."""
        # Pending application can be withdrawn
        pending_app = ApplicationFactory(status=self.pending_status)
        self.assertTrue(pending_app.can_withdraw())
        
        # Reviewed application can be withdrawn
        reviewed_app = ApplicationFactory(status=self.reviewed_status)
        self.assertTrue(reviewed_app.can_withdraw())
        
        # Accepted application cannot be withdrawn
        accepted_app = ApplicationFactory(status=self.accepted_status)
        self.assertFalse(accepted_app.can_withdraw())
        
        # Rejected application cannot be withdrawn
        rejected_app = ApplicationFactory(status=self.rejected_status)
        self.assertFalse(rejected_app.can_withdraw())
    
    def test_can_update_status(self):
        """Test can_update_status method."""
        # Non-final status can be updated
        pending_app = ApplicationFactory(status=self.pending_status)
        self.assertTrue(pending_app.can_update_status())
        
        # Final status cannot be updated
        accepted_app = ApplicationFactory(status=self.accepted_status)
        self.assertFalse(accepted_app.can_update_status())
    
    def test_withdraw_method(self):
        """Test withdraw method."""
        application = ApplicationFactory(status=self.pending_status)
        
        # Should be able to withdraw
        application.withdraw()
        application.refresh_from_db()
        self.assertEqual(application.status.name, 'withdrawn')
        
        # Should not be able to withdraw again
        with self.assertRaises(ValidationError):
            application.withdraw()
    
    def test_update_status_method(self):
        """Test update_status method."""
        application = ApplicationFactory(status=self.pending_status)
        admin_user = AdminUserFactory()
        notes = 'Application looks good'
        
        # Update status
        application.update_status(
            new_status=self.reviewed_status,
            reviewed_by=admin_user,
            notes=notes
        )
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.reviewed_status)
        self.assertEqual(application.reviewed_by, admin_user)
        self.assertEqual(application.notes, notes)
        self.assertIsNotNone(application.reviewed_at)
    
    def test_update_status_final_status(self):
        """Test update_status with final status."""
        application = ApplicationFactory(status=self.accepted_status)
        
        with self.assertRaises(ValidationError):
            application.update_status(self.rejected_status)
    
    def test_days_since_applied_property(self):
        """Test days_since_applied property."""
        # Create application with specific applied time
        past_time = timezone.now() - timedelta(days=5)
        application = ApplicationFactory()
        application.applied_at = past_time
        application.save()
        
        self.assertEqual(application.days_since_applied, 5)
    
    def test_is_recent_property(self):
        """Test is_recent property."""
        # Recent application (applied today)
        recent_app = ApplicationFactory()
        self.assertTrue(recent_app.is_recent)
        
        # Old application (applied 10 days ago)
        old_time = timezone.now() - timedelta(days=10)
        old_app = ApplicationFactory()
        old_app.applied_at = old_time
        old_app.save()
        self.assertFalse(old_app.is_recent)
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships."""
        application = ApplicationFactory()
        
        # Test user relationship
        self.assertIsNotNone(application.user)
        
        # Test job relationship
        self.assertIsNotNone(application.job)
        
        # Test status relationship
        self.assertIsNotNone(application.status)
    
    def test_application_meta_options(self):
        """Test application model meta options."""
        self.assertEqual(Application._meta.db_table, 'application')
        self.assertEqual(Application._meta.verbose_name, 'Application')
        self.assertEqual(Application._meta.verbose_name_plural, 'Applications')
        self.assertEqual(Application._meta.ordering, ['-applied_at'])
        
        # Test unique_together
        unique_together = Application._meta.unique_together
        self.assertIn(('user', 'job'), unique_together)
        
        # Test indexes
        index_fields = [index.fields for index in Application._meta.indexes]
        expected_indexes = [
            ['user', 'status'], ['job', 'status'], 
            ['applied_at'], ['status', 'applied_at']
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_fields)


class DocumentModelTest(BaseModelTestCase):
    """Test cases for Document model."""
    
    def test_document_creation(self):
        """Test basic document creation."""
        document = DocumentFactory()
        self.assertIsInstance(document, Document)
        self.assertIsNotNone(document.uploaded_at)
    
    def test_document_str_representation(self):
        """Test document string representation."""
        application = ApplicationFactory()
        document = DocumentFactory(
            title='Resume.pdf',
            document_type='resume',
            application=application
        )
        
        expected_str = f'Resume.pdf (Resume/CV) - {application}'
        self.assertEqual(str(document), expected_str)
    
    def test_document_type_choices(self):
        """Test document type choices."""
        valid_types = ['resume', 'cover_letter', 'portfolio', 'certificate', 'other']
        
        for doc_type in valid_types:
            document = DocumentFactory.build(document_type=doc_type)
            self.assertModelValid(document)
    
    def test_file_metadata_setting(self):
        """Test that file metadata is set on save."""
        document = DocumentFactory()
        
        # File size should be set
        self.assertIsNotNone(document.file_size)
        self.assertGreater(document.file_size, 0)
    
    def test_get_file_extension(self):
        """Test get_file_extension method."""
        # Test with PDF file
        document = DocumentFactory()
        document.file.name = 'resume.pdf'
        self.assertEqual(document.get_file_extension(), 'pdf')
        
        # Test with DOC file
        document.file.name = 'resume.doc'
        self.assertEqual(document.get_file_extension(), 'doc')
        
        # Test with no extension
        document.file.name = 'resume'
        self.assertEqual(document.get_file_extension(), '')
    
    def test_get_file_size_display(self):
        """Test get_file_size_display method."""
        document = DocumentFactory()
        
        # Test with different file sizes
        document.file_size = 1024  # 1KB
        self.assertEqual(document.get_file_size_display(), '1024.0 B')
        
        document.file_size = 1024 * 1024  # 1MB
        self.assertEqual(document.get_file_size_display(), '1.0 MB')
        
        document.file_size = None
        self.assertEqual(document.get_file_size_display(), 'Unknown size')
    
    def test_is_pdf_property(self):
        """Test is_pdf property."""
        document = DocumentFactory()
        
        # Test with PDF extension
        document.file.name = 'resume.pdf'
        self.assertTrue(document.is_pdf)
        
        # Test with PDF content type
        document.file.name = 'resume'
        document.content_type = 'application/pdf'
        self.assertTrue(document.is_pdf)
        
        # Test with non-PDF
        document.file.name = 'resume.doc'
        document.content_type = 'application/msword'
        self.assertFalse(document.is_pdf)
    
    def test_is_image_property(self):
        """Test is_image property."""
        document = DocumentFactory()
        
        # Test with image extension
        document.file.name = 'photo.jpg'
        self.assertTrue(document.is_image)
        
        # Test with image content type
        document.file.name = 'photo'
        document.content_type = 'image/jpeg'
        self.assertTrue(document.is_image)
        
        # Test with non-image
        document.file.name = 'resume.pdf'
        document.content_type = 'application/pdf'
        self.assertFalse(document.is_image)
    
    def test_is_document_property(self):
        """Test is_document property."""
        document = DocumentFactory()
        
        # Test with document extensions
        document_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf']
        for ext in document_extensions:
            document.file.name = f'file.{ext}'
            self.assertTrue(document.is_document)
        
        # Test with document content types
        document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/rtf'
        ]
        for content_type in document_types:
            document.file.name = 'file'
            document.content_type = content_type
            self.assertTrue(document.is_document)
        
        # Test with non-document
        document.file.name = 'photo.jpg'
        document.content_type = 'image/jpeg'
        self.assertFalse(document.is_document)
    
    def test_foreign_key_relationship_with_application(self):
        """Test foreign key relationship with Application."""
        application = ApplicationFactory()
        document = DocumentFactory(application=application)
        
        # Test forward relationship
        self.assertEqual(document.application, application)
        
        # Test reverse relationship
        self.assertIn(document, application.documents.all())
    
    def test_cascade_delete_with_application(self):
        """Test cascade delete when application is deleted."""
        application = ApplicationFactory()
        document = DocumentFactory(application=application)
        document_id = document.id
        
        # Delete application
        application.delete()
        
        # Document should be deleted too
        with self.assertRaises(Document.DoesNotExist):
            Document.objects.get(id=document_id)
    
    def test_document_meta_options(self):
        """Test document model meta options."""
        self.assertEqual(Document._meta.db_table, 'application_document')
        self.assertEqual(Document._meta.verbose_name, 'Application Document')
        self.assertEqual(Document._meta.verbose_name_plural, 'Application Documents')
        self.assertEqual(Document._meta.ordering, ['-uploaded_at'])
        
        # Test indexes
        index_fields = [index.fields for index in Document._meta.indexes]
        expected_indexes = [
            ['application', 'document_type'],
            ['uploaded_at']
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_fields)