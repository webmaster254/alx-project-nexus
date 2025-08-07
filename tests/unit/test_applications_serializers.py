"""
Unit tests for applications serializers.
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory
from datetime import timedelta

from apps.applications.serializers import (
    ApplicationStatusSerializer, DocumentSerializer, ApplicationListSerializer,
    ApplicationDetailSerializer, ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationWithdrawSerializer, BulkStatusUpdateSerializer
)
from tests.base import BaseSerializerTestCase
from tests.factories import (
    ApplicationStatusFactory, ApplicationFactory, DocumentFactory,
    UserFactory, JobFactory, AdminUserFactory
)


class ApplicationStatusSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationStatusSerializer."""
    
    def test_serializer_with_status(self):
        """Test serializer with application status instance."""
        status = ApplicationStatusFactory(
            name='pending',
            display_name='Pending Review',
            description='Application is awaiting review',
            is_final=False
        )
        
        serializer = ApplicationStatusSerializer(status)
        
        self.assertEqual(serializer.data['name'], 'pending')
        self.assertEqual(serializer.data['display_name'], 'Pending Review')
        self.assertEqual(serializer.data['description'], 'Application is awaiting review')
        self.assertFalse(serializer.data['is_final'])
    
    def test_read_only_fields(self):
        """Test that id is read-only."""
        status = ApplicationStatusFactory()
        serializer = ApplicationStatusSerializer(status)
        
        self.assertIn('id', serializer.data)
        # ID should be read-only
        self.assertTrue(serializer.fields['id'].read_only)


class DocumentSerializerTest(BaseSerializerTestCase):
    """Test cases for DocumentSerializer."""
    
    def setUp(self):
        self.valid_data = {
            'document_type': 'resume',
            'title': 'John Doe Resume',
            'description': 'Updated resume for 2024'
        }
    
    def test_serializer_with_document(self):
        """Test serializer with document instance."""
        document = DocumentFactory(
            document_type='resume',
            title='Test Resume',
            file_size=1024000
        )
        document.file.name = 'resume.pdf'
        
        serializer = DocumentSerializer(document)
        
        self.assertEqual(serializer.data['document_type'], 'resume')
        self.assertEqual(serializer.data['title'], 'Test Resume')
        self.assertEqual(serializer.data['file_extension'], 'pdf')
        self.assertIn('file_size_display', serializer.data)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        document = DocumentFactory()
        serializer = DocumentSerializer(document)
        
        read_only_fields = ['id', 'file_size', 'content_type', 'uploaded_at']
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)
    
    def test_document_type_choices(self):
        """Test document type choices validation."""
        valid_types = ['resume', 'cover_letter', 'portfolio', 'certificate', 'other']
        
        for doc_type in valid_types:
            data = self.valid_data.copy()
            data['document_type'] = doc_type
            self.assertSerializerValid(DocumentSerializer, data)


class ApplicationListSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationListSerializer."""
    
    def test_serializer_with_application(self):
        """Test serializer with application instance."""
        user = UserFactory(email='test@example.com', first_name='John', last_name='Doe')
        application = ApplicationFactory(user=user)
        
        serializer = ApplicationListSerializer(application)
        
        # Test nested data
        self.assertIn('job', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertEqual(serializer.data['user_email'], 'test@example.com')
        self.assertEqual(serializer.data['user_full_name'], 'John Doe')
        
        # Test computed fields
        self.assertIn('days_since_applied', serializer.data)
        self.assertIn('is_recent', serializer.data)
        self.assertIn('can_withdraw', serializer.data)
    
    def test_read_only_fields(self):
        """Test that all fields are read-only."""
        application = ApplicationFactory()
        serializer = ApplicationListSerializer(application)
        
        read_only_fields = ['id', 'applied_at', 'updated_at']
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)


class ApplicationDetailSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationDetailSerializer."""
    
    def test_serializer_with_application(self):
        """Test serializer with application instance."""
        application = ApplicationFactory()
        DocumentFactory.create_batch(2, application=application)
        
        serializer = ApplicationDetailSerializer(application)
        
        # Test nested data
        self.assertIn('job', serializer.data)
        self.assertIn('user', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertIn('documents', serializer.data)
        self.assertEqual(len(serializer.data['documents']), 2)
        
        # Test computed fields
        self.assertIn('days_since_applied', serializer.data)
        self.assertIn('is_recent', serializer.data)
        self.assertIn('can_withdraw', serializer.data)
        self.assertIn('can_update_status', serializer.data)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        application = ApplicationFactory()
        serializer = ApplicationDetailSerializer(application)
        
        read_only_fields = [
            'id', 'user', 'applied_at', 'updated_at', 
            'reviewed_at', 'reviewed_by', 'documents'
        ]
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)


class ApplicationCreateSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationCreateSerializer."""
    
    def setUp(self):
        self.user = UserFactory()
        self.job = JobFactory(is_active=True)
        self.factory = APIRequestFactory()
        
        self.valid_data = {
            'job_id': self.job.id,
            'cover_letter': 'I am very interested in this position...'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        serializer = self.assertSerializerValid(
            ApplicationCreateSerializer, self.valid_data, context
        )
        self.assertEqual(serializer.validated_data['job_id'], self.job.id)
    
    def test_job_id_validation_nonexistent(self):
        """Test job_id validation with nonexistent job."""
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        invalid_data = self.valid_data.copy()
        invalid_data['job_id'] = 99999
        
        self.assertSerializerInvalid(
            ApplicationCreateSerializer, invalid_data, 'job_id', context
        )
    
    def test_job_id_validation_inactive_job(self):
        """Test job_id validation with inactive job."""
        inactive_job = JobFactory(is_active=False)
        
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        invalid_data = self.valid_data.copy()
        invalid_data['job_id'] = inactive_job.id
        
        self.assertSerializerInvalid(
            ApplicationCreateSerializer, invalid_data, 'job_id', context
        )
    
    def test_duplicate_application_validation(self):
        """Test validation prevents duplicate applications."""
        # Create existing application
        ApplicationFactory(user=self.user, job=self.job)
        
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        self.assertSerializerInvalid(
            ApplicationCreateSerializer, self.valid_data, context=context
        )
    
    def test_own_job_application_validation(self):
        """Test validation prevents applying to own job."""
        own_job = JobFactory(created_by=self.user, is_active=True)
        
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        invalid_data = self.valid_data.copy()
        invalid_data['job_id'] = own_job.id
        
        self.assertSerializerInvalid(
            ApplicationCreateSerializer, invalid_data, context=context
        )
    
    def test_create_application(self):
        """Test application creation."""
        request = self.factory.post('/')
        request.user = self.user
        context = {'request': request}
        
        serializer = ApplicationCreateSerializer(data=self.valid_data, context=context)
        self.assertTrue(serializer.is_valid())
        
        application = serializer.save()
        
        # Check application was created correctly
        self.assertEqual(application.user, self.user)
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.cover_letter, self.valid_data['cover_letter'])
        self.assertEqual(application.status.name, 'pending')
        
        # Check job applications count was incremented
        self.job.refresh_from_db()
        self.assertEqual(self.job.applications_count, 1)


class ApplicationUpdateSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationUpdateSerializer."""
    
    def setUp(self):
        self.admin_user = AdminUserFactory()
        self.pending_status = ApplicationStatusFactory(name='pending', is_final=False)
        self.reviewed_status = ApplicationStatusFactory(name='reviewed', is_final=False)
        self.accepted_status = ApplicationStatusFactory(name='accepted', is_final=True)
        
        self.application = ApplicationFactory(status=self.pending_status)
        self.factory = APIRequestFactory()
        
        self.valid_data = {
            'status_name': 'reviewed',
            'notes': 'Application looks promising'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        request = self.factory.put('/')
        request.user = self.admin_user
        context = {'request': request}
        
        serializer = ApplicationUpdateSerializer(
            self.application, data=self.valid_data, context=context
        )
        self.assertTrue(serializer.is_valid())
    
    def test_status_name_validation_nonexistent(self):
        """Test status_name validation with nonexistent status."""
        request = self.factory.put('/')
        request.user = self.admin_user
        context = {'request': request}
        
        invalid_data = self.valid_data.copy()
        invalid_data['status_name'] = 'nonexistent'
        
        serializer = ApplicationUpdateSerializer(
            self.application, data=invalid_data, context=context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('status_name', serializer.errors)
    
    def test_final_status_validation(self):
        """Test validation prevents updating final status."""
        final_application = ApplicationFactory(status=self.accepted_status)
        
        request = self.factory.put('/')
        request.user = self.admin_user
        context = {'request': request}
        
        serializer = ApplicationUpdateSerializer(
            final_application, data=self.valid_data, context=context
        )
        self.assertFalse(serializer.is_valid())
    
    def test_update_application_status(self):
        """Test application status update."""
        request = self.factory.put('/')
        request.user = self.admin_user
        context = {'request': request}
        
        serializer = ApplicationUpdateSerializer(
            self.application, data=self.valid_data, context=context
        )
        self.assertTrue(serializer.is_valid())
        
        updated_application = serializer.save()
        
        # Check application was updated correctly
        self.assertEqual(updated_application.status.name, 'reviewed')
        self.assertEqual(updated_application.notes, 'Application looks promising')
        self.assertEqual(updated_application.reviewed_by, self.admin_user)
        self.assertIsNotNone(updated_application.reviewed_at)


class ApplicationWithdrawSerializerTest(BaseSerializerTestCase):
    """Test cases for ApplicationWithdrawSerializer."""
    
    def setUp(self):
        self.pending_status = ApplicationStatusFactory(name='pending', is_final=False)
        self.accepted_status = ApplicationStatusFactory(name='accepted', is_final=True)
        self.withdrawn_status = ApplicationStatusFactory(name='withdrawn', is_final=True)
    
    def test_withdraw_pending_application(self):
        """Test withdrawing pending application."""
        application = ApplicationFactory(status=self.pending_status)
        
        serializer = ApplicationWithdrawSerializer(application, data={})
        self.assertTrue(serializer.is_valid())
        
        withdrawn_application = serializer.save()
        self.assertEqual(withdrawn_application.status.name, 'withdrawn')
    
    def test_withdraw_final_application_validation(self):
        """Test validation prevents withdrawing final application."""
        application = ApplicationFactory(status=self.accepted_status)
        
        serializer = ApplicationWithdrawSerializer(application, data={})
        self.assertFalse(serializer.is_valid())


class BulkStatusUpdateSerializerTest(BaseSerializerTestCase):
    """Test cases for BulkStatusUpdateSerializer."""
    
    def setUp(self):
        self.applications = ApplicationFactory.create_batch(3)
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        
        self.valid_data = {
            'application_ids': [app.id for app in self.applications],
            'status_name': 'reviewed',
            'notes': 'Bulk update notes'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(BulkStatusUpdateSerializer, self.valid_data)
        self.assertEqual(len(serializer.validated_data['application_ids']), 3)
        self.assertEqual(serializer.validated_data['status_name'], 'reviewed')
    
    def test_status_name_validation(self):
        """Test status_name validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['status_name'] = 'nonexistent'
        
        self.assertSerializerInvalid(
            BulkStatusUpdateSerializer, invalid_data, 'status_name'
        )
    
    def test_application_ids_validation_empty(self):
        """Test application_ids validation with empty list."""
        invalid_data = self.valid_data.copy()
        invalid_data['application_ids'] = []
        
        self.assertSerializerInvalid(
            BulkStatusUpdateSerializer, invalid_data, 'application_ids'
        )
    
    def test_application_ids_validation_nonexistent(self):
        """Test application_ids validation with nonexistent IDs."""
        invalid_data = self.valid_data.copy()
        invalid_data['application_ids'] = [99999, 99998]
        
        self.assertSerializerInvalid(
            BulkStatusUpdateSerializer, invalid_data, 'application_ids'
        )
    
    def test_application_ids_validation_partial_nonexistent(self):
        """Test application_ids validation with some nonexistent IDs."""
        invalid_data = self.valid_data.copy()
        invalid_data['application_ids'] = [self.applications[0].id, 99999]
        
        self.assertSerializerInvalid(
            BulkStatusUpdateSerializer, invalid_data, 'application_ids'
        )
    
    def test_notes_field_optional(self):
        """Test that notes field is optional."""
        data = self.valid_data.copy()
        data.pop('notes')
        
        self.assertSerializerValid(BulkStatusUpdateSerializer, data)
        
        # Test with empty notes
        data['notes'] = ''
        self.assertSerializerValid(BulkStatusUpdateSerializer, data)