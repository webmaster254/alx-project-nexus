"""
Test suite to validate API documentation accuracy and ensure all documented endpoints work correctly.
This test file verifies that the API responses match the documented examples in the OpenAPI schema.
"""

import json
import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.models import UserProfile
from apps.jobs.models import Job, Company
from apps.categories.models import Category, Industry, JobType
from apps.applications.models import Application, ApplicationStatus

User = get_user_model()


class APIDocumentationTestCase(APITestCase):
    """
    Base test case for API documentation validation.
    Sets up common test data and authentication.
    """
    
    def setUp(self):
        """Set up test data for API documentation tests."""
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.admin_user,
            phone_number='+1234567890',
            bio='Admin user profile',
            location='San Francisco, CA',
            experience_years=10
        )
        
        UserProfile.objects.create(
            user=self.regular_user,
            phone_number='+1234567890',
            bio='Experienced software developer',
            location='San Francisco, CA',
            experience_years=5
        )
        
        # Create test categories
        self.parent_category = Category.objects.create(
            name='Software Development',
            description='Software engineering and development positions',
            slug='software-development'
        )
        
        self.child_category = Category.objects.create(
            name='Frontend Development',
            description='Frontend development positions',
            slug='frontend-development',
            parent=self.parent_category
        )
        
        # Create test industry and job type
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology and software industry',
            slug='technology'
        )
        
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time employment',
            slug='full-time'
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Tech Corp',
            description='Leading technology company',
            website='https://techcorp.com',
            email='contact@techcorp.com',
            slug='tech-corp'
        )
        
        # Create test job
        self.job = Job.objects.create(
            title='Senior Software Engineer',
            description='We are looking for an experienced software engineer...',
            company=self.company,
            location='San Francisco, CA',
            salary_min=120000,
            salary_max=180000,
            job_type=self.job_type,
            industry=self.industry,
            required_skills='Python, Django, PostgreSQL, React',
            created_by=self.admin_user
        )
        self.job.categories.add(self.parent_category)
        
        # Create application statuses
        self.pending_status = ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review',
            description='Application is pending review'
        )
        
        self.reviewed_status = ApplicationStatus.objects.create(
            name='reviewed',
            display_name='Under Review',
            description='Application is being reviewed by the hiring team'
        )
        
        # Create test application
        self.application = Application.objects.create(
            user=self.regular_user,
            job=self.job,
            status=self.pending_status,
            cover_letter='I am very interested in this position because...'
        )
        
        # Set up API client
        self.client = APIClient()
    
    def get_admin_token(self):
        """Get JWT token for admin user."""
        refresh = RefreshToken.for_user(self.admin_user)
        return str(refresh.access_token)
    
    def get_user_token(self):
        """Get JWT token for regular user."""
        refresh = RefreshToken.for_user(self.regular_user)
        return str(refresh.access_token)
    
    def authenticate_admin(self):
        """Authenticate as admin user."""
        token = self.get_admin_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def authenticate_user(self):
        """Authenticate as regular user."""
        token = self.get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class AuthenticationDocumentationTests(APIDocumentationTestCase):
    """Test authentication endpoints documentation accuracy."""
    
    def test_login_endpoint_documentation(self):
        """Test login endpoint matches documented examples."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure matches documentation
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data structure
        user_data = response.data['user']
        expected_fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_admin']
        for field in expected_fields:
            self.assertIn(field, user_data)
    
    def test_login_invalid_credentials_documentation(self):
        """Test login with invalid credentials matches documented error response."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify error response structure
        self.assertIn('detail', response.data)
    
    def test_register_endpoint_documentation(self):
        """Test registration endpoint matches documented examples."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure matches documentation
        expected_fields = ['message', 'access', 'refresh', 'user']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify user data includes profile
        user_data = response.data['user']
        self.assertIn('profile', user_data)
    
    def test_profile_endpoint_documentation(self):
        """Test profile endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('profile')
        
        # Test GET request
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        expected_fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_admin', 'profile']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify profile data structure
        profile_data = response.data['profile']
        profile_fields = ['phone_number', 'bio', 'location', 'experience_years']
        for field in profile_fields:
            self.assertIn(field, profile_data)


