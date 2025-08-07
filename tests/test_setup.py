"""
Test setup verification and basic factory testing.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .base import BaseTestCase, BaseAPITestCase
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
from .fixtures import TestDataMixin, load_test_fixtures

User = get_user_model()


class FactoryTestCase(BaseTestCase):
    """Test that all factories work correctly."""
    
    def test_user_factory(self):
        """Test UserFactory creates valid users."""
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertTrue(user.email)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.check_password('testpass123'))
    
    def test_admin_user_factory(self):
        """Test AdminUserFactory creates admin users."""
        admin = AdminUserFactory()
        self.assertIsInstance(admin, User)
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_user_profile_factory(self):
        """Test UserProfileFactory creates valid profiles."""
        profile = UserProfileFactory()
        self.assertIsNotNone(profile.user)
        self.assertTrue(profile.bio)
        self.assertTrue(profile.location)
        self.assertIsInstance(profile.experience_years, int)
    
    def test_industry_factory(self):
        """Test IndustryFactory creates valid industries."""
        industry = IndustryFactory()
        self.assertTrue(industry.name)
        self.assertTrue(industry.slug)
        self.assertTrue(industry.is_active)
    
    def test_job_type_factory(self):
        """Test JobTypeFactory creates valid job types."""
        job_type = JobTypeFactory()
        self.assertTrue(job_type.name)
        self.assertTrue(job_type.code)
        self.assertTrue(job_type.slug)
        self.assertTrue(job_type.is_active)
    
    def test_category_factory(self):
        """Test CategoryFactory creates valid categories."""
        category = CategoryFactory()
        self.assertTrue(category.name)
        self.assertTrue(category.slug)
        self.assertIsNone(category.parent)
        self.assertTrue(category.is_active)
    
    def test_company_factory(self):
        """Test CompanyFactory creates valid companies."""
        company = CompanyFactory()
        self.assertTrue(company.name)
        self.assertTrue(company.slug)
        self.assertTrue(company.is_active)
        self.assertIsInstance(company.founded_year, int)
    
    def test_job_factory(self):
        """Test JobFactory creates valid jobs."""
        job = JobFactory()
        self.assertTrue(job.title)
        self.assertTrue(job.description)
        self.assertIsNotNone(job.company)
        self.assertIsNotNone(job.job_type)
        self.assertIsNotNone(job.industry)
        self.assertIsNotNone(job.created_by)
        self.assertTrue(job.is_active)
    
    def test_application_status_factory(self):
        """Test ApplicationStatusFactory creates valid statuses."""
        status = ApplicationStatusFactory()
        self.assertTrue(status.name)
        self.assertTrue(status.display_name)
        self.assertIsInstance(status.is_final, bool)
    
    def test_application_factory(self):
        """Test ApplicationFactory creates valid applications."""
        application = ApplicationFactory()
        self.assertIsNotNone(application.user)
        self.assertIsNotNone(application.job)
        self.assertIsNotNone(application.status)
        self.assertTrue(application.applied_at)
    
    def test_document_factory(self):
        """Test DocumentFactory creates valid documents."""
        document = DocumentFactory()
        self.assertIsNotNone(document.application)
        self.assertTrue(document.title)
        self.assertTrue(document.document_type)
        self.assertTrue(document.file)


class FactoryRelationshipTestCase(BaseTestCase):
    """Test factory relationships and constraints."""
    
    def test_user_profile_relationship(self):
        """Test user-profile relationship."""
        user, profile = create_complete_user_with_profile()
        self.assertEqual(profile.user, user)
        self.assertEqual(user.profile, profile)
    
    def test_job_application_relationship(self):
        """Test job-application relationship."""
        job, applications = create_job_with_applications(num_applications=3)
        self.assertEqual(len(applications), 3)
        for application in applications:
            self.assertEqual(application.job, job)
        self.assertEqual(job.applications.count(), 3)
    
    def test_category_hierarchy(self):
        """Test category hierarchy creation."""
        categories = create_category_hierarchy()
        
        # Check root categories
        self.assertEqual(len(categories['root']), 2)
        for category in categories['root']:
            self.assertIsNone(category.parent)
        
        # Check level 1 categories
        self.assertEqual(len(categories['level1']), 4)
        for category in categories['level1']:
            self.assertIsNotNone(category.parent)
            self.assertIn(category.parent, categories['root'])
        
        # Check level 2 categories
        self.assertEqual(len(categories['level2']), 2)
        for category in categories['level2']:
            self.assertIsNotNone(category.parent)
            self.assertIn(category.parent, categories['level1'])
    
    def test_company_jobs_relationship(self):
        """Test company-jobs relationship."""
        company, jobs = create_company_with_jobs(num_jobs=5)
        self.assertEqual(len(jobs), 5)
        for job in jobs:
            self.assertEqual(job.company, company)
        self.assertEqual(company.jobs.count(), 5)
    
    def test_application_documents_relationship(self):
        """Test application-documents relationship."""
        application, documents = create_application_with_documents()
        self.assertEqual(len(documents), 2)
        for document in documents:
            self.assertEqual(document.application, application)
        self.assertEqual(application.documents.count(), 2)
    
    def test_unique_constraints(self):
        """Test unique constraints are respected."""
        from django.db import IntegrityError, transaction
        from django.core.exceptions import ValidationError
        
        # Test user email uniqueness
        user1 = UserFactory(email='test@example.com')
        try:
            with transaction.atomic():
                UserFactory(email='test@example.com')
            self.fail("Expected IntegrityError was not raised")
        except IntegrityError:
            pass  # Expected behavior
        
        # Test application uniqueness (user-job combination)
        job = JobFactory()
        user = UserFactory()
        ApplicationFactory(user=user, job=job)
        
        # This should raise ValidationError due to model validation
        with self.assertRaises(ValidationError):
            ApplicationFactory(user=user, job=job)


class TestDataMixinTestCase(BaseTestCase, TestDataMixin):
    """Test the TestDataMixin functionality."""
    
    def test_setup_basic_data(self):
        """Test basic data setup."""
        self.setUp_basic_data()
        
        # Check application statuses
        self.assertIsNotNone(self.pending_status)
        self.assertIsNotNone(self.reviewed_status)
        self.assertIsNotNone(self.accepted_status)
        self.assertIsNotNone(self.rejected_status)
        self.assertIsNotNone(self.withdrawn_status)
        
        # Check industries and job types
        self.assertIsNotNone(self.tech_industry)
        self.assertIsNotNone(self.healthcare_industry)
        self.assertIsNotNone(self.fulltime_type)
        self.assertIsNotNone(self.parttime_type)
        self.assertIsNotNone(self.contract_type)
        
        # Check users
        self.assertIsNotNone(self.regular_user)
        self.assertIsNotNone(self.admin_user)
        self.assertIsNotNone(self.user_with_profile)
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.regular_user.is_admin)
    
    def test_setup_job_data(self):
        """Test job data setup."""
        self.setUp_job_data()
        
        # Check companies
        self.assertIsNotNone(self.tech_company)
        self.assertIsNotNone(self.startup_company)
        
        # Check jobs
        self.assertIsNotNone(self.active_job)
        self.assertIsNotNone(self.inactive_job)
        self.assertIsNotNone(self.remote_job)
        
        self.assertTrue(self.active_job.is_active)
        self.assertFalse(self.inactive_job.is_active)
        self.assertTrue(self.remote_job.is_remote)
        
        # Check job categories
        self.assertTrue(self.active_job.categories.exists())
        self.assertTrue(self.remote_job.categories.exists())
    
    def test_setup_application_data(self):
        """Test application data setup."""
        self.setUp_application_data()
        
        # Check applications
        self.assertIsNotNone(self.pending_application)
        self.assertIsNotNone(self.reviewed_application)
        self.assertIsNotNone(self.accepted_application)
        
        self.assertEqual(self.pending_application.status.name, 'pending')
        self.assertEqual(self.reviewed_application.status.name, 'reviewed')
        self.assertEqual(self.accepted_application.status.name, 'accepted')
        
        # Check documents
        self.assertIsNotNone(self.resume_doc)
        self.assertEqual(self.resume_doc.document_type, 'resume')
    
    def test_setup_search_data(self):
        """Test search data setup."""
        self.setUp_search_data()
        
        # Check search jobs
        self.assertEqual(len(self.search_jobs), 7)  # 3 Python + 2 JavaScript + 2 Remote
        
        # Check job distribution
        python_jobs = [job for job in self.search_jobs if 'Python' in job.title]
        js_jobs = [job for job in self.search_jobs if 'JavaScript' in job.title]
        remote_jobs = [job for job in self.search_jobs if job.is_remote]
        explicit_remote_jobs = [job for job in self.search_jobs if 'Remote' in job.title]
        
        self.assertEqual(len(python_jobs), 3)
        self.assertEqual(len(js_jobs), 2)
        self.assertEqual(len(explicit_remote_jobs), 2)  # Check explicitly created remote jobs
        self.assertGreaterEqual(len(remote_jobs), 2)  # At least 2 remote jobs (could be more due to random factor)
    
    def test_setup_performance_data(self):
        """Test performance data setup."""
        self.setUp_performance_data()
        
        # Check data volumes
        self.assertEqual(len(self.companies), 10)
        self.assertEqual(len(self.performance_jobs), 50)
        self.assertEqual(len(self.test_users), 20)
        self.assertGreater(len(self.performance_applications), 30)  # At least 2 per user


class FixtureLoadingTestCase(BaseTestCase):
    """Test fixture loading functionality."""
    
    def test_load_test_fixtures(self):
        """Test that fixtures load correctly."""
        # Clear existing data
        from apps.applications.models import ApplicationStatus
        from apps.categories.models import Industry, JobType
        
        ApplicationStatus.objects.all().delete()
        Industry.objects.all().delete()
        JobType.objects.all().delete()
        
        # Load fixtures
        load_test_fixtures()
        
        # Check that data was created
        self.assertEqual(ApplicationStatus.objects.count(), 5)
        self.assertGreater(Industry.objects.count(), 5)
        self.assertGreater(JobType.objects.count(), 5)
        
        # Check specific statuses
        self.assertTrue(ApplicationStatus.objects.filter(name='pending').exists())
        self.assertTrue(ApplicationStatus.objects.filter(name='accepted').exists())
        
        # Check specific industries
        self.assertTrue(Industry.objects.filter(name='Technology').exists())
        self.assertTrue(Industry.objects.filter(name='Healthcare').exists())
        
        # Check specific job types
        self.assertTrue(JobType.objects.filter(code='full-time').exists())
        self.assertTrue(JobType.objects.filter(code='part-time').exists())


class BaseAPITestCaseTestCase(BaseAPITestCase):
    """Test the base API test case functionality."""
    
    def test_authentication_methods(self):
        """Test authentication helper methods."""
        # Test user authentication
        token = self.authenticate_user()
        self.assertIsNotNone(token)
        
        # Test admin authentication
        admin_token = self.authenticate_admin()
        self.assertIsNotNone(admin_token)
        self.assertNotEqual(token, admin_token)
        
        # Test unauthentication
        self.unauthenticate()
        # Should not have authorization header
        self.assertNotIn('HTTP_AUTHORIZATION', self.client.defaults)
    
    def test_response_assertion_methods(self):
        """Test response assertion helper methods."""
        from django.http import JsonResponse
        
        # Create mock responses
        success_response = JsonResponse({'key': 'value'}, status=200)
        success_response.data = {'key': 'value'}
        
        error_response = JsonResponse({'error': 'Not found'}, status=404)
        error_response.data = {'error': 'Not found'}
        
        # Test status assertions
        self.assertResponseStatus(success_response, 200)
        self.assertResponseStatus(error_response, 404)
        
        # Test key assertions
        self.assertResponseHasKeys(success_response, ['key'])
        self.assertResponseDoesNotHaveKeys(success_response, ['missing_key'])


class BaseTestCaseTestCase(BaseTestCase):
    """Test the base test case functionality."""
    
    def test_file_creation_methods(self):
        """Test file creation helper methods."""
        # Test image creation
        image_file = self.create_test_image('test.jpg')
        self.assertEqual(image_file.name, 'test.jpg')
        self.assertEqual(image_file.content_type, 'image/jpeg')
        
        # Test PDF creation
        pdf_file = self.create_test_pdf('test.pdf')
        self.assertEqual(pdf_file.name, 'test.pdf')
        self.assertEqual(pdf_file.content_type, 'application/pdf')
    
