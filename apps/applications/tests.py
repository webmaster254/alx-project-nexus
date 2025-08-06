"""
Integration tests for application API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.applications.models import Application, ApplicationStatus, Document
from apps.jobs.models import Job, Company
from apps.categories.models import Industry, JobType, Category
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()


class ApplicationAPITestCase(APITestCase):
    """Test case for Application API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='otherpass123',
            first_name='Other',
            last_name='User'
        )
        
        # Create company
        self.company = Company.objects.create(
            name='Test Company',
            description='A test company',
            email='contact@testcompany.com'
        )
        
        # Create industry and job type
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time employment'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        
        # Create job
        self.job = Job.objects.create(
            title='Software Engineer',
            description='A great software engineering position',
            company=self.company,
            location='San Francisco, CA',
            salary_min=80000,
            salary_max=120000,
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        self.job.categories.add(self.category)
        
        # Create application statuses
        self.pending_status = ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review',
            description='Application is pending review'
        )
        
        self.reviewed_status = ApplicationStatus.objects.create(
            name='reviewed',
            display_name='Under Review',
            description='Application is under review'
        )
        
        self.accepted_status = ApplicationStatus.objects.create(
            name='accepted',
            display_name='Accepted',
            description='Application has been accepted',
            is_final=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def get_tokens_for_user(self, user):
        """Get JWT tokens for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        tokens = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
    
    def test_create_application_success(self):
        """Test successful application creation."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        data = {
            'job_id': self.job.id,
            'cover_letter': 'I am very interested in this position.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        
        application = Application.objects.first()
        self.assertEqual(application.user, self.user)
        self.assertEqual(application.job, self.job)
        self.assertEqual(application.cover_letter, data['cover_letter'])
        self.assertEqual(application.status, self.pending_status)
    
    def test_create_application_duplicate_prevention(self):
        """Test that duplicate applications are prevented."""
        # Create first application
        Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        data = {
            'job_id': self.job.id,
            'cover_letter': 'Another application for the same job.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already applied', str(response.data))
        self.assertEqual(Application.objects.count(), 1)
    
    def test_create_application_own_job_prevention(self):
        """Test that users cannot apply to their own job postings."""
        self.authenticate_user(self.admin_user)  # admin_user created the job
        
        url = reverse('applications:application-list')
        data = {
            'job_id': self.job.id,
            'cover_letter': 'Applying to my own job.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot apply to your own', str(response.data))
        self.assertEqual(Application.objects.count(), 0)
    
    def test_create_application_inactive_job(self):
        """Test that applications cannot be created for inactive jobs."""
        self.job.is_active = False
        self.job.save()
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        data = {
            'job_id': self.job.id,
            'cover_letter': 'Applying to inactive job.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('no longer accepting applications', str(response.data))
        self.assertEqual(Application.objects.count(), 0)
    
    def test_create_application_unauthenticated(self):
        """Test that unauthenticated users cannot create applications."""
        url = reverse('applications:application-list')
        data = {
            'job_id': self.job.id,
            'cover_letter': 'Unauthenticated application.'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Application.objects.count(), 0)
    
    def test_list_user_applications(self):
        """Test listing user's own applications."""
        # Create applications for different users
        app1 = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status,
            cover_letter='First application'
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job,
            status=self.pending_status,
            cover_letter='Other user application'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], app1.id)
    
    def test_list_admin_applications(self):
        """Test that admins can see all applications."""
        # Create applications for different users
        app1 = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_application_detail(self):
        """Test retrieving application details."""
        application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status,
            cover_letter='Detailed application'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-detail', kwargs={'pk': application.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], application.id)
        self.assertEqual(response.data['cover_letter'], 'Detailed application')
        self.assertIn('job', response.data)
        self.assertIn('user', response.data)
        self.assertIn('status', response.data)
    
    def test_update_application_status_admin(self):
        """Test that admins can update application status."""
        application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-detail', kwargs={'pk': application.id})
        data = {
            'status_name': 'reviewed',
            'notes': 'Application looks good'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.reviewed_status)
        self.assertEqual(application.notes, 'Application looks good')
        self.assertEqual(application.reviewed_by, self.admin_user)
        self.assertIsNotNone(application.reviewed_at)
    
    def test_update_application_status_non_admin(self):
        """Test that non-admins cannot update application status."""
        application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-detail', kwargs={'pk': application.id})
        data = {
            'status_name': 'reviewed'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_withdraw_application_success(self):
        """Test successful application withdrawal."""
        application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-withdraw', kwargs={'pk': application.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        self.assertEqual(application.status.name, 'withdrawn')
    
    def test_withdraw_application_not_owner(self):
        """Test that users cannot withdraw other users' applications."""
        application = Application.objects.create(
            user=self.other_user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-withdraw', kwargs={'pk': application.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_my_applications_endpoint(self):
        """Test the my-applications endpoint."""
        # Create applications
        app1 = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        Application.objects.create(
            user=self.other_user,
            job=self.job,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-my-applications')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], app1.id)
    
    def test_applications_by_status(self):
        """Test filtering applications by status."""
        # Create another job for the second application
        job2 = Job.objects.create(
            title='Backend Developer',
            description='Backend development position',
            company=self.company,
            location='New York, NY',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        
        # Create applications with different statuses
        app1 = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.user,
            job=job2,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.user)
        
        # Test pending applications
        url = reverse('applications:application-by-status', kwargs={'status_name': 'pending'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], app1.id)
    
    def test_application_statistics(self):
        """Test application statistics endpoint."""
        # Create another job for the second application
        job2 = Job.objects.create(
            title='Data Scientist',
            description='Data science position',
            company=self.company,
            location='Boston, MA',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        
        # Create applications with different statuses
        Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        Application.objects.create(
            user=self.user,
            job=job2,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 2)
        self.assertEqual(response.data['status_breakdown']['pending'], 1)
        self.assertEqual(response.data['status_breakdown']['reviewed'], 1)
        self.assertIn('recent_applications_30_days', response.data)
    
    def test_application_filtering(self):
        """Test application filtering functionality."""
        # Create another job
        job2 = Job.objects.create(
            title='Backend Developer',
            description='Backend development position',
            company=self.company,
            location='New York, NY',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        
        # Create applications for different jobs
        app1 = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.user,
            job=job2,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.user)
        
        # Test filtering by job
        url = reverse('applications:application-list')
        response = self.client.get(url, {'job__id': self.job.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], app1.id)
        
        # Test filtering by status
        response = self.client.get(url, {'status__name': 'reviewed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], app2.id)
    
    def test_application_search(self):
        """Test application search functionality."""
        application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.pending_status,
            cover_letter='I have experience with Python and Django'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        
        # Search by cover letter content
        response = self.client.get(url, {'search': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], application.id)
        
        # Search by job title
        response = self.client.get(url, {'search': 'Software'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], application.id)


class DocumentAPITestCase(APITestCase):
    """Test case for Document API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Create company, industry, job type, and job (simplified setup)
        self.company = Company.objects.create(name='Test Company')
        self.industry = Industry.objects.create(name='Technology')
        self.job_type = JobType.objects.create(name='Full-time', code='FT')
        
        # Create admin user for job creation
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_admin=True
        )
        
        self.job = Job.objects.create(
            title='Software Engineer',
            description='A great position',
            company=self.company,
            location='San Francisco, CA',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user  # Use admin user instead of regular user
        )
        
        # Create application status
        self.status = ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review'
        )
        
        # Create application
        self.application = Application.objects.create(
            user=self.user,
            job=self.job,
            status=self.status
        )
        
        # Set up API client
        self.client = APIClient()
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_document_success(self):
        """Test successful document creation."""
        self.authenticate_user(self.user)
        
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test_resume.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        url = reverse('applications:document-list')
        data = {
            'application': self.application.id,
            'document_type': 'resume',
            'title': 'My Resume',
            'file': test_file,
            'description': 'Updated resume'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        
        document = Document.objects.first()
        self.assertEqual(document.application, self.application)
        self.assertEqual(document.document_type, 'resume')
        self.assertEqual(document.title, 'My Resume')
    
    def test_list_user_documents(self):
        """Test listing user's documents."""
        # Create document
        document = Document.objects.create(
            application=self.application,
            document_type='resume',
            title='Test Resume',
            file='test_file.pdf'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:document-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], document.id)


class ApplicationStatusManagementTestCase(APITestCase):
    """Test case for admin application status management functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='otherpass123',
            first_name='Other',
            last_name='User'
        )
        
        # Create company, industry, job type
        self.company = Company.objects.create(
            name='Test Company',
            description='A test company',
            email='contact@testcompany.com'
        )
        
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time employment'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        
        # Create jobs
        self.job1 = Job.objects.create(
            title='Software Engineer',
            description='A great software engineering position',
            company=self.company,
            location='San Francisco, CA',
            salary_min=80000,
            salary_max=120000,
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        self.job1.categories.add(self.category)
        
        self.job2 = Job.objects.create(
            title='Backend Developer',
            description='Backend development position',
            company=self.company,
            location='New York, NY',
            salary_min=90000,
            salary_max=130000,
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        self.job2.categories.add(self.category)
        
        # Create application statuses
        self.pending_status = ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review',
            description='Application is pending review'
        )
        
        self.reviewed_status = ApplicationStatus.objects.create(
            name='reviewed',
            display_name='Under Review',
            description='Application is under review'
        )
        
        self.accepted_status = ApplicationStatus.objects.create(
            name='accepted',
            display_name='Accepted',
            description='Application has been accepted',
            is_final=True
        )
        
        self.rejected_status = ApplicationStatus.objects.create(
            name='rejected',
            display_name='Rejected',
            description='Application has been rejected',
            is_final=True
        )
        
        self.withdrawn_status = ApplicationStatus.objects.create(
            name='withdrawn',
            display_name='Withdrawn',
            description='Application was withdrawn by the applicant',
            is_final=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_admin_update_application_status_success(self):
        """Test that admins can successfully update application status."""
        # Create application
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status,
            cover_letter='Test application'
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-update-status', kwargs={'pk': application.id})
        data = {
            'status_name': 'reviewed',
            'notes': 'Application looks promising'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.reviewed_status)
        self.assertEqual(application.notes, 'Application looks promising')
        self.assertEqual(application.reviewed_by, self.admin_user)
        self.assertIsNotNone(application.reviewed_at)
    
    def test_non_admin_cannot_update_status(self):
        """Test that non-admin users cannot update application status."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-update-status', kwargs={'pk': application.id})
        data = {
            'status_name': 'reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.pending_status)
    
    def test_admin_filter_applications_by_job(self):
        """Test that admins can filter applications by job."""
        # Create applications for different jobs
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.reviewed_status
        )
        
        app3 = Application.objects.create(
            user=self.user,
            job=self.job2,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-by-job', kwargs={'job_id': self.job1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that only applications for job1 are returned
        returned_ids = [app['id'] for app in response.data['results']]
        self.assertIn(app1.id, returned_ids)
        self.assertIn(app2.id, returned_ids)
        self.assertNotIn(app3.id, returned_ids)
    
    def test_non_admin_cannot_filter_by_job(self):
        """Test that non-admin users cannot access job filtering endpoint."""
        Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-by-job', kwargs={'job_id': self.job1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_get_pending_applications(self):
        """Test admin endpoint for getting all pending applications."""
        # Create applications with different statuses
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job2,
            status=self.pending_status
        )
        
        app3 = Application.objects.create(
            user=self.user,
            job=self.job2,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-admin-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that only pending applications are returned
        returned_ids = [app['id'] for app in response.data['results']]
        self.assertIn(app1.id, returned_ids)
        self.assertIn(app2.id, returned_ids)
        self.assertNotIn(app3.id, returned_ids)
    
    def test_non_admin_cannot_access_pending_endpoint(self):
        """Test that non-admin users cannot access admin pending endpoint."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-admin-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_bulk_status_update_success(self):
        """Test successful bulk status update by admin."""
        # Create multiple applications
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.pending_status
        )
        
        app3 = Application.objects.create(
            user=self.user,
            job=self.job2,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [app1.id, app2.id, app3.id],
            'status_name': 'reviewed',
            'notes': 'Bulk review completed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 3)
        self.assertEqual(response.data['total_requested'], 3)
        
        # Verify all applications were updated
        for app in [app1, app2, app3]:
            app.refresh_from_db()
            self.assertEqual(app.status, self.reviewed_status)
            self.assertEqual(app.notes, 'Bulk review completed')
            self.assertEqual(app.reviewed_by, self.admin_user)
    
    def test_bulk_status_update_skip_final_status(self):
        """Test that bulk update skips applications with final status."""
        # Create applications with different statuses
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.accepted_status  # Final status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [app1.id, app2.id],
            'status_name': 'reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 1)  # Only app1 updated
        self.assertEqual(response.data['total_requested'], 2)
        
        # Verify only app1 was updated
        app1.refresh_from_db()
        app2.refresh_from_db()
        self.assertEqual(app1.status, self.reviewed_status)
        self.assertEqual(app2.status, self.accepted_status)  # Unchanged
    
    def test_bulk_status_update_non_admin(self):
        """Test that non-admin users cannot perform bulk status updates."""
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [app1.id],
            'status_name': 'reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_bulk_status_update_invalid_status(self):
        """Test bulk update with invalid status name."""
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [app1.id],
            'status_name': 'invalid_status'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not found', response.data['error'])
    
    def test_bulk_status_update_missing_data(self):
        """Test bulk update with missing required data."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        
        # Test missing application_ids
        response = self.client.post(url, {'status_name': 'reviewed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('application_ids is required', response.data['error'])
        
        # Test missing status_name
        response = self.client.post(url, {'application_ids': [1]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status_name is required', response.data['error'])
    
    def test_user_withdraw_application_success(self):
        """Test that users can successfully withdraw their applications."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-withdraw', kwargs={'pk': application.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.withdrawn_status)
    
    def test_user_cannot_withdraw_final_status_application(self):
        """Test that users cannot withdraw applications with final status."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.accepted_status  # Final status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-withdraw', kwargs={'pk': application.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot be withdrawn', str(response.data))
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.accepted_status)  # Unchanged
    
    def test_admin_cannot_update_final_status_application(self):
        """Test that admins cannot update applications with final status."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.accepted_status  # Final status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-update-status', kwargs={'pk': application.id})
        data = {
            'status_name': 'rejected'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot be updated', str(response.data))
        
        application.refresh_from_db()
        self.assertEqual(application.status, self.accepted_status)  # Unchanged
    
    def test_application_status_list_endpoint(self):
        """Test the application status list endpoint."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:applicationstatus-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # All statuses
        
        # Check that all statuses are returned
        status_names = [status['name'] for status in response.data['results']]
        expected_statuses = ['pending', 'reviewed', 'accepted', 'rejected', 'withdrawn']
        for expected_status in expected_statuses:
            self.assertIn(expected_status, status_names)
    
    def test_application_status_available_endpoint(self):
        """Test the available application statuses endpoint."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:applicationstatus-available')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # All statuses
        
        # Check that status details are included
        for status_data in response.data:
            self.assertIn('id', status_data)
            self.assertIn('name', status_data)
            self.assertIn('display_name', status_data)
            self.assertIn('description', status_data)
            self.assertIn('is_final', status_data)
    
    def test_application_status_unauthenticated(self):
        """Test that unauthenticated users cannot access status endpoints."""
        url = reverse('applications:applicationstatus-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_statistics_include_all_applications(self):
        """Test that admin statistics include all applications."""
        # Create applications for different users
        Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.reviewed_status
        )
        
        Application.objects.create(
            user=self.user,
            job=self.job2,
            status=self.accepted_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 3)
        self.assertEqual(response.data['status_breakdown']['pending'], 1)
        self.assertEqual(response.data['status_breakdown']['reviewed'], 1)
        self.assertEqual(response.data['status_breakdown']['accepted'], 1)
    
    def test_user_statistics_only_own_applications(self):
        """Test that user statistics only include their own applications."""
        # Create applications for different users
        Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.reviewed_status
        )
        
        Application.objects.create(
            user=self.user,
            job=self.job2,
            status=self.accepted_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 2)  # Only user's applications
        self.assertEqual(response.data['status_breakdown']['pending'], 1)
        self.assertEqual(response.data['status_breakdown']['reviewed'], 0)
        self.assertEqual(response.data['status_breakdown']['accepted'], 1)
    
    def test_admin_can_see_all_applications_in_list(self):
        """Test that admins can see all applications in the main list."""
        # Create applications for different users
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that both applications are returned
        returned_ids = [app['id'] for app in response.data['results']]
        self.assertIn(app1.id, returned_ids)
        self.assertIn(app2.id, returned_ids)
    
    def test_regular_user_only_sees_own_applications(self):
        """Test that regular users only see their own applications."""
        # Create applications for different users
        app1 = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        app2 = Application.objects.create(
            user=self.other_user,
            job=self.job1,
            status=self.reviewed_status
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Check that only user's application is returned
        self.assertEqual(response.data['results'][0]['id'], app1.id)
    
    def test_application_detail_includes_status_info(self):
        """Test that application detail includes comprehensive status information."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status,
            cover_letter='Test application'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-detail', kwargs={'pk': application.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check status information
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status']['name'], 'pending')
        self.assertEqual(response.data['status']['display_name'], 'Pending Review')
        self.assertIn('is_final', response.data['status'])
        
        # Check status-related properties
        self.assertIn('can_withdraw', response.data)
        self.assertIn('can_update_status', response.data)
        self.assertTrue(response.data['can_withdraw'])
        self.assertTrue(response.data['can_update_status'])
    
    def test_application_detail_final_status_properties(self):
        """Test application detail properties for final status applications."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.accepted_status,  # Final status
            cover_letter='Test application'
        )
        
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-detail', kwargs={'pk': application.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that final status applications cannot be withdrawn or updated
        self.assertFalse(response.data['can_withdraw'])
        self.assertFalse(response.data['can_update_status'])
    
    def test_bulk_update_with_empty_application_list(self):
        """Test bulk update with empty application list."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [],
            'status_name': 'reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('application_ids is required', response.data['error'])
    
    def test_bulk_update_with_nonexistent_applications(self):
        """Test bulk update with non-existent application IDs."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-bulk-update-status')
        data = {
            'application_ids': [99999, 99998],  # Non-existent IDs
            'status_name': 'reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No valid applications found', response.data['error'])
    
    def test_filter_by_nonexistent_job(self):
        """Test filtering by non-existent job ID."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-by-job', kwargs={'job_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not found', response.data['error'])
    
    def test_filter_by_nonexistent_status(self):
        """Test filtering by non-existent status name."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:application-by-status', kwargs={'status_name': 'nonexistent'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not found', response.data['error'])
    
    def test_application_timestamps_updated_correctly(self):
        """Test that application timestamps are updated correctly during status changes."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        # Initially, reviewed_at should be None
        self.assertIsNone(application.reviewed_at)
        self.assertIsNone(application.reviewed_by)
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-update-status', kwargs={'pk': application.id})
        data = {
            'status_name': 'reviewed',
            'notes': 'Application reviewed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        application.refresh_from_db()
        
        # After status change, reviewed_at and reviewed_by should be set
        self.assertIsNotNone(application.reviewed_at)
        self.assertEqual(application.reviewed_by, self.admin_user)
        self.assertIsNotNone(application.updated_at)
    
    def test_application_list_serializer_includes_user_info(self):
        """Test that application list includes user information for admins."""
        application = Application.objects.create(
            user=self.user,
            job=self.job1,
            status=self.pending_status
        )
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('applications:application-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        app_data = response.data['results'][0]
        self.assertIn('user_email', app_data)
        self.assertIn('user_full_name', app_data)
        self.assertEqual(app_data['user_email'], self.user.email)
        self.assertEqual(app_data['user_full_name'], self.user.get_full_name())


class ApplicationStatusAPITestCase(APITestCase):
    """Test case for ApplicationStatus API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_admin=True
        )
        
        # Create application statuses
        self.pending_status = ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review',
            description='Application is pending review',
            is_final=False
        )
        
        self.accepted_status = ApplicationStatus.objects.create(
            name='accepted',
            display_name='Accepted',
            description='Application has been accepted',
            is_final=True
        )
        
        self.client = APIClient()
    
    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_list_application_statuses(self):
        """Test listing all application statuses."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:applicationstatus-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that status data is complete
        for status_data in response.data['results']:
            self.assertIn('id', status_data)
            self.assertIn('name', status_data)
            self.assertIn('display_name', status_data)
            self.assertIn('description', status_data)
            self.assertIn('is_final', status_data)
    
    def test_retrieve_application_status(self):
        """Test retrieving a specific application status."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:applicationstatus-detail', kwargs={'pk': self.pending_status.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'pending')
        self.assertEqual(response.data['display_name'], 'Pending Review')
        self.assertFalse(response.data['is_final'])
    
    def test_application_status_read_only(self):
        """Test that application statuses are read-only for regular users."""
        self.authenticate_user(self.user)
        
        url = reverse('applications:applicationstatus-list')
        data = {
            'name': 'new_status',
            'display_name': 'New Status',
            'description': 'A new status'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should not be allowed (read-only viewset)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_application_status_unauthenticated(self):
        """Test that unauthenticated users cannot access status endpoints."""
        url = reverse('applications:applicationstatus-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)