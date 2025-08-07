"""
Integration tests for application management API endpoints.
Tests application submission, status management, and document handling.
"""
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.base import BaseAPIEndpointTestCase
from tests.factories import (
    UserFactory, AdminUserFactory, JobFactory, ApplicationFactory,
    ApplicationStatusFactory, DocumentFactory, CompanyFactory,
    IndustryFactory, JobTypeFactory
)
from apps.applications.models import Application, Document

User = get_user_model()


class ApplicationAPITestCase(BaseAPIEndpointTestCase):
    """Test application API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.applications_url = reverse('applications:application-list')
        
        # Create test data
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        
        self.job1 = JobFactory(
            title='Python Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        
        self.job2 = JobFactory(
            title='JavaScript Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        
        # Create application statuses
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted')
        self.rejected_status = ApplicationStatusFactory(name='rejected')
        
        # Create test users
        self.applicant_user = UserFactory()
        self.other_user = UserFactory()
        
        # Create existing applications
        self.user_application = ApplicationFactory(
            user=self.applicant_user,
            job=self.job1,
            status=self.pending_status,
            cover_letter='I am interested in this position...'
        )
        
        self.other_application = ApplicationFactory(
            user=self.other_user,
            job=self.job2,
            status=self.reviewed_status
        )
    
    def test_list_applications_user_own_only(self):
        """Test that users can only see their own applications."""
        self.authenticate_user(self.applicant_user)
        
        response = self.client.get(self.applications_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=1)
        
        application_data = response.data['results'][0]
        self.assertEqual(application_data['id'], self.user_application.id)
        self.assertEqual(application_data['user'], self.applicant_user.id)
        self.assertEqual(application_data['job']['id'], self.job1.id)
    
    def test_list_applications_admin_sees_all(self):
        """Test that admin users can see all applications."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=2)
        
        application_ids = [app['id'] for app in response.data['results']]
        self.assertIn(self.user_application.id, application_ids)
        self.assertIn(self.other_application.id, application_ids)
    
    def test_list_applications_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot list applications."""
        response = self.client.get(self.applications_url)
        
        self.assertPermissionDenied(response)
    
    def test_retrieve_application_owner_success(self):
        """Test retrieving application by owner."""
        self.authenticate_user(self.applicant_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        response = self.client.get(application_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_application.id)
        
        expected_fields = [
            'id', 'user', 'job', 'status', 'cover_letter',
            'notes', 'applied_at', 'updated_at', 'reviewed_by', 'reviewed_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_retrieve_application_non_owner_forbidden(self):
        """Test that users cannot retrieve others' applications."""
        self.authenticate_user(self.other_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        response = self.client.get(application_url)
        
        self.assertPermissionDenied(response)
    
    def test_retrieve_application_admin_success(self):
        """Test that admin can retrieve any application."""
        self.authenticate_admin()
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        response = self.client.get(application_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_application.id)
    
    def test_create_application_success(self):
        """Test successful application creation."""
        self.authenticate_user(self.applicant_user)
        
        application_data = {
            'job': self.job2.id,
            'cover_letter': 'I am very interested in this JavaScript position...',
            'notes': 'Available to start immediately'
        }
        
        response = self.client.post(self.applications_url, application_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['job']['id'], self.job2.id)
        self.assertEqual(response.data['user'], self.applicant_user.id)
        self.assertEqual(response.data['status']['name'], 'pending')
        
        # Verify application was created in database
        application = Application.objects.get(
            user=self.applicant_user,
            job=self.job2
        )
        self.assertEqual(application.cover_letter, application_data['cover_letter'])
    
    def test_create_application_duplicate_forbidden(self):
        """Test that duplicate applications are not allowed."""
        self.authenticate_user(self.applicant_user)
        
        application_data = {
            'job': self.job1.id,  # User already has application for this job
            'cover_letter': 'Duplicate application attempt'
        }
        
        response = self.client.post(self.applications_url, application_data)
        
        self.assertValidationError(response)
        # Should contain error about duplicate application
        self.assertIn('non_field_errors', response.data)
    
    def test_create_application_inactive_job_forbidden(self):
        """Test that applications cannot be created for inactive jobs."""
        inactive_job = JobFactory(
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=False
        )
        
        self.authenticate_user(self.applicant_user)
        
        application_data = {
            'job': inactive_job.id,
            'cover_letter': 'Application for inactive job'
        }
        
        response = self.client.post(self.applications_url, application_data)
        
        self.assertValidationError(response, 'job')
    
    def test_create_application_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot create applications."""
        application_data = {
            'job': self.job2.id,
            'cover_letter': 'Unauthorized application'
        }
        
        response = self.client.post(self.applications_url, application_data)
        
        self.assertPermissionDenied(response)
    
    def test_update_application_status_admin_success(self):
        """Test updating application status as admin."""
        self.authenticate_admin()
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        update_data = {
            'status': self.reviewed_status.id,
            'notes': 'Application reviewed and looks promising'
        }
        
        response = self.client.patch(application_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['status']['name'], 'reviewed')
        self.assertEqual(response.data['reviewed_by'], self.admin_user.id)
        self.assertIsNotNone(response.data['reviewed_at'])
        
        # Verify application was updated in database
        self.user_application.refresh_from_db()
        self.assertEqual(self.user_application.status, self.reviewed_status)
        self.assertEqual(self.user_application.reviewed_by, self.admin_user)
    
    def test_update_application_status_user_forbidden(self):
        """Test that regular users cannot update application status."""
        self.authenticate_user(self.applicant_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        update_data = {
            'status': self.reviewed_status.id
        }
        
        response = self.client.patch(application_url, update_data)
        
        self.assertPermissionDenied(response)
    
    def test_update_application_cover_letter_user_success(self):
        """Test that users can update their own application cover letter."""
        self.authenticate_user(self.applicant_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        update_data = {
            'cover_letter': 'Updated cover letter with more details...'
        }
        
        response = self.client.patch(application_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['cover_letter'], update_data['cover_letter'])
        
        # Verify application was updated
        self.user_application.refresh_from_db()
        self.assertEqual(self.user_application.cover_letter, update_data['cover_letter'])
    
    def test_withdraw_application_user_success(self):
        """Test that users can withdraw their own applications."""
        withdrawn_status = ApplicationStatusFactory(name='withdrawn')
        
        self.authenticate_user(self.applicant_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        response = self.client.delete(application_url)
        
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Verify application was marked as withdrawn, not deleted
        self.user_application.refresh_from_db()
        self.assertEqual(self.user_application.status.name, 'withdrawn')
    
    def test_delete_application_admin_success(self):
        """Test that admin can delete applications."""
        self.authenticate_admin()
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': self.user_application.pk})
        
        response = self.client.delete(application_url)
        
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Verify application was actually deleted
        self.assertFalse(Application.objects.filter(pk=self.user_application.pk).exists())
    
    def test_filter_applications_by_status(self):
        """Test filtering applications by status."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'status': self.pending_status.id
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['status']['name'], 'pending')
    
    def test_filter_applications_by_job(self):
        """Test filtering applications by job."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'job': self.job1.id
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['job']['id'], self.job1.id)


class ApplicationStatusAPITestCase(BaseAPIEndpointTestCase):
    """Test application status API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.statuses_url = reverse('applications:applicationstatus-list')
        
        # Create application statuses
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted')
        self.rejected_status = ApplicationStatusFactory(name='rejected')
    
    def test_list_application_statuses(self):
        """Test listing application statuses."""
        response = self.client.get(self.statuses_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=4)
        
        status_names = [status['name'] for status in response.data['results']]
        self.assertIn('pending', status_names)
        self.assertIn('reviewed', status_names)
        self.assertIn('accepted', status_names)
        self.assertIn('rejected', status_names)
    
    def test_retrieve_application_status(self):
        """Test retrieving a specific application status."""
        status_url = reverse('applications:applicationstatus-detail', 
                           kwargs={'pk': self.pending_status.pk})
        
        response = self.client.get(status_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'pending')
        
        expected_fields = ['id', 'name', 'display_name', 'description', 'is_final']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_create_application_status_admin_success(self):
        """Test creating application status as admin."""
        self.authenticate_admin()
        
        status_data = {
            'name': 'interview_scheduled',
            'display_name': 'Interview Scheduled',
            'description': 'Interview has been scheduled with the candidate',
            'is_final': False
        }
        
        response = self.client.post(self.statuses_url, status_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'interview_scheduled')
    
    def test_create_application_status_user_forbidden(self):
        """Test that regular users cannot create application statuses."""
        self.authenticate_user()
        
        status_data = {
            'name': 'unauthorized_status',
            'display_name': 'Unauthorized Status'
        }
        
        response = self.client.post(self.statuses_url, status_data)
        
        self.assertPermissionDenied(response)


