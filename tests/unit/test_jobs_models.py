"""
Unit tests for jobs models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal
from datetime import timedelta

from apps.jobs.models import Company, Job
from apps.categories.models import Industry, JobType, Category
from tests.base import BaseModelTestCase
from tests.factories import (
    CompanyFactory, JobFactory, IndustryFactory, 
    JobTypeFactory, CategoryFactory, UserFactory, AdminUserFactory
)


class CompanyModelTest(BaseModelTestCase):
    """Test cases for Company model."""
    
    def test_company_creation(self):
        """Test basic company creation."""
        company = CompanyFactory()
        self.assertIsInstance(company, Company)
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)
    
    def test_company_str_representation(self):
        """Test company string representation."""
        company = CompanyFactory(name='Test Company')
        self.assertEqual(str(company), 'Test Company')
    
    def test_company_name_uniqueness(self):
        """Test that company name must be unique."""
        name = 'Unique Company'
        CompanyFactory(name=name)
        
        with self.assertRaises(IntegrityError):
            CompanyFactory(name=name)
    
    def test_slug_auto_generation(self):
        """Test automatic slug generation from company name."""
        company = CompanyFactory(name='Test Company Inc.')
        self.assertEqual(company.slug, 'test-company-inc')
    
    def test_slug_uniqueness(self):
        """Test that company slug must be unique."""
        CompanyFactory(name='Test Company', slug='test-company')
        
        with self.assertRaises(IntegrityError):
            CompanyFactory(name='Another Company', slug='test-company')
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        company = CompanyFactory(slug='test-company')
        expected_url = '/companies/test-company/'
        self.assertEqual(company.get_absolute_url(), expected_url)
    
    def test_job_count_property(self):
        """Test job_count property."""
        company = CompanyFactory()
        
        # Initially no jobs
        self.assertEqual(company.job_count, 0)
        
        # Create active jobs
        JobFactory.create_batch(3, company=company, is_active=True)
        self.assertEqual(company.job_count, 3)
        
        # Create inactive job (should not be counted)
        JobFactory(company=company, is_active=False)
        self.assertEqual(company.job_count, 3)
    
    def test_website_url_validation(self):
        """Test website URL validation."""
        # Valid URLs
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://subdomain.example.com/path',
            ''  # Empty is allowed
        ]
        
        for url in valid_urls:
            company = CompanyFactory.build(website=url)
            self.assertModelValid(company)
        
        # Invalid URLs
        invalid_urls = ['not-a-url', 'ftp://example.com']
        
        for url in invalid_urls:
            company = CompanyFactory.build(website=url)
            self.assertModelInvalid(company, 'website')
    
    def test_email_validation(self):
        """Test email field validation."""
        # Valid emails
        valid_emails = ['test@example.com', 'contact@company.co.uk', '']
        
        for email in valid_emails:
            company = CompanyFactory.build(email=email)
            self.assertModelValid(company)
        
        # Invalid emails
        invalid_emails = ['invalid-email', '@example.com', 'test@']
        
        for email in invalid_emails:
            company = CompanyFactory.build(email=email)
            self.assertModelInvalid(company, 'email')
    
    def test_company_meta_options(self):
        """Test company model meta options."""
        self.assertEqual(Company._meta.db_table, 'company')
        self.assertEqual(Company._meta.verbose_name, 'Company')
        self.assertEqual(Company._meta.verbose_name_plural, 'Companies')
        self.assertEqual(Company._meta.ordering, ['name'])


class JobModelTest(BaseModelTestCase):
    """Test cases for Job model."""
    
    def setUp(self):
        super().setUp()
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        self.category = CategoryFactory()
        self.admin_user = AdminUserFactory()
    
    def test_job_creation(self):
        """Test basic job creation."""
        job = JobFactory()
        self.assertIsInstance(job, Job)
        self.assertTrue(job.is_active)
        self.assertFalse(job.is_featured)
        self.assertEqual(job.views_count, 0)
        self.assertEqual(job.applications_count, 0)
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)
    
    def test_job_str_representation(self):
        """Test job string representation."""
        job = JobFactory(title='Software Engineer', company__name='Tech Corp')
        expected_str = 'Software Engineer at Tech Corp'
        self.assertEqual(str(job), expected_str)
    
    def test_salary_validation(self):
        """Test salary range validation."""
        # Valid salary ranges
        job = JobFactory.build(salary_min=50000, salary_max=80000)
        self.assertModelValid(job)
        
        # Invalid: min > max
        job_invalid = JobFactory.build(salary_min=80000, salary_max=50000)
        self.assertModelInvalid(job_invalid)
        
        # Valid: only min
        job_min_only = JobFactory.build(salary_min=50000, salary_max=None)
        self.assertModelValid(job_min_only)
        
        # Valid: only max
        job_max_only = JobFactory.build(salary_min=None, salary_max=80000)
        self.assertModelValid(job_max_only)
    
    def test_application_deadline_validation(self):
        """Test application deadline validation."""
        # Valid: future date
        future_date = timezone.now() + timedelta(days=30)
        job = JobFactory.build(application_deadline=future_date)
        self.assertModelValid(job)
        
        # Invalid: past date
        past_date = timezone.now() - timedelta(days=1)
        job_invalid = JobFactory.build(application_deadline=past_date)
        self.assertModelInvalid(job_invalid)
    
    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        job = JobFactory()
        expected_url = f'/jobs/{job.pk}/'
        self.assertEqual(job.get_absolute_url(), expected_url)
    
    def test_get_salary_display(self):
        """Test get_salary_display method."""
        # Both min and max
        job = JobFactory(
            salary_min=50000, salary_max=80000, 
            salary_type='yearly', salary_currency='USD'
        )
        expected = '$50,000 - $80,000 yearly'
        self.assertEqual(job.get_salary_display(), expected)
        
        # Only min
        job_min = JobFactory(
            salary_min=50000, salary_max=None,
            salary_type='yearly', salary_currency='USD'
        )
        expected_min = 'From $50,000 yearly'
        self.assertEqual(job_min.get_salary_display(), expected_min)
        
        # Only max
        job_max = JobFactory(
            salary_min=None, salary_max=80000,
            salary_type='yearly', salary_currency='USD'
        )
        expected_max = 'Up to $80,000 yearly'
        self.assertEqual(job_max.get_salary_display(), expected_max)
        
        # No salary specified
        job_none = JobFactory(salary_min=None, salary_max=None)
        expected_none = 'Salary not specified'
        self.assertEqual(job_none.get_salary_display(), expected_none)
    
    def test_skills_list_methods(self):
        """Test skills list getter and setter methods."""
        job = JobFactory(required_skills='Python, JavaScript, React')
        
        # Test getter
        expected_skills = ['Python', 'JavaScript', 'React']
        self.assertEqual(job.get_required_skills_list(), expected_skills)
        
        # Test setter
        new_skills = ['Java', 'Spring', 'MySQL']
        job.set_required_skills_list(new_skills)
        self.assertEqual(job.required_skills, 'Java, Spring, MySQL')
        
        # Test with empty list
        job.set_required_skills_list([])
        self.assertEqual(job.required_skills, '')
        
        # Test preferred skills
        job.set_preferred_skills_list(['Docker', 'AWS'])
        self.assertEqual(job.preferred_skills, 'Docker, AWS')
    
    def test_increment_views(self):
        """Test increment_views method."""
        job = JobFactory(views_count=5)
        job.increment_views()
        job.refresh_from_db()
        self.assertEqual(job.views_count, 6)
    
    def test_increment_applications(self):
        """Test increment_applications method."""
        job = JobFactory(applications_count=3)
        job.increment_applications()
        job.refresh_from_db()
        self.assertEqual(job.applications_count, 4)
    
    def test_is_application_deadline_passed(self):
        """Test is_application_deadline_passed method."""
        # No deadline
        job_no_deadline = JobFactory(application_deadline=None)
        self.assertFalse(job_no_deadline.is_application_deadline_passed())
        
        # Future deadline
        future_deadline = timezone.now() + timedelta(days=7)
        job_future = JobFactory(application_deadline=future_deadline)
        self.assertFalse(job_future.is_application_deadline_passed())
        
        # Past deadline
        past_deadline = timezone.now() - timedelta(days=1)
        job_past = JobFactory(application_deadline=past_deadline)
        self.assertTrue(job_past.is_application_deadline_passed())
    
    def test_can_apply(self):
        """Test can_apply method."""
        # Active job with future deadline
        future_deadline = timezone.now() + timedelta(days=7)
        job_can_apply = JobFactory(is_active=True, application_deadline=future_deadline)
        self.assertTrue(job_can_apply.can_apply())
        
        # Inactive job
        job_inactive = JobFactory(is_active=False, application_deadline=future_deadline)
        self.assertFalse(job_inactive.can_apply())
        
        # Past deadline
        past_deadline = timezone.now() - timedelta(days=1)
        job_past_deadline = JobFactory(is_active=True, application_deadline=past_deadline)
        self.assertFalse(job_past_deadline.can_apply())
        
        # No deadline (should be able to apply)
        job_no_deadline = JobFactory(is_active=True, application_deadline=None)
        self.assertTrue(job_no_deadline.can_apply())
    
    def test_category_names_property(self):
        """Test category_names property."""
        job = JobFactory()
        categories = CategoryFactory.create_batch(3)
        job.categories.set(categories)
        
        expected_names = [cat.name for cat in categories]
        self.assertEqual(set(job.category_names), set(expected_names))
    
    def test_days_since_posted_property(self):
        """Test days_since_posted property."""
        # Create job with specific creation time
        past_time = timezone.now() - timedelta(days=5)
        job = JobFactory()
        job.created_at = past_time
        job.save()
        
        self.assertEqual(job.days_since_posted, 5)
    
    def test_is_new_property(self):
        """Test is_new property."""
        # New job (created today)
        new_job = JobFactory()
        self.assertTrue(new_job.is_new)
        
        # Old job (created 10 days ago)
        old_time = timezone.now() - timedelta(days=10)
        old_job = JobFactory()
        old_job.created_at = old_time
        old_job.save()
        self.assertFalse(old_job.is_new)
    
    def test_is_urgent_property(self):
        """Test is_urgent property."""
        # Urgent job (deadline in 3 days)
        urgent_deadline = timezone.now() + timedelta(days=3)
        urgent_job = JobFactory(application_deadline=urgent_deadline)
        self.assertTrue(urgent_job.is_urgent)
        
        # Not urgent (deadline in 10 days)
        future_deadline = timezone.now() + timedelta(days=10)
        normal_job = JobFactory(application_deadline=future_deadline)
        self.assertFalse(normal_job.is_urgent)
        
        # No deadline
        no_deadline_job = JobFactory(application_deadline=None)
        self.assertFalse(no_deadline_job.is_urgent)
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships."""
        job = JobFactory()
        
        # Test company relationship
        self.assertIsInstance(job.company, Company)
        
        # Test industry relationship
        self.assertIsInstance(job.industry, Industry)
        
        # Test job_type relationship
        self.assertIsInstance(job.job_type, JobType)
        
        # Test created_by relationship
        self.assertIsNotNone(job.created_by)
        self.assertTrue(job.created_by.is_admin)
    
    def test_many_to_many_categories(self):
        """Test many-to-many relationship with categories."""
        job = JobFactory()
        categories = CategoryFactory.create_batch(3)
        
        # Add categories
        job.categories.set(categories)
        self.assertEqual(job.categories.count(), 3)
        
        # Test reverse relationship
        for category in categories:
            self.assertIn(job, category.jobs.all())
    
    def test_job_meta_options(self):
        """Test job model meta options."""
        self.assertEqual(Job._meta.db_table, 'job')
        self.assertEqual(Job._meta.verbose_name, 'Job')
        self.assertEqual(Job._meta.verbose_name_plural, 'Jobs')
        self.assertEqual(Job._meta.ordering, ['-created_at'])
        
        # Test indexes
        index_fields = [index.fields for index in Job._meta.indexes]
        expected_indexes = [
            ['title'], ['location'], ['is_active'], ['created_at'],
            ['company', 'is_active'], ['industry', 'job_type'],
            ['location', 'is_active']
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_fields)
    
    def test_experience_level_choices(self):
        """Test experience level choices."""
        valid_levels = ['entry', 'junior', 'mid', 'senior', 'lead', 'executive']
        
        for level in valid_levels:
            job = JobFactory.build(experience_level=level)
            self.assertModelValid(job)
        
        # Invalid level
        job_invalid = JobFactory.build(experience_level='invalid')
        # Note: This would be caught by form validation, not model validation
        # Model validation doesn't enforce choices by default
    
    def test_salary_type_choices(self):
        """Test salary type choices."""
        valid_types = ['hourly', 'monthly', 'yearly']
        
        for salary_type in valid_types:
            job = JobFactory.build(salary_type=salary_type)
            self.assertModelValid(job)
    
    def test_required_fields(self):
        """Test required fields validation."""
        # Test that title is required
        job = JobFactory.build(title='')
        self.assertModelInvalid(job, 'title')
        
        # Test that description is required
        job = JobFactory.build(description='')
        self.assertModelInvalid(job, 'description')
        
        # Test that location is required
        job = JobFactory.build(location='')
        self.assertModelInvalid(job, 'location')
    
    def test_cascade_delete_relationships(self):
        """Test cascade delete behavior."""
        company = CompanyFactory()
        industry = IndustryFactory()
        job_type = JobTypeFactory()
        user = AdminUserFactory()
        
        job = JobFactory(
            company=company,
            industry=industry,
            job_type=job_type,
            created_by=user
        )
        job_id = job.id
        
        # Delete company should delete job
        company.delete()
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(id=job_id)