class JobsDocumentationTests(APIDocumentationTestCase):
    """Test jobs endpoints documentation accuracy."""
    
    def test_jobs_list_endpoint_documentation(self):
        """Test jobs list endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('job-list')
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        
        # Verify job data structure if jobs exist
        if response.data['results']:
            job_data = response.data['results'][0]
            expected_fields = [
                'id', 'title', 'company', 'location', 'salary_min', 'salary_max',
                'job_type', 'industry', 'categories', 'created_at'
            ]
            for field in expected_fields:
                self.assertIn(field, job_data)
            
            # Verify nested company structure
            company_data = job_data['company']
            self.assertIn('id', company_data)
            self.assertIn('name', company_data)
    
    def test_job_detail_endpoint_documentation(self):
        """Test job detail endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('job-detail', kwargs={'pk': self.job.pk})
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify detailed job data structure
        expected_fields = [
            'id', 'title', 'description', 'company', 'location', 'salary_min', 'salary_max',
            'job_type', 'industry', 'categories', 'required_skills', 'is_active',
            'created_at', 'updated_at', 'created_by'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_job_creation_endpoint_documentation(self):
        """Test job creation endpoint matches documented examples."""
        self.authenticate_admin()
        url = reverse('job-list')
        
        data = {
            'title': 'Backend Developer',
            'description': 'We are looking for a backend developer...',
            'company': self.company.id,
            'location': 'New York, NY',
            'salary_min': 100000,
            'salary_max': 150000,
            'job_type': self.job_type.id,
            'industry': self.industry.id,
            'categories': [self.parent_category.id],
            'required_skills': 'Python, Django, PostgreSQL'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure matches documentation
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('company', response.data)
        self.assertIn('created_by', response.data)
    
    def test_job_creation_permission_denied_documentation(self):
        """Test job creation permission denied matches documented error response."""
        self.authenticate_user()  # Regular user, not admin
        url = reverse('job-list')
        
        data = {
            'title': 'Backend Developer',
            'description': 'We are looking for a backend developer...',
            'company': self.company.id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify error response structure
        self.assertIn('error', response.data)


class ApplicationsDocumentationTests(APIDocumentationTestCase):
    """Test applications endpoints documentation accuracy."""
    
    def test_applications_list_endpoint_documentation(self):
        """Test applications list endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('application-list')
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        
        # Verify application data structure if applications exist
        if response.data['results']:
            app_data = response.data['results'][0]
            expected_fields = [
                'id', 'job', 'status', 'user_email', 'user_full_name', 'applied_at'
            ]
            for field in expected_fields:
                self.assertIn(field, app_data)
    
    def test_application_creation_endpoint_documentation(self):
        """Test application creation endpoint matches documented examples."""
        self.authenticate_user()
        
        # Create a new job to apply for (to avoid duplicate application error)
        new_job = Job.objects.create(
            title='Frontend Developer',
            description='Frontend development position',
            company=self.company,
            location='San Francisco, CA',
            salary_min=90000,
            salary_max=130000,
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        
        url = reverse('application-list')
        data = {
            'job': new_job.id,
            'cover_letter': 'I am very interested in this frontend position...'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure
        expected_fields = ['id', 'job', 'user', 'status', 'cover_letter', 'applied_at']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_application_duplicate_prevention_documentation(self):
        """Test duplicate application prevention matches documented error response."""
        self.authenticate_user()
        url = reverse('application-list')
        
        # Try to apply for the same job again
        data = {
            'job': self.job.id,
            'cover_letter': 'Another application for the same job'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify error response structure
        self.assertTrue(
            'non_field_errors' in response.data or 
            any('already applied' in str(error) for error in response.data.values())
        )
    
    def test_application_statistics_endpoint_documentation(self):
        """Test application statistics endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('application-statistics')
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistics structure
        expected_fields = ['total_applications', 'status_breakdown', 'recent_applications_30_days']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify status breakdown structure
        status_breakdown = response.data['status_breakdown']
        self.assertIsInstance(status_breakdown, dict)


class CategoriesDocumentationTests(APIDocumentationTestCase):
    """Test categories endpoints documentation accuracy."""
    
    def test_categories_list_endpoint_documentation(self):
        """Test categories list endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('category-list')
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        
        # Verify category data structure if categories exist
        if response.data['results']:
            category_data = response.data['results'][0]
            expected_fields = [
                'id', 'name', 'description', 'slug', 'parent', 'job_count',
                'full_path', 'level', 'children', 'is_active'
            ]
            for field in expected_fields:
                self.assertIn(field, category_data)
    
    def test_category_detail_endpoint_documentation(self):
        """Test category detail endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('category-detail', kwargs={'slug': self.parent_category.slug})
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify detailed category data structure
        expected_fields = [
            'id', 'name', 'description', 'slug', 'parent', 'job_count',
            'full_path', 'level', 'children', 'is_active', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_category_creation_endpoint_documentation(self):
        """Test category creation endpoint matches documented examples."""
        self.authenticate_admin()
        url = reverse('category-list')
        
        data = {
            'name': 'Data Science',
            'description': 'Data science and analytics positions',
            'parent': self.parent_category.id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify response structure
        expected_fields = ['id', 'name', 'description', 'slug', 'parent', 'parent_name']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_category_hierarchy_endpoint_documentation(self):
        """Test category hierarchy endpoint matches documented examples."""
        self.authenticate_user()
        url = reverse('category-hierarchy')
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response is a list
        self.assertIsInstance(response.data, list)
        
        # Verify hierarchy structure if categories exist
        if response.data:
            category_data = response.data[0]
            self.assertIn('children', category_data)


class ErrorResponseDocumentationTests(APIDocumentationTestCase):
    """Test error responses match documented examples."""
    
    def test_unauthorized_access_documentation(self):
        """Test unauthorized access error matches documented response."""
        # Try to access protected endpoint without authentication
        url = reverse('job-list')
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify error response structure
        self.assertIn('detail', response.data)
        self.assertIn('Authentication credentials were not provided', str(response.data['detail']))
    
    def test_not_found_error_documentation(self):
        """Test not found error matches documented response."""
        self.authenticate_user()
        url = reverse('job-detail', kwargs={'pk': 99999})  # Non-existent job
        
        response = self.client.get(url)
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify error response structure
        self.assertIn('detail', response.data)
    
    def test_validation_error_documentation(self):
        """Test validation error matches documented response."""
        self.authenticate_admin()
        url = reverse('job-list')
        
        # Send incomplete data to trigger validation error
        data = {
            'title': '',  # Empty title should trigger validation error
            'company': self.company.id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify validation error structure
        self.assertIsInstance(response.data, dict)
        # Should contain field-specific errors
        self.assertTrue(any(isinstance(v, list) for v in response.data.values()))


class TokenAuthenticationDocumentationTests(APIDocumentationTestCase):
    """Test JWT token authentication documentation accuracy."""
    
    def test_token_refresh_endpoint_documentation(self):
        """Test token refresh endpoint matches documented examples."""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.regular_user)
        refresh_token = str(refresh)
        
        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        self.assertIn('access', response.data)
        # May also include new refresh token if rotation is enabled
    
    def test_token_refresh_invalid_token_documentation(self):
        """Test token refresh with invalid token matches documented error response."""
        url = reverse('token_refresh')
        data = {'refresh': 'invalid_token'}
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify error response structure
        self.assertIn('detail', response.data)
        self.assertIn('code', response.data)
    
    def test_logout_endpoint_documentation(self):
        """Test logout endpoint matches documented examples."""
        # Get refresh token
        refresh = RefreshToken.for_user(self.regular_user)
        refresh_token = str(refresh)
        
        url = reverse('logout')
        data = {'refresh': refresh_token}
        
        response = self.client.post(url, data, format='json')
        
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        self.assertIn('message', response.data)


if __name__ == '__main__':
    # Run the tests
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])