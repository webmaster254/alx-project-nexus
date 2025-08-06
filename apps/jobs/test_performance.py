"""
Performance tests for job database indexes and query optimization.
Tests validate that the created indexes improve query performance.
"""

import time
from django.test import TestCase, TransactionTestCase
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.jobs.models import Job, Company
from apps.categories.models import Industry, JobType, Category
from apps.authentication.models import UserProfile


User = get_user_model()


class JobIndexPerformanceTest(TransactionTestCase):
    """
    Test database index performance for job queries.
    Uses TransactionTestCase to allow raw SQL execution.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_test_data()

    @classmethod
    def setup_test_data(cls):
        """Create test data for performance testing."""
        # Create test user
        cls.user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_admin=True
        )
        
        # Create industries
        cls.tech_industry = Industry.objects.create(
            name='Technology',
            description='Technology and software companies'
        )
        cls.finance_industry = Industry.objects.create(
            name='Finance',
            description='Financial services and banking'
        )
        
        # Create job types
        cls.full_time = JobType.objects.create(
            name='Full-time',
            description='Full-time employment'
        )
        cls.part_time = JobType.objects.create(
            name='Part-time',
            description='Part-time employment'
        )
        
        # Create categories
        cls.backend_category = Category.objects.create(
            name='Backend Development',
            slug='backend-development'
        )
        cls.frontend_category = Category.objects.create(
            name='Frontend Development',
            slug='frontend-development'
        )
        
        # Create companies
        companies = []
        for i in range(10):
            company = Company.objects.create(
                name=f'Test Company {i}',
                description=f'Description for company {i}',
                slug=f'test-company-{i}',
                is_active=True
            )
            companies.append(company)
        
        # Create jobs with varied data for testing
        jobs = []
        locations = ['New York', 'San Francisco', 'London', 'Berlin', 'Remote']
        experience_levels = ['entry', 'junior', 'mid', 'senior', 'lead']
        
        for i in range(100):  # Create 100 jobs for testing
            job = Job.objects.create(
                title=f'Software Engineer {i}',
                description=f'Job description for position {i}',
                company=companies[i % len(companies)],
                location=locations[i % len(locations)],
                is_remote=(i % 5 == 0),  # Every 5th job is remote
                salary_min=50000 + (i * 1000),
                salary_max=80000 + (i * 1000),
                job_type=cls.full_time if i % 2 == 0 else cls.part_time,
                industry=cls.tech_industry if i % 3 == 0 else cls.finance_industry,
                experience_level=experience_levels[i % len(experience_levels)],
                is_active=True,
                is_featured=(i % 10 == 0),  # Every 10th job is featured
                created_by=cls.user,
                created_at=timezone.now() - timedelta(days=i % 30)  # Spread over 30 days
            )
            jobs.append(job)
        
        # Add categories to jobs
        for i, job in enumerate(jobs):
            if i % 2 == 0:
                job.categories.add(cls.backend_category)
            else:
                job.categories.add(cls.frontend_category)

    def measure_query_time(self, query_func):
        """Measure the execution time of a query function."""
        start_time = time.time()
        result = query_func()
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time

    def test_title_search_performance(self):
        """Test performance of title-based searches using indexes."""
        def query_by_title():
            return list(Job.objects.filter(
                title__icontains='Engineer',
                is_active=True
            )[:10])
        
        result, execution_time = self.measure_query_time(query_by_title)
        
        # Verify results
        self.assertGreater(len(result), 0)
        
        # Performance assertion - should complete quickly with index
        self.assertLess(execution_time, 0.5, 
                       f"Title search took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Title search performance: {execution_time:.4f}s for {len(result)} results")

    def test_location_filter_performance(self):
        """Test performance of location-based filtering using indexes."""
        def query_by_location():
            return list(Job.objects.filter(
                location='New York',
                is_active=True
            ).order_by('-created_at')[:10])
        
        result, execution_time = self.measure_query_time(query_by_location)
        
        # Verify results
        self.assertGreater(len(result), 0)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Location filter took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Location filter performance: {execution_time:.4f}s for {len(result)} results")

    def test_composite_filter_performance(self):
        """Test performance of composite filters using multiple indexes."""
        def query_composite():
            return list(Job.objects.filter(
                industry=self.tech_industry,
                job_type=self.full_time,
                location='San Francisco',
                is_active=True
            ).order_by('-created_at')[:10])
        
        result, execution_time = self.measure_query_time(query_composite)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Composite filter took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Composite filter performance: {execution_time:.4f}s for {len(result)} results")

    def test_salary_range_filter_performance(self):
        """Test performance of salary range filtering using indexes."""
        def query_by_salary():
            return list(Job.objects.filter(
                salary_min__gte=60000,
                salary_max__lte=100000,
                is_active=True
            )[:10])
        
        result, execution_time = self.measure_query_time(query_by_salary)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Salary range filter took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Salary range filter performance: {execution_time:.4f}s for {len(result)} results")

    def test_featured_jobs_performance(self):
        """Test performance of featured jobs query using indexes."""
        def query_featured():
            return list(Job.objects.filter(
                is_featured=True,
                is_active=True
            ).order_by('-created_at')[:10])
        
        result, execution_time = self.measure_query_time(query_featured)
        
        # Verify results
        self.assertGreater(len(result), 0)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Featured jobs query took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Featured jobs performance: {execution_time:.4f}s for {len(result)} results")

    def test_remote_jobs_performance(self):
        """Test performance of remote jobs filtering using indexes."""
        def query_remote():
            return list(Job.objects.filter(
                is_remote=True,
                is_active=True
            ).order_by('-created_at')[:10])
        
        result, execution_time = self.measure_query_time(query_remote)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Remote jobs query took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Remote jobs performance: {execution_time:.4f}s for {len(result)} results")

    def test_company_jobs_performance(self):
        """Test performance of company-specific job queries using indexes."""
        company = Company.objects.first()
        
        def query_company_jobs():
            return list(Job.objects.filter(
                company=company,
                is_active=True
            ).order_by('-created_at')[:10])
        
        result, execution_time = self.measure_query_time(query_company_jobs)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Company jobs query took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Company jobs performance: {execution_time:.4f}s for {len(result)} results")

    def test_experience_level_performance(self):
        """Test performance of experience level filtering using indexes."""
        def query_by_experience():
            return list(Job.objects.filter(
                experience_level='senior',
                is_active=True
            )[:10])
        
        result, execution_time = self.measure_query_time(query_by_experience)
        
        # Performance assertion
        self.assertLess(execution_time, 0.5,
                       f"Experience level query took {execution_time:.4f}s, expected < 0.5s")
        
        print(f"Experience level performance: {execution_time:.4f}s for {len(result)} results")

    def test_index_usage_analysis(self):
        """Analyze if indexes are being used by examining query plans."""
        with connection.cursor() as cursor:
            # Test query plan for title search
            cursor.execute("""
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM job 
                WHERE title ILIKE %s AND is_active = true 
                LIMIT 10
            """, ['%Engineer%'])
            
            plan = cursor.fetchall()
            plan_text = '\n'.join([row[0] for row in plan])
            
            # Check if index is being used
            self.assertIn('Index', plan_text, 
                         "Query should use index for title search")
            
            print(f"Title search query plan:\n{plan_text}")

    def test_database_statistics(self):
        """Check database statistics for created indexes."""
        with connection.cursor() as cursor:
            # Check if our custom indexes exist
            cursor.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename IN ('job', 'company') 
                AND indexname LIKE '%_idx'
                ORDER BY indexname
            """)
            
            indexes = cursor.fetchall()
            index_names = [idx[0] for idx in indexes]
            
            # Verify our performance indexes exist
            expected_indexes = [
                'job_title_location_active_idx',
                'job_created_active_idx',
                'job_salary_range_idx',
                'job_experience_level_idx',
                'job_remote_location_idx',
                'job_featured_created_idx',
                'job_industry_type_location_idx',
                'job_company_created_idx',
                'company_name_active_idx',
                'company_slug_active_idx'
            ]
            
            for expected_idx in expected_indexes:
                self.assertIn(expected_idx, index_names,
                             f"Index {expected_idx} should exist")
            
            print(f"Found {len(indexes)} custom indexes:")
            for idx_name, table_name in indexes:
                print(f"  - {idx_name} on {table_name}")


