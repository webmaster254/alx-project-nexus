"""
Integration tests for search and filtering functionality across the API.
Tests advanced search, filtering combinations, and performance optimization.
"""
from django.urls import reverse
from rest_framework import status
from django.db import connection
from django.test.utils import override_settings

from tests.base import BaseAPIEndpointTestCase, PerformanceTestMixin
from tests.factories import (
    JobFactory, CompanyFactory, CategoryFactory, IndustryFactory,
    JobTypeFactory, UserFactory, ApplicationFactory, ApplicationStatusFactory
)


class AdvancedJobSearchTestCase(BaseAPIEndpointTestCase):
    """Test advanced job search functionality."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create test data with varied attributes
        self.tech_industry = IndustryFactory(name='Technology')
        self.finance_industry = IndustryFactory(name='Finance')
        self.healthcare_industry = IndustryFactory(name='Healthcare')
        
        self.fulltime_type = JobTypeFactory(name='Full-time')
        self.remote_type = JobTypeFactory(name='Remote')
        self.contract_type = JobTypeFactory(name='Contract')
        
        self.dev_category = CategoryFactory(name='Development')
        self.design_category = CategoryFactory(name='Design')
        self.marketing_category = CategoryFactory(name='Marketing')
        
        self.tech_company = CompanyFactory(name='TechCorp Inc')
        self.finance_company = CompanyFactory(name='FinanceBank LLC')
        self.startup_company = CompanyFactory(name='StartupXYZ')
        
        # Create diverse job postings
        self.python_job = JobFactory(
            title='Senior Python Developer',
            description='We are looking for an experienced Python developer with Django and FastAPI experience. Must have 5+ years of backend development experience.',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            location='San Francisco, CA',
            salary_min=120000,
            salary_max=160000,
            experience_level='senior',
            required_skills='Python, Django, FastAPI, PostgreSQL, Redis',
            preferred_skills='Docker, Kubernetes, AWS',
            is_remote=False,
            is_active=True
        )
        self.python_job.categories.add(self.dev_category)
        
        self.javascript_job = JobFactory(
            title='Frontend JavaScript Engineer',
            description='Join our team as a frontend engineer working with React, TypeScript, and modern web technologies. Remote-friendly position.',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.remote_type,
            location='Remote',
            salary_min=90000,
            salary_max=130000,
            experience_level='mid',
            required_skills='JavaScript, React, TypeScript, HTML, CSS',
            preferred_skills='Next.js, GraphQL, Jest',
            is_remote=True,
            is_active=True
        )
        self.javascript_job.categories.add(self.dev_category)
        
        self.data_job = JobFactory(
            title='Data Scientist',
            description='We need a data scientist with machine learning expertise to analyze large datasets and build predictive models.',
            company=self.finance_company,
            industry=self.finance_industry,
            job_type=self.fulltime_type,
            location='New York, NY',
            salary_min=110000,
            salary_max=150000,
            experience_level='mid',
            required_skills='Python, Machine Learning, Statistics, SQL',
            preferred_skills='TensorFlow, PyTorch, Spark',
            is_remote=False,
            is_active=True
        )
        self.data_job.categories.add(self.dev_category)
        
        self.designer_job = JobFactory(
            title='UX/UI Designer',
            description='Creative UX/UI designer needed for designing user interfaces and improving user experience across our products.',
            company=self.startup_company,
            industry=self.tech_industry,
            job_type=self.contract_type,
            location='Austin, TX',
            salary_min=70000,
            salary_max=100000,
            experience_level='junior',
            required_skills='Figma, Sketch, Adobe Creative Suite, User Research',
            preferred_skills='Prototyping, Animation, HTML/CSS',
            is_remote=True,
            is_active=True
        )
        self.designer_job.categories.add(self.design_category)
        
        self.marketing_job = JobFactory(
            title='Digital Marketing Manager',
            description='Lead our digital marketing efforts including SEO, SEM, social media marketing, and content strategy.',
            company=self.startup_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            location='Los Angeles, CA',
            salary_min=80000,
            salary_max=120000,
            experience_level='mid',
            required_skills='SEO, SEM, Google Analytics, Social Media Marketing',
            preferred_skills='Content Marketing, Email Marketing, A/B Testing',
            is_remote=False,
            is_active=True
        )
        self.marketing_job.categories.add(self.marketing_category)
    
    def test_full_text_search_title(self):
        """Test full-text search in job titles."""
        response = self.client.get(self.jobs_url, {'search': 'Python'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)  # Python job and Data job
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Senior Python Developer', job_titles)
        self.assertIn('Data Scientist', job_titles)  # Has Python in skills
    
    def test_full_text_search_description(self):
        """Test full-text search in job descriptions."""
        response = self.client.get(self.jobs_url, {'search': 'machine learning'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Data Scientist')
    
    def test_full_text_search_company_name(self):
        """Test full-text search in company names."""
        response = self.client.get(self.jobs_url, {'search': 'TechCorp'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Python and JavaScript jobs
        
        for job in response.data['results']:
            self.assertEqual(job['company']['name'], 'TechCorp Inc')
    
    def test_full_text_search_skills(self):
        """Test full-text search in required and preferred skills."""
        response = self.client.get(self.jobs_url, {'search': 'React'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Frontend JavaScript Engineer')
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        # Test with different cases
        test_cases = ['python', 'PYTHON', 'Python', 'pYtHoN']
        
        for search_term in test_cases:
            response = self.client.get(self.jobs_url, {'search': search_term})
            
            self.assertResponseStatus(response, status.HTTP_200_OK)
            self.assertGreaterEqual(response.data['count'], 1)
    
    def test_search_partial_matching(self):
        """Test partial word matching in search."""
        response = self.client.get(self.jobs_url, {'search': 'develop'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)
        
        # Should match "Developer" and "development"
        job_titles = [job['title'] for job in response.data['results']]
        matching_titles = [title for title in job_titles if 'develop' in title.lower()]
        self.assertGreater(len(matching_titles), 0)
    
    def test_search_multiple_terms(self):
        """Test search with multiple terms."""
        response = self.client.get(self.jobs_url, {'search': 'Python Django'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        # Should prioritize jobs that match both terms
        first_result = response.data['results'][0]
        self.assertEqual(first_result['title'], 'Senior Python Developer')
    
    def test_search_with_quotes(self):
        """Test exact phrase search with quotes."""
        response = self.client.get(self.jobs_url, {'search': '"machine learning"'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Data Scientist')
    
    def test_search_ranking_relevance(self):
        """Test that search results are ranked by relevance."""
        response = self.client.get(self.jobs_url, {'search': 'Python'})
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        # Job with "Python" in title should rank higher than job with "Python" in skills
        first_result = response.data['results'][0]
        self.assertEqual(first_result['title'], 'Senior Python Developer')


class ComplexFilteringTestCase(BaseAPIEndpointTestCase):
    """Test complex filtering combinations."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Use the same test data setup as AdvancedJobSearchTestCase
        self.tech_industry = IndustryFactory(name='Technology')
        self.finance_industry = IndustryFactory(name='Finance')
        
        self.fulltime_type = JobTypeFactory(name='Full-time')
        self.remote_type = JobTypeFactory(name='Remote')
        
        self.dev_category = CategoryFactory(name='Development')
        self.design_category = CategoryFactory(name='Design')
        
        self.tech_company = CompanyFactory(name='TechCorp Inc')
        self.finance_company = CompanyFactory(name='FinanceBank LLC')
        
        # Create jobs with specific attributes for filtering
        self.senior_python_job = JobFactory(
            title='Senior Python Developer',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            location='San Francisco, CA',
            salary_min=120000,
            salary_max=160000,
            experience_level='senior',
            is_remote=False,
            is_active=True
        )
        self.senior_python_job.categories.add(self.dev_category)
        
        self.remote_js_job = JobFactory(
            title='Remote JavaScript Developer',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.remote_type,
            location='Remote',
            salary_min=90000,
            salary_max=130000,
            experience_level='mid',
            is_remote=True,
            is_active=True
        )
        self.remote_js_job.categories.add(self.dev_category)
        
        self.finance_analyst_job = JobFactory(
            title='Financial Analyst',
            company=self.finance_company,
            industry=self.finance_industry,
            job_type=self.fulltime_type,
            location='New York, NY',
            salary_min=70000,
            salary_max=100000,
            experience_level='junior',
            is_remote=False,
            is_active=True
        )
        self.finance_analyst_job.categories.add(self.design_category)
    
    def test_filter_by_multiple_industries(self):
        """Test filtering by multiple industries."""
        response = self.client.get(self.jobs_url, {
            'industry': f"{self.tech_industry.pk},{self.finance_industry.pk}"
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All jobs
    
    def test_filter_by_multiple_job_types(self):
        """Test filtering by multiple job types."""
        response = self.client.get(self.jobs_url, {
            'job_type': f"{self.fulltime_type.pk},{self.remote_type.pk}"
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All jobs
    
    def test_filter_by_multiple_categories(self):
        """Test filtering by multiple categories."""
        response = self.client.get(self.jobs_url, {
            'categories': f"{self.dev_category.pk},{self.design_category.pk}"
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All jobs
    
    def test_filter_by_salary_range(self):
        """Test filtering by salary range."""
        response = self.client.get(self.jobs_url, {
            'salary_min': 80000,
            'salary_max': 140000
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should return jobs with overlapping salary ranges
        for job in response.data['results']:
            job_salary_min = float(job['salary_min']) if job['salary_min'] else 0
            job_salary_max = float(job['salary_max']) if job['salary_max'] else float('inf')
            
            # Check if salary ranges overlap
            overlaps = not (job_salary_max < 80000 or job_salary_min > 140000)
            self.assertTrue(overlaps)
    
    def test_filter_by_experience_level(self):
        """Test filtering by experience level."""
        response = self.client.get(self.jobs_url, {
            'experience_level': 'senior'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
    
    def test_filter_by_remote_status(self):
        """Test filtering by remote work status."""
        response = self.client.get(self.jobs_url, {
            'is_remote': 'true'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Remote JavaScript Developer')
    
    def test_filter_by_location_partial_match(self):
        """Test filtering by location with partial matching."""
        response = self.client.get(self.jobs_url, {
            'location': 'San Francisco'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['location'], 'San Francisco, CA')
    
    def test_combined_filters_and_search(self):
        """Test combining multiple filters with search."""
        response = self.client.get(self.jobs_url, {
            'search': 'Developer',
            'industry': self.tech_industry.pk,
            'job_type': self.fulltime_type.pk,
            'experience_level': 'senior'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
    
    def test_filter_with_no_results(self):
        """Test filtering with criteria that match no jobs."""
        response = self.client.get(self.jobs_url, {
            'industry': self.tech_industry.pk,
            'location': 'Nonexistent City',
            'experience_level': 'executive'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_by_company(self):
        """Test filtering by company."""
        response = self.client.get(self.jobs_url, {
            'company': self.tech_company.pk
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        for job in response.data['results']:
            self.assertEqual(job['company']['id'], self.tech_company.pk)
    
    def test_filter_by_date_range(self):
        """Test filtering by creation date range."""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Create a job with specific creation date
        past_date = timezone.now() - timedelta(days=30)
        old_job = JobFactory(
            title='Old Job Posting',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            is_active=True
        )
        old_job.created_at = past_date
        old_job.save()
        
        # Filter for jobs created in the last 7 days
        recent_date = timezone.now() - timedelta(days=7)
        response = self.client.get(self.jobs_url, {
            'created_after': recent_date.isoformat()
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should not include the old job
        job_titles = [job['title'] for job in response.data['results']]
        self.assertNotIn('Old Job Posting', job_titles)


class SearchPerformanceTestCase(BaseAPIEndpointTestCase, PerformanceTestMixin):
    """Test search and filtering performance."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create a large dataset for performance testing
        self.companies = CompanyFactory.create_batch(10)
        self.industries = IndustryFactory.create_batch(5)
        self.job_types = JobTypeFactory.create_batch(4)
        self.categories = CategoryFactory.create_batch(8)
        
        # Create many jobs for performance testing
        self.jobs = []
        for i in range(100):
            job = JobFactory(
                title=f'Job {i}',
                company=self.companies[i % len(self.companies)],
                industry=self.industries[i % len(self.industries)],
                job_type=self.job_types[i % len(self.job_types)],
                is_active=True
            )
            # Add random categories
            job.categories.add(self.categories[i % len(self.categories)])
            self.jobs.append(job)
    
    @override_settings(DEBUG=True)
    def test_search_query_performance(self):
        """Test that search queries are optimized."""
        def search_jobs():
            response = self.client.get(self.jobs_url, {'search': 'Job'})
            return response
        
        # Should use minimal database queries
        self.assertQueryCountLessThan(10, search_jobs)
    
    @override_settings(DEBUG=True)
    def test_filtering_query_performance(self):
        """Test that filtering queries are optimized."""
        def filter_jobs():
            response = self.client.get(self.jobs_url, {
                'industry': self.industries[0].pk,
                'job_type': self.job_types[0].pk,
                'categories': self.categories[0].pk
            })
            return response
        
        # Should use minimal database queries with proper joins
        self.assertQueryCountLessThan(8, filter_jobs)
    
    @override_settings(DEBUG=True)
    def test_pagination_performance(self):
        """Test that pagination doesn't cause N+1 queries."""
        def paginated_jobs():
            response = self.client.get(self.jobs_url, {'page_size': 20})
            return response
        
        # Should use select_related/prefetch_related to avoid N+1 queries
        self.assertQueryCountLessThan(6, paginated_jobs)
    
    def test_large_result_set_performance(self):
        """Test performance with large result sets."""
        import time
        
        start_time = time.time()
        response = self.client.get(self.jobs_url, {'page_size': 50})
        end_time = time.time()
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should complete within reasonable time (adjust threshold as needed)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 2.0, "Query took too long to execute")
    
    def test_complex_search_performance(self):
        """Test performance of complex search with multiple filters."""
        import time
        
        start_time = time.time()
        response = self.client.get(self.jobs_url, {
            'search': 'Job',
            'industry': self.industries[0].pk,
            'job_type': self.job_types[0].pk,
            'categories': self.categories[0].pk,
            'salary_min': 50000,
            'salary_max': 150000,
            'is_remote': 'false'
        })
        end_time = time.time()
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Complex queries should still be reasonably fast
        execution_time = end_time - start_time
        self.assertLess(execution_time, 3.0, "Complex query took too long to execute")


class ApplicationSearchAndFilteringTestCase(BaseAPIEndpointTestCase):
    """Test search and filtering for applications."""
    
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
        
        # Create users and applications
        self.users = UserFactory.create_batch(5)
        self.applications = []
        
        for i, user in enumerate(self.users):
            job = self.job1 if i % 2 == 0 else self.job2
            status = [self.pending_status, self.reviewed_status, self.accepted_status][i % 3]
            
            application = ApplicationFactory(
                user=user,
                job=job,
                status=status,
                cover_letter=f'Cover letter for {job.title} by {user.username}'
            )
            self.applications.append(application)
    
    def test_filter_applications_by_status(self):
        """Test filtering applications by status."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'status': self.pending_status.pk
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Count pending applications
        pending_count = sum(1 for app in self.applications if app.status == self.pending_status)
        self.assertEqual(response.data['count'], pending_count)
        
        for app in response.data['results']:
            self.assertEqual(app['status']['name'], 'pending')
    
    def test_filter_applications_by_job(self):
        """Test filtering applications by job."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'job': self.job1.pk
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Count applications for job1
        job1_count = sum(1 for app in self.applications if app.job == self.job1)
        self.assertEqual(response.data['count'], job1_count)
        
        for app in response.data['results']:
            self.assertEqual(app['job']['id'], self.job1.pk)
    
    def test_filter_applications_by_multiple_statuses(self):
        """Test filtering applications by multiple statuses."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'status': f"{self.pending_status.pk},{self.reviewed_status.pk}"
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should include applications with either status
        for app in response.data['results']:
            self.assertIn(app['status']['name'], ['pending', 'reviewed'])
    
    def test_search_applications_by_cover_letter(self):
        """Test searching applications by cover letter content."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'search': 'Python'
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Should find applications with "Python" in cover letter
        self.assertGreater(response.data['count'], 0)
        
        for app in response.data['results']:
            # Cover letter should contain "Python" or job title should contain "Python"
            contains_python = (
                'Python' in app['cover_letter'] or 
                'Python' in app['job']['title']
            )
            self.assertTrue(contains_python)
    
    def test_combined_application_filters(self):
        """Test combining multiple application filters."""
        self.authenticate_admin()
        
        response = self.client.get(self.applications_url, {
            'job': self.job1.pk,
            'status': self.pending_status.pk
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        for app in response.data['results']:
            self.assertEqual(app['job']['id'], self.job1.pk)
            self.assertEqual(app['status']['name'], 'pending')


class CrossEntitySearchTestCase(BaseAPIEndpointTestCase):
    """Test search functionality across different entities."""
    
    def setUp(self):
        super().setUp()
        
        # Create interconnected test data
        self.tech_company = CompanyFactory(name='TechCorp Solutions')
        self.tech_industry = IndustryFactory(name='Technology')
        self.fulltime_type = JobTypeFactory(name='Full-time')
        self.dev_category = CategoryFactory(name='Software Development')
        
        self.job = JobFactory(
            title='Full Stack Developer',
            description='Looking for a full stack developer with React and Node.js experience',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            required_skills='React, Node.js, JavaScript, MongoDB',
            is_active=True
        )
        self.job.categories.add(self.dev_category)
        
        self.user = UserFactory(username='johndoe', first_name='John', last_name='Doe')
        self.status = ApplicationStatusFactory(name='pending')
        
        self.application = ApplicationFactory(
            user=self.user,
            job=self.job,
            status=self.status,
            cover_letter='I am excited about this full stack developer position at TechCorp'
        )
    
    def test_search_jobs_finds_related_data(self):
        """Test that job search includes related entity data."""
        jobs_url = reverse('jobs:job-list')
        
        # Search by company name
        response = self.client.get(jobs_url, {'search': 'TechCorp'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by industry name
        response = self.client.get(jobs_url, {'search': 'Technology'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by category name
        response = self.client.get(jobs_url, {'search': 'Software'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_search_applications_finds_related_data(self):
        """Test that application search includes related entity data."""
        self.authenticate_admin()
        applications_url = reverse('applications:application-list')
        
        # Search by job title
        response = self.client.get(applications_url, {'search': 'Full Stack'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by company name
        response = self.client.get(applications_url, {'search': 'TechCorp'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Search by applicant name
        response = self.client.get(applications_url, {'search': 'John Doe'})
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_global_search_across_entities(self):
        """Test global search that could span multiple entity types."""
        # This would test a global search endpoint if implemented
        # For now, test that individual entity searches work consistently
        
        search_term = 'TechCorp'
        
        # Search jobs
        jobs_response = self.client.get(reverse('jobs:job-list'), {'search': search_term})
        self.assertResponseStatus(jobs_response, status.HTTP_200_OK)
        
        # Search companies
        companies_response = self.client.get(reverse('jobs:company-list'), {'search': search_term})
        self.assertResponseStatus(companies_response, status.HTTP_200_OK)
        
        # Both should find the same company/related jobs
        self.assertGreater(jobs_response.data['count'], 0)
        self.assertGreater(companies_response.data['count'], 0)