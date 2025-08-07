"""
Integration tests for job management API endpoints.
Tests job CRUD operations, filtering, search, and permissions.
"""
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from tests.base import BaseAPIEndpointTestCase
from tests.factories import (
    UserFactory, AdminUserFactory, JobFactory, CompanyFactory,
    CategoryFactory, IndustryFactory, JobTypeFactory
)
from apps.jobs.models import Job, Company

User = get_user_model()


class JobAPITestCase(BaseAPIEndpointTestCase):
    """Test job API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create test data
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        self.category = CategoryFactory()
        
        # Create sample jobs
        self.job1 = JobFactory(
            title='Senior Python Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            location='San Francisco, CA',
            is_active=True
        )
        self.job1.categories.add(self.category)
        
        self.job2 = JobFactory(
            title='Frontend React Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            location='New York, NY',
            is_active=True
        )
        self.job2.categories.add(self.category)
        
        self.inactive_job = JobFactory(
            title='Inactive Job',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=False
        )
    
    def test_list_jobs_unauthenticated(self):
        """Test listing jobs without authentication."""
        response = self.client.get(self.jobs_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        # Should only return active jobs
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Senior Python Developer', job_titles)
        self.assertIn('Frontend React Developer', job_titles)
        self.assertNotIn('Inactive Job', job_titles)
    
    def test_list_jobs_authenticated(self):
        """Test listing jobs with authentication."""
        self.authenticate_user()
        
        response = self.client.get(self.jobs_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        # Verify response structure
        job_data = response.data['results'][0]
        expected_fields = [
            'id', 'title', 'summary', 'company', 'location', 'is_remote',
            'salary_min', 'salary_max', 'salary_type', 'job_type', 'industry',
            'categories', 'experience_level', 'is_featured', 'created_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, job_data)
    
    def test_retrieve_job_success(self):
        """Test retrieving a specific job."""
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        response = self.client.get(job_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior Python Developer')
        self.assertEqual(response.data['company']['name'], self.company.name)
        
        # Verify detailed fields are included
        detailed_fields = [
            'description', 'required_skills', 'preferred_skills',
            'application_deadline', 'views_count', 'applications_count'
        ]
        
        for field in detailed_fields:
            self.assertIn(field, response.data)
    
    def test_retrieve_inactive_job_not_found(self):
        """Test retrieving inactive job returns 404."""
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.inactive_job.pk})
        
        response = self.client.get(job_url)
        
        self.assertNotFound(response)
    
    def test_create_job_admin_success(self):
        """Test creating job as admin user."""
        self.authenticate_admin()
        
        job_data = {
            'title': 'New Backend Developer',
            'description': 'We are looking for a backend developer...',
            'summary': 'Backend developer position',
            'company': self.company.pk,
            'location': 'Austin, TX',
            'is_remote': False,
            'salary_min': 80000,
            'salary_max': 120000,
            'salary_type': 'yearly',
            'salary_currency': 'USD',
            'job_type': self.job_type.pk,
            'industry': self.industry.pk,
            'categories': [self.category.pk],
            'experience_level': 'mid',
            'required_skills': 'Python, Django, PostgreSQL',
            'preferred_skills': 'Docker, AWS',
        }
        
        response = self.client.post(self.jobs_url, job_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Backend Developer')
        self.assertEqual(response.data['created_by'], self.admin_user.pk)
        
        # Verify job was created in database
        job = Job.objects.get(title='New Backend Developer')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.salary_min, 80000)
        self.assertTrue(job.categories.filter(pk=self.category.pk).exists())
    
    def test_create_job_regular_user_forbidden(self):
        """Test creating job as regular user is forbidden."""
        self.authenticate_user()
        
        job_data = {
            'title': 'Unauthorized Job',
            'description': 'This should not be created',
            'company': self.company.pk,
            'job_type': self.job_type.pk,
            'industry': self.industry.pk,
        }
        
        response = self.client.post(self.jobs_url, job_data)
        
        self.assertPermissionDenied(response)
    
    def test_create_job_unauthenticated_forbidden(self):
        """Test creating job without authentication is forbidden."""
        job_data = {
            'title': 'Unauthorized Job',
            'description': 'This should not be created',
            'company': self.company.pk,
            'job_type': self.job_type.pk,
            'industry': self.industry.pk,
        }
        
        response = self.client.post(self.jobs_url, job_data)
        
        self.assertPermissionDenied(response)
    
    def test_create_job_invalid_data(self):
        """Test creating job with invalid data."""
        self.authenticate_admin()
        
        job_data = {
            'title': '',  # Empty title
            'description': 'Valid description',
            'company': 999,  # Non-existent company
            'job_type': self.job_type.pk,
            'industry': self.industry.pk,
        }
        
        response = self.client.post(self.jobs_url, job_data)
        
        self.assertValidationError(response)
        self.assertIn('title', response.data)
        self.assertIn('company', response.data)
    
    def test_update_job_admin_success(self):
        """Test updating job as admin user."""
        self.authenticate_admin()
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        update_data = {
            'title': 'Updated Senior Python Developer',
            'description': self.job1.description,
            'summary': self.job1.summary,
            'company': self.company.pk,
            'location': 'Remote',
            'is_remote': True,
            'salary_min': 100000,
            'salary_max': 150000,
            'salary_type': 'yearly',
            'salary_currency': 'USD',
            'job_type': self.job_type.pk,
            'industry': self.industry.pk,
            'categories': [self.category.pk],
            'experience_level': 'senior',
            'required_skills': 'Python, Django, FastAPI',
        }
        
        response = self.client.put(job_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Senior Python Developer')
        self.assertEqual(response.data['location'], 'Remote')
        self.assertTrue(response.data['is_remote'])
        self.assertEqual(response.data['salary_min'], '100000.00')
        
        # Verify job was updated in database
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.title, 'Updated Senior Python Developer')
        self.assertEqual(self.job1.location, 'Remote')
        self.assertTrue(self.job1.is_remote)
    
    def test_update_job_regular_user_forbidden(self):
        """Test updating job as regular user is forbidden."""
        self.authenticate_user()
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        update_data = {
            'title': 'Unauthorized Update',
        }
        
        response = self.client.put(job_url, update_data)
        
        self.assertPermissionDenied(response)
    
    def test_partial_update_job_admin_success(self):
        """Test partial update of job as admin user."""
        self.authenticate_admin()
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        update_data = {
            'salary_min': 110000,
            'salary_max': 160000,
        }
        
        response = self.client.patch(job_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['salary_min'], '110000.00')
        self.assertEqual(response.data['salary_max'], '160000.00')
        
        # Verify other fields remain unchanged
        self.assertEqual(response.data['title'], 'Senior Python Developer')
    
    def test_delete_job_admin_success(self):
        """Test deleting job as admin user."""
        self.authenticate_admin()
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        response = self.client.delete(job_url)
        
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Verify job was deleted
        self.assertFalse(Job.objects.filter(pk=self.job1.pk).exists())
    
    def test_delete_job_regular_user_forbidden(self):
        """Test deleting job as regular user is forbidden."""
        self.authenticate_user()
        job_url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        response = self.client.delete(job_url)
        
        self.assertPermissionDenied(response)
        
        # Verify job still exists
        self.assertTrue(Job.objects.filter(pk=self.job1.pk).exists())


class JobFilteringTestCase(BaseAPIEndpointTestCase):
    """Test job filtering functionality."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create test data
        self.tech_industry = IndustryFactory(name='Technology')
        self.finance_industry = IndustryFactory(name='Finance')
        
        self.fulltime_type = JobTypeFactory(name='Full-time')
        self.remote_type = JobTypeFactory(name='Remote')
        
        self.dev_category = CategoryFactory(name='Development')
        self.design_category = CategoryFactory(name='Design')
        
        self.company1 = CompanyFactory(name='Tech Corp')
        self.company2 = CompanyFactory(name='Finance Inc')
        
        # Create jobs with different attributes
        self.tech_job = JobFactory(
            title='Python Developer',
            company=self.company1,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            location='San Francisco, CA',
            salary_min=80000,
            salary_max=120000,
            is_remote=False,
            is_active=True
        )
        self.tech_job.categories.add(self.dev_category)
        
        self.remote_job = JobFactory(
            title='Remote JavaScript Developer',
            company=self.company1,
            industry=self.tech_industry,
            job_type=self.remote_type,
            location='Remote',
            salary_min=70000,
            salary_max=100000,
            is_remote=True,
            is_active=True
        )
        self.remote_job.categories.add(self.dev_category)
        
        self.finance_job = JobFactory(
            title='Financial Analyst',
            company=self.company2,
            industry=self.finance_industry,
            job_type=self.fulltime_type,
            location='New York, NY',
            salary_min=60000,
            salary_max=90000,
            is_remote=False,
            is_active=True
        )
        self.finance_job.categories.add(self.design_category)
    
    def test_filter_by_industry(self):
        """Test filtering jobs by industry."""
        response = self.client.get(self.jobs_url, {'industry': self.tech_industry.pk})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Remote JavaScript Developer', job_titles)
        self.assertNotIn('Financial Analyst', job_titles)
    
    def test_filter_by_job_type(self):
        """Test filtering jobs by job type."""
        response = self.client.get(self.jobs_url, {'job_type': self.fulltime_type.pk})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Financial Analyst', job_titles)
        self.assertNotIn('Remote JavaScript Developer', job_titles)
    
    def test_filter_by_location(self):
        """Test filtering jobs by location."""
        response = self.client.get(self.jobs_url, {'location': 'San Francisco'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Developer')
    
    def test_filter_by_remote(self):
        """Test filtering jobs by remote status."""
        response = self.client.get(self.jobs_url, {'is_remote': 'true'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Remote JavaScript Developer')
    
    def test_filter_by_category(self):
        """Test filtering jobs by category."""
        response = self.client.get(self.jobs_url, {'categories': self.dev_category.pk})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Remote JavaScript Developer', job_titles)
        self.assertNotIn('Financial Analyst', job_titles)
    
    def test_filter_by_salary_range(self):
        """Test filtering jobs by salary range."""
        response = self.client.get(self.jobs_url, {
            'salary_min': 75000,
            'salary_max': 125000
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should return jobs with overlapping salary ranges
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)  # 80k-120k overlaps
        self.assertIn('Remote JavaScript Developer', job_titles)  # 70k-100k overlaps
    
    def test_filter_by_company(self):
        """Test filtering jobs by company."""
        response = self.client.get(self.jobs_url, {'company': self.company1.pk})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Remote JavaScript Developer', job_titles)
        self.assertNotIn('Financial Analyst', job_titles)
    
    def test_multiple_filters_combined(self):
        """Test combining multiple filters."""
        response = self.client.get(self.jobs_url, {
            'industry': self.tech_industry.pk,
            'job_type': self.fulltime_type.pk,
            'location': 'San Francisco'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Developer')
    
    def test_filter_no_results(self):
        """Test filtering with criteria that match no jobs."""
        response = self.client.get(self.jobs_url, {
            'industry': self.tech_industry.pk,
            'location': 'Nonexistent City'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)


class JobSearchTestCase(BaseAPIEndpointTestCase):
    """Test job search functionality."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create test data
        self.company = CompanyFactory(name='Search Test Company')
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        
        # Create jobs with searchable content
        self.python_job = JobFactory(
            title='Senior Python Developer',
            description='We are looking for a Python developer with Django experience...',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            required_skills='Python, Django, PostgreSQL',
            is_active=True
        )
        
        self.javascript_job = JobFactory(
            title='Frontend JavaScript Engineer',
            description='Join our team as a JavaScript developer working with React...',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            required_skills='JavaScript, React, HTML, CSS',
            is_active=True
        )
        
        self.data_job = JobFactory(
            title='Data Scientist',
            description='We need a data scientist with machine learning expertise...',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            required_skills='Python, Machine Learning, Statistics',
            is_active=True
        )
    
    def test_search_by_title(self):
        """Test searching jobs by title."""
        response = self.client.get(self.jobs_url, {'search': 'Python'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Python job and Data job (Python in skills)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Senior Python Developer', job_titles)
        self.assertIn('Data Scientist', job_titles)
    
    def test_search_by_description(self):
        """Test searching jobs by description content."""
        response = self.client.get(self.jobs_url, {'search': 'Django'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
    
    def test_search_by_company_name(self):
        """Test searching jobs by company name."""
        response = self.client.get(self.jobs_url, {'search': 'Search Test'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All jobs from this company
    
    def test_search_by_skills(self):
        """Test searching jobs by required skills."""
        response = self.client.get(self.jobs_url, {'search': 'React'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Frontend JavaScript Engineer')
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        response = self.client.get(self.jobs_url, {'search': 'python'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Senior Python Developer', job_titles)
    
    def test_search_partial_match(self):
        """Test searching with partial matches."""
        response = self.client.get(self.jobs_url, {'search': 'develop'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        # Should match "Developer" in titles
        job_titles = [job['title'] for job in response.data['results']]
        matching_titles = [title for title in job_titles if 'Developer' in title]
        self.assertGreater(len(matching_titles), 0)
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.jobs_url, {'search': 'nonexistent'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_search_combined_with_filters(self):
        """Test combining search with filters."""
        response = self.client.get(self.jobs_url, {
            'search': 'Python',
            'industry': self.industry.pk
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        # All results should be from the specified industry
        for job in response.data['results']:
            self.assertEqual(job['industry']['id'], self.industry.pk)
    
    def test_search_empty_query(self):
        """Test search with empty query returns all jobs."""
        response = self.client.get(self.jobs_url, {'search': ''})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All active jobs


class JobPaginationTestCase(BaseAPIEndpointTestCase):
    """Test job listing pagination."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create multiple jobs for pagination testing
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        
        self.jobs = []
        for i in range(25):  # Create 25 jobs
            job = JobFactory(
                title=f'Job {i+1}',
                company=self.company,
                industry=self.industry,
                job_type=self.job_type,
                is_active=True
            )
            self.jobs.append(job)
    
    def test_default_pagination(self):
        """Test default pagination settings."""
        response = self.client.get(self.jobs_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response, expected_count=25)
        
        # Check default page size (should be 20 or configured value)
        self.assertLessEqual(len(response.data['results']), 20)
    
    def test_custom_page_size(self):
        """Test custom page size parameter."""
        response = self.client.get(self.jobs_url, {'page_size': 10})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)
    
    def test_pagination_navigation(self):
        """Test pagination navigation links."""
        response = self.client.get(self.jobs_url, {'page_size': 10})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data['previous'])  # First page
        self.assertIsNotNone(response.data['next'])   # Has next page
        
        # Test second page
        next_url = response.data['next']
        response2 = self.client.get(next_url)
        
        self.assertResponseStatus(response2, status.HTTP_200_OK)
        self.assertIsNotNone(response2.data['previous'])  # Has previous page
    
    def test_invalid_page_number(self):
        """Test requesting invalid page number."""
        response = self.client.get(self.jobs_url, {'page': 999})
        
        self.assertResponseStatus(response, status.HTTP_404_NOT_FOUND)
    
    def test_page_size_limit(self):
        """Test page size limit enforcement."""
        response = self.client.get(self.jobs_url, {'page_size': 1000})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        # Should be limited to maximum allowed page size
        self.assertLessEqual(len(response.data['results']), 100)


class CompanyAPITestCase(BaseAPIEndpointTestCase):
    """Test company API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.companies_url = reverse('jobs:company-list')
        
        self.company1 = CompanyFactory(name='Tech Corp', is_active=True)
        self.company2 = CompanyFactory(name='Finance Inc', is_active=True)
        self.inactive_company = CompanyFactory(name='Inactive Corp', is_active=False)
    
    def test_list_companies(self):
        """Test listing companies."""
        response = self.client.get(self.companies_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        # Should only return active companies
        company_names = [company['name'] for company in response.data['results']]
        self.assertIn('Tech Corp', company_names)
        self.assertIn('Finance Inc', company_names)
        self.assertNotIn('Inactive Corp', company_names)
    
    def test_retrieve_company(self):
        """Test retrieving a specific company."""
        company_url = reverse('jobs:company-detail', kwargs={'pk': self.company1.pk})
        
        response = self.client.get(company_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tech Corp')
        
        expected_fields = [
            'id', 'name', 'description', 'website', 'email',
            'phone', 'address', 'founded_year', 'employee_count'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_create_company_admin_success(self):
        """Test creating company as admin user."""
        self.authenticate_admin()
        
        company_data = {
            'name': 'New Company',
            'description': 'A new company for testing',
            'website': 'https://newcompany.com',
            'email': 'contact@newcompany.com',
            'phone': '+1-555-123-4567',
            'address': '123 New Street, New City, NC 12345',
            'founded_year': 2020,
            'employee_count': '10-50'
        }
        
        response = self.client.post(self.companies_url, company_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Company')
        
        # Verify company was created
        company = Company.objects.get(name='New Company')
        self.assertEqual(company.website, 'https://newcompany.com')
    
    def test_create_company_regular_user_forbidden(self):
        """Test creating company as regular user is forbidden."""
        self.authenticate_user()
        
        company_data = {
            'name': 'Unauthorized Company',
            'description': 'This should not be created'
        }
        
        response = self.client.post(self.companies_url, company_data)
        
        self.assertPermissionDenied(response)