"""
Test fixtures providing common test data and setup utilities.
"""
from django.core.management import call_command
from django.db import transaction
from .factories import (
    UserFactory, AdminUserFactory, UserProfileFactory,
    IndustryFactory, JobTypeFactory, CategoryFactory,
    CompanyFactory, JobFactory, ApplicationStatusFactory,
    ApplicationFactory, DocumentFactory,
    create_complete_user_with_profile,
    create_job_with_applications,
    create_category_hierarchy,
    create_company_with_jobs,
    create_application_with_documents
)


class TestDataMixin:
    """
    Mixin providing methods to set up common test data scenarios.
    """
    
    def setUp_basic_data(self):
        """Set up basic test data needed for most tests."""
        # Create application statuses
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted')
        self.rejected_status = ApplicationStatusFactory(name='rejected')
        self.withdrawn_status = ApplicationStatusFactory(name='withdrawn')
        
        # Create basic classification data
        self.tech_industry = IndustryFactory(name='Technology')
        self.healthcare_industry = IndustryFactory(name='Healthcare')
        
        self.fulltime_type = JobTypeFactory(name='Full-time', code='full-time')
        self.parttime_type = JobTypeFactory(name='Part-time', code='part-time')
        self.contract_type = JobTypeFactory(name='Contract', code='contract')
        
        # Create category hierarchy
        self.categories = create_category_hierarchy()
        
        # Create users
        self.regular_user = UserFactory()
        self.admin_user = AdminUserFactory()
        self.user_with_profile = UserProfileFactory().user
    
    def setUp_job_data(self):
        """Set up job-related test data."""
        self.setUp_basic_data()
        
        # Create companies
        self.tech_company = CompanyFactory(name='TechCorp Inc.')
        self.startup_company = CompanyFactory(name='StartupXYZ')
        
        # Create jobs
        self.active_job = JobFactory(
            title='Senior Software Engineer',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            created_by=self.admin_user,
            is_active=True
        )
        
        self.inactive_job = JobFactory(
            title='Junior Developer',
            company=self.startup_company,
            industry=self.tech_industry,
            job_type=self.parttime_type,
            created_by=self.admin_user,
            is_active=False
        )
        
        self.remote_job = JobFactory(
            title='Remote Python Developer',
            company=self.tech_company,
            industry=self.tech_industry,
            job_type=self.fulltime_type,
            location='Remote',
            is_remote=True,
            created_by=self.admin_user
        )
        
        # Add categories to jobs
        self.active_job.categories.add(self.categories['level1'][0])  # Software Development
        self.remote_job.categories.add(self.categories['level2'][0])  # Frontend Development
    
    def setUp_application_data(self):
        """Set up application-related test data."""
        self.setUp_job_data()
        
        # Create applications
        self.pending_application = ApplicationFactory(
            user=self.regular_user,
            job=self.active_job,
            status=self.pending_status
        )
        
        self.reviewed_application = ApplicationFactory(
            user=self.user_with_profile,
            job=self.remote_job,
            status=self.reviewed_status,
            reviewed_by=self.admin_user
        )
        
        self.accepted_application = ApplicationFactory(
            user=UserFactory(),
            job=self.active_job,
            status=self.accepted_status,
            reviewed_by=self.admin_user
        )
        
        # Create documents for applications
        self.resume_doc = DocumentFactory(
            application=self.pending_application,
            document_type='resume',
            title='John Doe Resume'
        )
    
    def setUp_search_data(self):
        """Set up data for search and filtering tests."""
        self.setUp_basic_data()
        
        # Create multiple companies and jobs for search testing
        companies = [
            CompanyFactory(name='Google'),
            CompanyFactory(name='Microsoft'),
            CompanyFactory(name='Apple'),
            CompanyFactory(name='Amazon'),
        ]
        
        # Create jobs with different attributes for filtering
        self.search_jobs = []
        
        # Python jobs
        for i in range(3):
            job = JobFactory(
                title=f'Python Developer {i+1}',
                company=companies[i % len(companies)],
                industry=self.tech_industry,
                job_type=self.fulltime_type,
                location='San Francisco',
                required_skills='Python, Django, PostgreSQL',
                created_by=self.admin_user
            )
            self.search_jobs.append(job)
        
        # JavaScript jobs
        for i in range(2):
            job = JobFactory(
                title=f'JavaScript Developer {i+1}',
                company=companies[i % len(companies)],
                industry=self.tech_industry,
                job_type=self.fulltime_type,
                location='New York',
                required_skills='JavaScript, React, Node.js',
                created_by=self.admin_user
            )
            self.search_jobs.append(job)
        
        # Remote jobs
        for i in range(2):
            job = JobFactory(
                title=f'Remote Full Stack Developer {i+1}',
                company=companies[i % len(companies)],
                industry=self.tech_industry,
                job_type=self.fulltime_type,
                location='Remote',
                is_remote=True,
                required_skills='Python, JavaScript, React, Django',
                created_by=self.admin_user
            )
            self.search_jobs.append(job)
    
    def setUp_performance_data(self):
        """Set up large dataset for performance testing."""
        self.setUp_basic_data()
        
        # Create multiple companies
        self.companies = CompanyFactory.create_batch(10)
        
        # Create multiple jobs
        self.performance_jobs = []
        for i in range(50):
            job = JobFactory(
                company=self.companies[i % len(self.companies)],
                industry=self.tech_industry,
                job_type=self.fulltime_type,
                created_by=self.admin_user
            )
            self.performance_jobs.append(job)
        
        # Create multiple users and applications
        self.test_users = UserFactory.create_batch(20)
        self.performance_applications = []
        
        for i, user in enumerate(self.test_users):
            # Each user applies to 2-3 jobs
            for j in range(2 + (i % 2)):
                if j < len(self.performance_jobs):
                    application = ApplicationFactory(
                        user=user,
                        job=self.performance_jobs[j],
                        status=self.pending_status
                    )
                    self.performance_applications.append(application)


