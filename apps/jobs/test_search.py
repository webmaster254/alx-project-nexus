"""
Tests for full-text search functionality.
Tests PostgreSQL full-text search, ranking, and relevance scoring.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import connection

from apps.jobs.models import Job, Company
from apps.jobs.search import (
    JobSearchManager, CompanySearchManager,
    search_jobs, search_jobs_by_title, search_jobs_by_skills,
    search_jobs_by_location, advanced_job_search,
    search_companies, search_companies_by_name
)
from apps.categories.models import Industry, JobType, Category


User = get_user_model()


class FullTextSearchTestCase(TestCase):
    """Base test case with common setup for search tests."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for search functionality."""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create industries
        cls.tech_industry = Industry.objects.create(
            name='Technology',
            description='Software and technology companies'
        )
        cls.finance_industry = Industry.objects.create(
            name='Finance',
            description='Financial services and banking'
        )
        
        # Create job types
        cls.full_time = JobType.objects.create(
            name='Full-time',
            code='FT',
            description='Full-time employment'
        )
        cls.part_time = JobType.objects.create(
            name='Part-time',
            code='PT',
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
        cls.tech_company = Company.objects.create(
            name='TechCorp Solutions',
            description='Leading technology solutions provider',
            slug='techcorp-solutions',
            is_active=True
        )
        cls.startup_company = Company.objects.create(
            name='InnovateLab Startup',
            description='Innovative startup focused on AI and machine learning',
            slug='innovatelab-startup',
            is_active=True
        )
        cls.finance_company = Company.objects.create(
            name='FinanceFirst Bank',
            description='Premier financial services institution',
            slug='financefirst-bank',
            is_active=True
        )
        
        # Create test jobs with varied content for search testing
        cls.python_job = Job.objects.create(
            title='Senior Python Developer',
            description='We are looking for an experienced Python developer to join our backend team. You will work on scalable web applications using Django and Flask frameworks.',
            company=cls.tech_company,
            location='San Francisco, CA',
            salary_min=90000,
            salary_max=130000,
            job_type=cls.full_time,
            industry=cls.tech_industry,
            experience_level='senior',
            required_skills='Python, Django, PostgreSQL, REST APIs',
            preferred_skills='Docker, Kubernetes, AWS',
            is_active=True,
            created_by=cls.user
        )
        cls.python_job.categories.add(cls.backend_category)
        
        cls.javascript_job = Job.objects.create(
            title='Frontend JavaScript Engineer',
            description='Join our frontend team to build amazing user interfaces with React and TypeScript. Experience with modern JavaScript frameworks required.',
            company=cls.startup_company,
            location='New York, NY',
            salary_min=80000,
            salary_max=120000,
            job_type=cls.full_time,
            industry=cls.tech_industry,
            experience_level='mid',
            required_skills='JavaScript, React, TypeScript, HTML, CSS',
            preferred_skills='Next.js, GraphQL, Jest',
            is_active=True,
            created_by=cls.user
        )
        cls.javascript_job.categories.add(cls.frontend_category)
        
        cls.fullstack_job = Job.objects.create(
            title='Full Stack Developer',
            description='Looking for a versatile full stack developer with experience in both Python backend and React frontend development.',
            company=cls.tech_company,
            location='Remote',
            is_remote=True,
            salary_min=85000,
            salary_max=125000,
            job_type=cls.full_time,
            industry=cls.tech_industry,
            experience_level='mid',
            required_skills='Python, JavaScript, React, Django, PostgreSQL',
            preferred_skills='Docker, AWS, CI/CD',
            is_active=True,
            created_by=cls.user
        )
        cls.fullstack_job.categories.add(cls.backend_category, cls.frontend_category)
        
        cls.data_job = Job.objects.create(
            title='Data Scientist',
            description='We need a data scientist to analyze large datasets and build machine learning models. Experience with Python and statistical analysis required.',
            company=cls.startup_company,
            location='Boston, MA',
            salary_min=95000,
            salary_max=140000,
            job_type=cls.full_time,
            industry=cls.tech_industry,
            experience_level='senior',
            required_skills='Python, Machine Learning, Statistics, Pandas, NumPy',
            preferred_skills='TensorFlow, PyTorch, SQL',
            is_active=True,
            created_by=cls.user
        )
        
        cls.finance_job = Job.objects.create(
            title='Financial Analyst',
            description='Seeking a financial analyst to perform financial modeling and analysis. Strong Excel and analytical skills required.',
            company=cls.finance_company,
            location='Chicago, IL',
            salary_min=70000,
            salary_max=95000,
            job_type=cls.full_time,
            industry=cls.finance_industry,
            experience_level='junior',
            required_skills='Excel, Financial Modeling, Analysis',
            preferred_skills='SQL, Python, Tableau',
            is_active=True,
            created_by=cls.user
        )


class JobFullTextSearchTest(FullTextSearchTestCase):
    """Test job full-text search functionality."""
    
    def test_basic_full_text_search(self):
        """Test basic full-text search functionality."""
        # Search for Python-related jobs
        results = search_jobs('Python')
        
        # Should find Python developer, full stack, and data scientist jobs
        self.assertGreaterEqual(results.count(), 3)
        
        # Check that results are ordered by relevance
        titles = [job.title for job in results]
        self.assertIn('Senior Python Developer', titles)
        self.assertIn('Full Stack Developer', titles)
        self.assertIn('Data Scientist', titles)
    
    def test_search_ranking(self):
        """Test that search results are properly ranked by relevance."""
        results = search_jobs('Python developer')
        
        # The "Senior Python Developer" should rank higher than others
        # because it has both terms in the title
        first_result = results.first()
        self.assertEqual(first_result.title, 'Senior Python Developer')
        
        # Check that search_rank annotation is present
        self.assertTrue(hasattr(first_result, 'search_rank'))
        self.assertGreater(first_result.search_rank, 0)
    
    def test_search_with_filters(self):
        """Test full-text search with additional filters."""
        filters = {
            'industry': self.tech_industry,
            'experience_level': 'senior'
        }
        
        results = search_jobs('Python', filters=filters)
        
        # Should find senior Python jobs in tech industry
        self.assertGreater(results.count(), 0)
        for job in results:
            self.assertEqual(job.industry, self.tech_industry)
            self.assertEqual(job.experience_level, 'senior')
    
    def test_search_no_results(self):
        """Test search with query that should return no results."""
        results = search_jobs('nonexistent technology')
        self.assertEqual(results.count(), 0)
    
    def test_empty_search_query(self):
        """Test search with empty query."""
        results = search_jobs('')
        self.assertEqual(results.count(), 0)
        
        results = search_jobs(None)
        self.assertEqual(results.count(), 0)


class JobTitleSearchTest(FullTextSearchTestCase):
    """Test job title-specific search functionality."""
    
    def test_title_search_exact_match(self):
        """Test title search with exact match."""
        results = search_jobs_by_title('Senior Python Developer')
        
        self.assertGreater(results.count(), 0)
        first_result = results.first()
        self.assertEqual(first_result.title, 'Senior Python Developer')
    
    def test_title_search_partial_match(self):
        """Test title search with partial match."""
        results = search_jobs_by_title('Python')
        
        # Should find jobs with Python in the title
        titles = [job.title for job in results]
        self.assertIn('Senior Python Developer', titles)
    
    def test_title_search_fuzzy_match(self):
        """Test title search with fuzzy matching using trigrams."""
        # Test with slight misspelling
        results = search_jobs_by_title('Pythom Developer')
        
        # Should still find Python developer due to trigram similarity
        self.assertGreater(results.count(), 0)
        
        # Check that similarity annotation is present
        first_result = results.first()
        self.assertTrue(hasattr(first_result, 'title_similarity'))


class JobSkillsSearchTest(FullTextSearchTestCase):
    """Test job skills-based search functionality."""
    
    def test_skills_search_single_skill(self):
        """Test search by single skill."""
        results = search_jobs_by_skills(['Python'])
        
        # Should find all jobs requiring Python
        self.assertGreaterEqual(results.count(), 3)
        
        # All results should mention Python in skills
        for job in results:
            skills_text = f"{job.required_skills} {job.preferred_skills}".lower()
            self.assertIn('python', skills_text)
    
    def test_skills_search_multiple_skills(self):
        """Test search by multiple skills."""
        results = search_jobs_by_skills(['Python', 'Django'])
        
        # Should find jobs requiring both Python and Django
        self.assertGreater(results.count(), 0)
        
        # Check skill match scoring
        first_result = results.first()
        self.assertTrue(hasattr(first_result, 'skill_match_score'))
        self.assertGreater(first_result.skill_match_score, 0)
    
    def test_skills_search_required_vs_preferred(self):
        """Test that required skills score higher than preferred skills."""
        results = search_jobs_by_skills(['Docker'])
        
        # Docker is a preferred skill in some jobs
        self.assertGreater(results.count(), 0)
        
        # Jobs with Docker as required skill should score higher
        for job in results:
            if hasattr(job, 'skill_match_score'):
                if 'docker' in job.required_skills.lower():
                    # Required skills should have higher score
                    self.assertGreaterEqual(job.skill_match_score, 2.0)


class JobLocationSearchTest(FullTextSearchTestCase):
    """Test job location-based search functionality."""
    
    def test_location_search_exact_match(self):
        """Test location search with exact match."""
        results = search_jobs_by_location('San Francisco')
        
        self.assertGreater(results.count(), 0)
        
        # Should find jobs in San Francisco
        locations = [job.location for job in results]
        san_francisco_jobs = [loc for loc in locations if 'San Francisco' in loc]
        self.assertGreater(len(san_francisco_jobs), 0)
    
    def test_location_search_partial_match(self):
        """Test location search with partial match."""
        results = search_jobs_by_location('New York')
        
        self.assertGreater(results.count(), 0)
        
        # Should find jobs in New York
        first_result = results.first()
        self.assertIn('New York', first_result.location)
    
    def test_location_search_includes_remote(self):
        """Test that location search includes remote jobs."""
        results = search_jobs_by_location('California')
        
        # Should include remote jobs even if they don't match location
        remote_jobs = [job for job in results if job.is_remote]
        self.assertGreater(len(remote_jobs), 0)
    
    def test_location_search_fuzzy_match(self):
        """Test location search with fuzzy matching."""
        results = search_jobs_by_location('San Fransisco')  # Misspelled
        
        # Should still find San Francisco jobs due to trigram similarity
        self.assertGreater(results.count(), 0)
        
        # Check similarity annotation
        first_result = results.first()
        self.assertTrue(hasattr(first_result, 'location_similarity'))


class AdvancedJobSearchTest(FullTextSearchTestCase):
    """Test advanced job search combining multiple criteria."""
    
    def test_advanced_search_all_criteria(self):
        """Test advanced search with all criteria specified."""
        results = advanced_job_search(
            query_text='developer',
            title='Python',
            location='San Francisco',
            skills=['Python', 'Django'],
            company='TechCorp',
            filters={'experience_level': 'senior'}
        )
        
        self.assertGreater(results.count(), 0)
        
        # Should find the senior Python developer job
        first_result = results.first()
        self.assertEqual(first_result.title, 'Senior Python Developer')
    
    def test_advanced_search_partial_criteria(self):
        """Test advanced search with some criteria specified."""
        results = advanced_job_search(
            query_text='Python',
            location='Remote'
        )
        
        # Should find remote Python jobs
        self.assertGreater(results.count(), 0)
        
        remote_jobs = [job for job in results if job.is_remote]
        self.assertGreater(len(remote_jobs), 0)
    
    def test_advanced_search_with_filters(self):
        """Test advanced search with additional filters."""
        filters = {
            'industry': self.tech_industry,
            'salary_min': 80000
        }
        
        results = advanced_job_search(
            query_text='developer',
            filters=filters
        )
        
        self.assertGreater(results.count(), 0)
        
        # All results should meet filter criteria
        for job in results:
            self.assertEqual(job.industry, self.tech_industry)
            if job.salary_min:
                self.assertGreaterEqual(job.salary_min, 80000)


class CompanySearchTest(FullTextSearchTestCase):
    """Test company search functionality."""
    
    def test_company_full_text_search(self):
        """Test company full-text search."""
        results = search_companies('technology')
        
        self.assertGreater(results.count(), 0)
        
        # Should find companies with technology in name or description
        company_names = [company.name for company in results]
        self.assertIn('TechCorp Solutions', company_names)
    
    def test_company_name_search(self):
        """Test company name-specific search."""
        results = search_companies_by_name('TechCorp')
        
        self.assertGreater(results.count(), 0)
        
        first_result = results.first()
        self.assertEqual(first_result.name, 'TechCorp Solutions')
    
    def test_company_search_fuzzy_match(self):
        """Test company search with fuzzy matching."""
        results = search_companies_by_name('TekCorp')  # Misspelled
        
        # Should still find TechCorp due to trigram similarity
        self.assertGreater(results.count(), 0)
        
        # Check similarity annotation
        first_result = results.first()
        self.assertTrue(hasattr(first_result, 'name_similarity'))
    
    def test_company_search_ranking(self):
        """Test company search result ranking."""
        results = search_companies('startup innovation')
        
        # Should rank companies with both terms higher
        self.assertGreater(results.count(), 0)
        
        # Check ranking annotations
        first_result = results.first()
        self.assertTrue(hasattr(first_result, 'search_rank'))
        self.assertTrue(hasattr(first_result, 'relevance_score'))


class SearchPerformanceTest(FullTextSearchTestCase):
    """Test search performance and index usage."""
    
    def test_search_uses_indexes(self):
        """Test that search queries use the created indexes."""
        with connection.cursor() as cursor:
            # Test full-text search query plan
            cursor.execute("""
                EXPLAIN (ANALYZE, BUFFERS) 
                SELECT * FROM job 
                WHERE search_vector @@ to_tsquery('english', 'python')
                AND is_active = true
                LIMIT 10
            """)
            
            plan = cursor.fetchall()
            plan_text = '\n'.join([row[0] for row in plan])
            
            # Should use GIN index for search_vector
            self.assertIn('Index', plan_text)
            print(f"Full-text search query plan:\n{plan_text}")
    
    def test_trigram_search_uses_indexes(self):
        """Test that trigram searches use the created indexes."""
        with connection.cursor() as cursor:
            # Test trigram similarity query plan
            cursor.execute("""
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT *, similarity(title, 'python developer') as sim
                FROM job 
                WHERE similarity(title, 'python developer') > 0.2
                ORDER BY sim DESC
                LIMIT 10
            """)
            
            plan = cursor.fetchall()
            plan_text = '\n'.join([row[0] for row in plan])
            
            # Should use GIN trigram index
            self.assertIn('Index', plan_text)
            print(f"Trigram search query plan:\n{plan_text}")
    
    def test_search_vector_updates(self):
        """Test that search vectors are automatically updated."""
        # Create a new job
        new_job = Job.objects.create(
            title='Machine Learning Engineer',
            description='Build and deploy ML models using Python and TensorFlow',
            company=self.tech_company,
            location='Seattle, WA',
            job_type=self.full_time,
            industry=self.tech_industry,
            experience_level='mid',
            required_skills='Python, Machine Learning, TensorFlow',
            is_active=True,
            created_by=self.user
        )
        
        # Search should immediately find the new job
        results = search_jobs('Machine Learning')
        job_titles = [job.title for job in results]
        self.assertIn('Machine Learning Engineer', job_titles)
        
        # Update the job title
        new_job.title = 'Senior ML Engineer'
        new_job.save()
        
        # Search should find the updated title
        results = search_jobs('Senior ML')
        job_titles = [job.title for job in results]
        self.assertIn('Senior ML Engineer', job_titles)