class CompanyIndexPerformanceTest(TransactionTestCase):
    """Test performance of Company model indexes."""

    def setUp(self):
        """Set up test data for company performance tests."""
        # Create companies for testing
        for i in range(50):
            Company.objects.create(
                name=f'Company {i}',
                description=f'Description for company {i}',
                slug=f'company-{i}',
                is_active=(i % 5 != 0)  # Most companies active
            )

    def test_company_name_search_performance(self):
        """Test performance of company name searches."""
        def query_by_name():
            return list(Company.objects.filter(
                name__icontains='Company',
                is_active=True
            )[:10])
        
        start_time = time.time()
        result = query_by_name()
        execution_time = time.time() - start_time
        
        self.assertGreater(len(result), 0)
        self.assertLess(execution_time, 0.5,
                       f"Company name search took {execution_time:.4f}s")
        
        print(f"Company name search performance: {execution_time:.4f}s")

    def test_company_slug_lookup_performance(self):
        """Test performance of company slug lookups."""
        def query_by_slug():
            return Company.objects.filter(
                slug='company-5',  # Use a slug that exists
                is_active=True
            ).first()
        
        start_time = time.time()
        result = query_by_slug()
        execution_time = time.time() - start_time
        
        self.assertIsNotNone(result)
        self.assertLess(execution_time, 0.5,  # More realistic expectation
                       f"Company slug lookup took {execution_time:.4f}s")
        
        print(f"Company slug lookup performance: {execution_time:.4f}s")