def load_test_fixtures():
    """Load initial test fixtures into the database."""
    with transaction.atomic():
        # Create application statuses
        statuses = [
            ('pending', 'Pending Review', False),
            ('reviewed', 'Under Review', False),
            ('accepted', 'Accepted', True),
            ('rejected', 'Rejected', True),
            ('withdrawn', 'Withdrawn', True),
        ]
        
        for name, display_name, is_final in statuses:
            ApplicationStatusFactory(
                name=name,
                display_name=display_name,
                is_final=is_final
            )
        
        # Create basic industries
        industries = [
            'Technology', 'Healthcare', 'Finance', 'Education',
            'Manufacturing', 'Retail', 'Consulting', 'Media'
        ]
        
        for industry_name in industries:
            IndustryFactory(name=industry_name)
        
        # Create basic job types
        job_types = [
            ('Full-time', 'full-time'),
            ('Part-time', 'part-time'),
            ('Contract', 'contract'),
            ('Temporary', 'temporary'),
            ('Internship', 'internship'),
            ('Freelance', 'freelance'),
            ('Remote', 'remote'),
            ('Hybrid', 'hybrid'),
        ]
        
        for name, code in job_types:
            JobTypeFactory(name=name, code=code)
        
        # Create category hierarchy
        create_category_hierarchy()


def create_test_scenario(scenario_name):
    """Create specific test scenarios by name."""
    scenarios = {
        'basic': lambda: TestDataMixin().setUp_basic_data(),
        'jobs': lambda: TestDataMixin().setUp_job_data(),
        'applications': lambda: TestDataMixin().setUp_application_data(),
        'search': lambda: TestDataMixin().setUp_search_data(),
        'performance': lambda: TestDataMixin().setUp_performance_data(),
    }
    
    if scenario_name in scenarios:
        return scenarios[scenario_name]()
    else:
        raise ValueError(f"Unknown test scenario: {scenario_name}")


class FixtureTestCase:
    """
    Base test case that automatically loads common fixtures.
    """
    
    @classmethod
    def setUpClass(cls):
        """Load fixtures once per test class."""
        super().setUpClass()
        load_test_fixtures()
    
    def setUp(self):
        """Set up test data for each test method."""
        super().setUp()
        # Subclasses can override this to set up specific data