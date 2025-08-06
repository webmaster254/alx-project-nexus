"""
Simple test to verify API documentation examples work correctly.
"""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.authentication.models import UserProfile
from apps.categories.models import Category, Industry, JobType
from apps.jobs.models import Job, Company
from apps.applications.models import ApplicationStatus

User = get_user_model()


class SimpleAPIDocumentationTest(TestCase):
    """Simple test to verify API documentation examples work."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        # Create user profiles
        UserProfile.objects.create(user=self.user)
        UserProfile.objects.create(user=self.admin)
        
        # Create test data
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry',
            slug='technology'
        )
        
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time employment',
            slug='full-time'
        )
        
        self.company = Company.objects.create(
            name='Tech Corp',
            description='Leading technology company',
            slug='tech-corp'
        )
        
        self.category = Category.objects.create(
            name='Software Development',
            description='Software development positions',
            slug='software-development'
        )
        
        # Create application status
        ApplicationStatus.objects.create(
            name='pending',
            display_name='Pending Review',
            description='Application is pending review'
        )
    
    def test_login_endpoint_with_documented_example(self):
        """Test login endpoint with the exact example from documentation."""
        url = '/api/auth/login/'
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response matches documented structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data structure
        user_data = response.data['user']
        self.assertEqual(user_data['email'], 'user@example.com')
        self.assertEqual(user_data['first_name'], 'John')
        self.assertEqual(user_data['last_name'], 'Doe')
        self.assertFalse(user_data['is_admin'])
    
    def test_register_endpoint_with_documented_example(self):
        """Test registration endpoint with documented example."""
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'first_name': 'Jane',
            'last_name': 'Smith'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response matches documented structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data includes profile
        user_data = response.data['user']
        self.assertIn('profile', user_data)
        self.assertEqual(user_data['email'], 'newuser@example.com')
    
    def test_job_creation_with_admin_permissions(self):
        """Test job creation endpoint with admin user."""
        # Login as admin
        login_response = self.client.post('/api/auth/login/', {
            'email': 'admin@example.com',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create job with documented example data
        url = '/api/jobs/'
        data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for an experienced software engineer...',
            'company': self.company.id,
            'location': 'San Francisco, CA',
            'salary_min': 120000,
            'salary_max': 180000,
            'job_type': self.job_type.id,
            'industry': self.industry.id,
            'categories': [self.category.id],
            'required_skills': 'Python, Django, PostgreSQL, React'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify response matches documented structure
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('company', response.data)
        self.assertIn('created_by', response.data)
        self.assertEqual(response.data['title'], 'Senior Software Engineer')
    
    def test_job_creation_permission_denied_for_regular_user(self):
        """Test job creation permission denied for regular user."""
        # Login as regular user
        login_response = self.client.post('/api/auth/login/', {
            'email': 'user@example.com',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Try to create job
        url = '/api/jobs/'
        data = {
            'title': 'Backend Developer',
            'description': 'Backend development position',
            'company': self.company.id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify permission denied response matches documentation
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_categories_list_endpoint(self):
        """Test categories list endpoint."""
        # Login as user
        login_response = self.client.post('/api/auth/login/', {
            'email': 'user@example.com',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = '/api/categories/'
        response = self.client.get(url)
        
        # Verify response structure matches documentation
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
    
    def test_unauthorized_access_error_response(self):
        """Test unauthorized access error matches documented response."""
        url = '/api/jobs/'
        response = self.client.get(url)
        
        # Verify error response structure matches documentation
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertIn('Authentication credentials were not provided', str(response.data['detail']))
    
    def test_not_found_error_response(self):
        """Test not found error matches documented response."""
        # Login as user
        login_response = self.client.post('/api/auth/login/', {
            'email': 'user@example.com',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Try to access non-existent job
        url = '/api/jobs/99999/'
        response = self.client.get(url)
        
        # Verify error response structure matches documentation
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)


if __name__ == '__main__':
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])