class DocumentAPITestCase(BaseAPIEndpointTestCase):
    """Test document API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.documents_url = reverse('applications:document-list')
        
        # Create test data
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        self.job = JobFactory(
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        
        self.status = ApplicationStatusFactory(name='pending')
        self.applicant_user = UserFactory()
        self.other_user = UserFactory()
        
        self.application = ApplicationFactory(
            user=self.applicant_user,
            job=self.job,
            status=self.status
        )
        
        # Create test document
        self.document = DocumentFactory(
            application=self.application,
            document_type='resume',
            title='Test Resume'
        )
    
    def test_list_documents_user_own_only(self):
        """Test that users can only see documents from their applications."""
        self.authenticate_user(self.applicant_user)
        
        response = self.client.get(self.documents_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=1)
        
        document_data = response.data['results'][0]
        self.assertEqual(document_data['id'], self.document.id)
        self.assertEqual(document_data['application'], self.application.id)
    
    def test_list_documents_admin_sees_all(self):
        """Test that admin users can see all documents."""
        # Create document for other user
        other_application = ApplicationFactory(
            user=self.other_user,
            job=self.job,
            status=self.status
        )
        other_document = DocumentFactory(
            application=other_application,
            document_type='cover_letter'
        )
        
        self.authenticate_admin()
        
        response = self.client.get(self.documents_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=2)
        
        document_ids = [doc['id'] for doc in response.data['results']]
        self.assertIn(self.document.id, document_ids)
        self.assertIn(other_document.id, document_ids)
    
    def test_retrieve_document_owner_success(self):
        """Test retrieving document by application owner."""
        self.authenticate_user(self.applicant_user)
        document_url = reverse('applications:document-detail', 
                             kwargs={'pk': self.document.pk})
        
        response = self.client.get(document_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.document.id)
        
        expected_fields = [
            'id', 'application', 'document_type', 'title', 'file',
            'file_size', 'content_type', 'description', 'uploaded_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_create_document_success(self):
        """Test successful document creation."""
        self.authenticate_user(self.applicant_user)
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document_data = {
            'application': self.application.id,
            'document_type': 'cover_letter',
            'title': 'My Cover Letter',
            'file': test_file,
            'description': 'Cover letter for the position'
        }
        
        response = self.client.post(self.documents_url, document_data, format='multipart')
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['document_type'], 'cover_letter')
        self.assertEqual(response.data['title'], 'My Cover Letter')
        self.assertEqual(response.data['application'], self.application.id)
        
        # Verify document was created in database
        document = Document.objects.get(title='My Cover Letter')
        self.assertEqual(document.application, self.application)
        self.assertEqual(document.document_type, 'cover_letter')
    
    def test_create_document_other_user_application_forbidden(self):
        """Test that users cannot create documents for others' applications."""
        other_application = ApplicationFactory(
            user=self.other_user,
            job=self.job,
            status=self.status
        )
        
        self.authenticate_user(self.applicant_user)
        
        test_file = SimpleUploadedFile(
            "unauthorized.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document_data = {
            'application': other_application.id,
            'document_type': 'resume',
            'title': 'Unauthorized Document',
            'file': test_file
        }
        
        response = self.client.post(self.documents_url, document_data, format='multipart')
        
        self.assertPermissionDenied(response)
    
    def test_update_document_owner_success(self):
        """Test updating document by owner."""
        self.authenticate_user(self.applicant_user)
        document_url = reverse('applications:document-detail', 
                             kwargs={'pk': self.document.pk})
        
        update_data = {
            'title': 'Updated Resume Title',
            'description': 'Updated description'
        }
        
        response = self.client.patch(document_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Resume Title')
        self.assertEqual(response.data['description'], 'Updated description')
        
        # Verify document was updated
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Resume Title')
    
    def test_delete_document_owner_success(self):
        """Test deleting document by owner."""
        self.authenticate_user(self.applicant_user)
        document_url = reverse('applications:document-detail', 
                             kwargs={'pk': self.document.pk})
        
        response = self.client.delete(document_url)
        
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Verify document was deleted
        self.assertFalse(Document.objects.filter(pk=self.document.pk).exists())
    
    def test_delete_document_non_owner_forbidden(self):
        """Test that users cannot delete others' documents."""
        self.authenticate_user(self.other_user)
        document_url = reverse('applications:document-detail', 
                             kwargs={'pk': self.document.pk})
        
        response = self.client.delete(document_url)
        
        self.assertPermissionDenied(response)
        
        # Verify document still exists
        self.assertTrue(Document.objects.filter(pk=self.document.pk).exists())
    
    def test_filter_documents_by_type(self):
        """Test filtering documents by type."""
        # Create additional document with different type
        cover_letter_doc = DocumentFactory(
            application=self.application,
            document_type='cover_letter',
            title='Cover Letter'
        )
        
        self.authenticate_user(self.applicant_user)
        
        response = self.client.get(self.documents_url, {
            'document_type': 'resume'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['document_type'], 'resume')
    
    def test_filter_documents_by_application(self):
        """Test filtering documents by application."""
        self.authenticate_admin()
        
        response = self.client.get(self.documents_url, {
            'application': self.application.id
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['application'], self.application.id)


class ApplicationWorkflowTestCase(BaseAPIEndpointTestCase):
    """Test complete application workflow scenarios."""
    
    def setUp(self):
        super().setUp()
        
        # Create test data
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        self.job = JobFactory(
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        
        # Create application statuses
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted')
        self.rejected_status = ApplicationStatusFactory(name='rejected')
        
        self.applicant_user = UserFactory()
    
    def test_complete_application_submission_workflow(self):
        """Test complete application submission and review workflow."""
        # Step 1: User submits application
        self.authenticate_user(self.applicant_user)
        
        application_data = {
            'job': self.job.id,
            'cover_letter': 'I am very interested in this position...',
            'notes': 'Available to start in 2 weeks'
        }
        
        application_response = self.client.post(
            reverse('applications:application-list'),
            application_data
        )
        
        self.assertResponseStatus(application_response, status.HTTP_201_CREATED)
        application_id = application_response.data['id']
        
        # Step 2: User uploads resume document
        test_file = SimpleUploadedFile(
            "resume.pdf",
            b"resume_content",
            content_type="application/pdf"
        )
        
        document_data = {
            'application': application_id,
            'document_type': 'resume',
            'title': 'My Resume',
            'file': test_file,
            'description': 'Updated resume for 2024'
        }
        
        document_response = self.client.post(
            reverse('applications:document-list'),
            document_data,
            format='multipart'
        )
        
        self.assertResponseStatus(document_response, status.HTTP_201_CREATED)
        
        # Step 3: Admin reviews application
        self.authenticate_admin()
        
        # Admin can see the application
        admin_list_response = self.client.get(reverse('applications:application-list'))
        self.assertResponseStatus(admin_list_response, status.HTTP_200_OK)
        self.assertEqual(admin_list_response.data['count'], 1)
        
        # Admin updates application status
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': application_id})
        
        status_update_data = {
            'status': self.reviewed_status.id,
            'notes': 'Good candidate, scheduling interview'
        }
        
        status_response = self.client.patch(application_url, status_update_data)
        self.assertResponseStatus(status_response, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status']['name'], 'reviewed')
        
        # Step 4: User can see updated status
        self.authenticate_user(self.applicant_user)
        
        user_app_response = self.client.get(application_url)
        self.assertResponseStatus(user_app_response, status.HTTP_200_OK)
        self.assertEqual(user_app_response.data['status']['name'], 'reviewed')
        self.assertIsNotNone(user_app_response.data['reviewed_at'])
        
        # Step 5: Final decision - Admin accepts application
        self.authenticate_admin()
        
        final_update_data = {
            'status': self.accepted_status.id,
            'notes': 'Congratulations! We would like to offer you the position.'
        }
        
        final_response = self.client.patch(application_url, final_update_data)
        self.assertResponseStatus(final_response, status.HTTP_200_OK)
        self.assertEqual(final_response.data['status']['name'], 'accepted')
    
    def test_application_withdrawal_workflow(self):
        """Test application withdrawal workflow."""
        # Step 1: Create application
        application = ApplicationFactory(
            user=self.applicant_user,
            job=self.job,
            status=self.pending_status
        )
        
        # Step 2: User withdraws application
        self.authenticate_user(self.applicant_user)
        application_url = reverse('applications:application-detail', 
                                kwargs={'pk': application.pk})
        
        response = self.client.delete(application_url)
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Step 3: Verify application is marked as withdrawn
        application.refresh_from_db()
        self.assertEqual(application.status.name, 'withdrawn')
        
        # Step 4: Admin can still see withdrawn application
        self.authenticate_admin()
        
        admin_response = self.client.get(application_url)
        self.assertResponseStatus(admin_response, status.HTTP_200_OK)
        self.assertEqual(admin_response.data['status']['name'], 'withdrawn')
    
    def test_bulk_application_status_update_workflow(self):
        """Test bulk status update workflow for admin."""
        # Create multiple applications
        applications = []
        for i in range(3):
            user = UserFactory()
            app = ApplicationFactory(
                user=user,
                job=self.job,
                status=self.pending_status
            )
            applications.append(app)
        
        self.authenticate_admin()
        
        # Admin can filter and update multiple applications
        # First, get all pending applications
        pending_response = self.client.get(
            reverse('applications:application-list'),
            {'status': self.pending_status.id}
        )
        
        self.assertResponseStatus(pending_response, status.HTTP_200_OK)
        self.assertEqual(pending_response.data['count'], 3)
        
        # Update each application to reviewed status
        for app_data in pending_response.data['results']:
            app_url = reverse('applications:application-detail', 
                            kwargs={'pk': app_data['id']})
            
            update_response = self.client.patch(app_url, {
                'status': self.reviewed_status.id,
                'notes': 'Batch review completed'
            })
            
            self.assertResponseStatus(update_response, status.HTTP_200_OK)
            self.assertEqual(update_response.data['status']['name'], 'reviewed')
        
        # Verify all applications are now reviewed
        reviewed_response = self.client.get(
            reverse('applications:application-list'),
            {'status': self.reviewed_status.id}
        )
        
        self.assertResponseStatus(reviewed_response, status.HTTP_200_OK)
        self.assertEqual(reviewed_response.data['count'], 3)