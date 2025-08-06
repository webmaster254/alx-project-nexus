from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from .models import Company


class CompanyModelTest(TestCase):
    """Test cases for the Company model."""

    def setUp(self):
        """Set up test data."""
        self.company_data = {
            'name': 'Test Company Inc.',
            'description': 'A test company for software development',
            'website': 'https://testcompany.com',
            'email': 'contact@testcompany.com',
            'phone': '+1-555-123-4567',
            'address': '123 Test Street, Test City, TC 12345',
            'founded_year': 2020,
            'employee_count': '50-100'
        }

    def test_create_company(self):
        """Test creating a company with all fields."""
        company = Company.objects.create(**self.company_data)
        
        self.assertEqual(company.name, 'Test Company Inc.')
        self.assertEqual(company.description, 'A test company for software development')
        self.assertEqual(company.website, 'https://testcompany.com')
        self.assertEqual(company.email, 'contact@testcompany.com')
        self.assertEqual(company.phone, '+1-555-123-4567')
        self.assertEqual(company.address, '123 Test Street, Test City, TC 12345')
        self.assertEqual(company.founded_year, 2020)
        self.assertEqual(company.employee_count, '50-100')
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)

    def test_create_company_minimal(self):
        """Test creating a company with only required fields."""
        company = Company.objects.create(name='Minimal Company')
        
        self.assertEqual(company.name, 'Minimal Company')
        self.assertEqual(company.description, '')
        self.assertEqual(company.website, '')
        self.assertEqual(company.email, '')
        self.assertEqual(company.phone, '')
        self.assertEqual(company.address, '')
        self.assertIsNone(company.founded_year)
        self.assertEqual(company.employee_count, '')
        self.assertTrue(company.is_active)

    def test_company_name_unique_constraint(self):
        """Test that company name must be unique."""
        Company.objects.create(name='Unique Company')
        
        with self.assertRaises(IntegrityError):
            Company.objects.create(name='Unique Company')

    def test_company_name_max_length(self):
        """Test company name max length validation."""
        long_name = 'A' * 201  # Exceeds max_length of 200
        company = Company(name=long_name)
        
        with self.assertRaises(ValidationError):
            company.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from company name."""
        company = Company.objects.create(name='Test Company Inc.')
        expected_slug = slugify('Test Company Inc.')
        self.assertEqual(company.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        Company.objects.create(name='Test Company', slug='test-company')
        
        with self.assertRaises(IntegrityError):
            Company.objects.create(name='Another Company', slug='test-company')

    def test_custom_slug(self):
        """Test creating company with custom slug."""
        company = Company.objects.create(
            name='Test Company',
            slug='custom-slug'
        )
        self.assertEqual(company.slug, 'custom-slug')

    def test_website_url_validation(self):
        """Test website URL validation."""
        # Valid URLs
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://www.example.com',
            'https://subdomain.example.com'
        ]
        
        for url in valid_urls:
            company_data = self.company_data.copy()
            company_data['website'] = url
            company_data['name'] = f'Company {url}'
            company = Company(**company_data)
            try:
                company.full_clean()
            except ValidationError:
                self.fail(f"Valid URL {url} failed validation")

        # Invalid URLs
        invalid_urls = ['not-a-url', 'just-text', 'http://']
        
        for url in invalid_urls:
            company_data = self.company_data.copy()
            company_data['website'] = url
            company = Company(**company_data)
            with self.assertRaises(ValidationError):
                company.full_clean()

    def test_email_validation(self):
        """Test email field validation."""
        # Valid emails
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.co.uk'
        ]
        
        for email in valid_emails:
            company_data = self.company_data.copy()
            company_data['email'] = email
            company_data['name'] = f'Company {email}'
            company = Company(**company_data)
            try:
                company.full_clean()
            except ValidationError:
                self.fail(f"Valid email {email} failed validation")

        # Invalid emails
        invalid_emails = ['not-an-email', '@example.com', 'user@']
        
        for email in invalid_emails:
            company_data = self.company_data.copy()
            company_data['email'] = email
            company = Company(**company_data)
            with self.assertRaises(ValidationError):
                company.full_clean()

    def test_str_representation(self):
        """Test string representation of company."""
        company = Company.objects.create(name='Test Company')
        self.assertEqual(str(company), 'Test Company')

    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        company = Company.objects.create(name='Test Company')
        expected_url = f"/companies/{company.slug}/"
        self.assertEqual(company.get_absolute_url(), expected_url)

    def test_job_count_property(self):
        """Test job_count property with Job model implemented."""
        company = Company.objects.create(name='Test Company')
        # Should return 0 when no jobs exist
        self.assertEqual(company.job_count, 0)

    def test_is_active_field(self):
        """Test is_active field functionality."""
        company = Company.objects.create(name='Test Company')
        self.assertTrue(company.is_active)
        
        company.is_active = False
        company.save()
        company.refresh_from_db()
        self.assertFalse(company.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        Company.objects.create(name='Zebra Company')
        Company.objects.create(name='Alpha Company')
        Company.objects.create(name='Beta Company')
        
        companies = list(Company.objects.all())
        company_names = [company.name for company in companies]
        
        self.assertEqual(company_names, ['Alpha Company', 'Beta Company', 'Zebra Company'])

    def test_phone_max_length(self):
        """Test phone field max length."""
        long_phone = '1' * 21  # Exceeds max_length of 20
        company = Company(name='Test Company', phone=long_phone)
        
        with self.assertRaises(ValidationError):
            company.full_clean()

    def test_employee_count_max_length(self):
        """Test employee_count field max length."""
        long_count = 'A' * 51  # Exceeds max_length of 50
        company = Company(name='Test Company', employee_count=long_count)
        
        with self.assertRaises(ValidationError):
            company.full_clean()


from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.categories.models import Industry, JobType, Category
from .models import Job

User = get_user_model()


class JobModelTest(TestCase):
    """Test cases for the Job model."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Test Company',
            description='A test company'
        )
        
        # Create test industry
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        
        # Create test job type
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            description='Full-time employment'
        )
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        self.category2 = Category.objects.create(
            name='Backend Development',
            description='Backend development jobs',
            parent=self.category1
        )
        
        # Base job data
        self.job_data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for a senior software engineer...',
            'summary': 'Senior software engineer position',
            'company': self.company,
            'location': 'San Francisco, CA',
            'salary_min': Decimal('80000.00'),
            'salary_max': Decimal('120000.00'),
            'salary_type': 'yearly',
            'salary_currency': 'USD',
            'job_type': self.job_type,
            'industry': self.industry,
            'experience_level': 'senior',
            'required_skills': 'Python, Django, PostgreSQL',
            'preferred_skills': 'React, Docker, AWS',
            'created_by': self.user
        }

    def test_create_job_with_all_fields(self):
        """Test creating a job with all fields."""
        future_date = timezone.now() + timedelta(days=30)
        job_data = self.job_data.copy()
        job_data.update({
            'is_remote': True,
            'application_deadline': future_date,
            'external_url': 'https://company.com/apply',
            'is_featured': True
        })
        
        job = Job.objects.create(**job_data)
        job.categories.add(self.category1, self.category2)
        
        self.assertEqual(job.title, 'Senior Software Engineer')
        self.assertEqual(job.description, 'We are looking for a senior software engineer...')
        self.assertEqual(job.summary, 'Senior software engineer position')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.location, 'San Francisco, CA')
        self.assertTrue(job.is_remote)
        self.assertEqual(job.salary_min, Decimal('80000.00'))
        self.assertEqual(job.salary_max, Decimal('120000.00'))
        self.assertEqual(job.salary_type, 'yearly')
        self.assertEqual(job.salary_currency, 'USD')
        self.assertEqual(job.job_type, self.job_type)
        self.assertEqual(job.industry, self.industry)
        self.assertEqual(job.experience_level, 'senior')
        self.assertEqual(job.required_skills, 'Python, Django, PostgreSQL')
        self.assertEqual(job.preferred_skills, 'React, Docker, AWS')
        self.assertEqual(job.application_deadline, future_date)
        self.assertEqual(job.external_url, 'https://company.com/apply')
        self.assertTrue(job.is_active)
        self.assertTrue(job.is_featured)
        self.assertEqual(job.views_count, 0)
        self.assertEqual(job.applications_count, 0)
        self.assertEqual(job.created_by, self.user)
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)
        self.assertIn(self.category1, job.categories.all())
        self.assertIn(self.category2, job.categories.all())

    def test_create_job_minimal_fields(self):
        """Test creating a job with only required fields."""
        minimal_data = {
            'title': 'Software Engineer',
            'description': 'Software engineer position',
            'company': self.company,
            'location': 'Remote',
            'job_type': self.job_type,
            'industry': self.industry,
            'created_by': self.user
        }
        
        job = Job.objects.create(**minimal_data)
        
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.description, 'Software engineer position')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.location, 'Remote')
        self.assertEqual(job.job_type, self.job_type)
        self.assertEqual(job.industry, self.industry)
        self.assertEqual(job.created_by, self.user)
        self.assertEqual(job.experience_level, 'mid')  # default value
        self.assertEqual(job.salary_type, 'yearly')  # default value
        self.assertEqual(job.salary_currency, 'USD')  # default value
        self.assertTrue(job.is_active)  # default value
        self.assertFalse(job.is_featured)  # default value
        self.assertFalse(job.is_remote)  # default value

    def test_job_title_max_length(self):
        """Test job title max length validation."""
        long_title = 'A' * 201  # Exceeds max_length of 200
        job_data = self.job_data.copy()
        job_data['title'] = long_title
        job = Job(**job_data)
        
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_job_location_max_length(self):
        """Test job location max length validation."""
        long_location = 'A' * 201  # Exceeds max_length of 200
        job_data = self.job_data.copy()
        job_data['location'] = long_location
        job = Job(**job_data)
        
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_salary_validation_min_greater_than_max(self):
        """Test salary validation when min is greater than max."""
        job_data = self.job_data.copy()
        job_data['salary_min'] = Decimal('120000.00')
        job_data['salary_max'] = Decimal('80000.00')
        job = Job(**job_data)
        
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_salary_validation_negative_values(self):
        """Test salary validation with negative values."""
        job_data = self.job_data.copy()
        job_data['salary_min'] = Decimal('-1000.00')
        job = Job(**job_data)
        
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_application_deadline_validation_past_date(self):
        """Test application deadline validation with past date."""
        past_date = timezone.now() - timedelta(days=1)
        job_data = self.job_data.copy()
        job_data['application_deadline'] = past_date
        job = Job(**job_data)
        
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_application_deadline_validation_future_date(self):
        """Test application deadline validation with future date."""
        future_date = timezone.now() + timedelta(days=30)
        job_data = self.job_data.copy()
        job_data['application_deadline'] = future_date
        job = Job(**job_data)
        
        try:
            job.full_clean()
        except ValidationError:
            self.fail("Future application deadline should be valid")

    def test_str_representation(self):
        """Test string representation of job."""
        job = Job.objects.create(**self.job_data)
        expected_str = f"{job.title} at {job.company.name}"
        self.assertEqual(str(job), expected_str)

    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        job = Job.objects.create(**self.job_data)
        expected_url = f"/jobs/{job.pk}/"
        self.assertEqual(job.get_absolute_url(), expected_url)

    def test_get_salary_display_full_range(self):
        """Test get_salary_display with full salary range."""
        job = Job.objects.create(**self.job_data)
        expected_display = "$80,000 - $120,000 yearly"
        self.assertEqual(job.get_salary_display(), expected_display)

    def test_get_salary_display_min_only(self):
        """Test get_salary_display with minimum salary only."""
        job_data = self.job_data.copy()
        job_data['salary_max'] = None
        job = Job.objects.create(**job_data)
        expected_display = "From $80,000 yearly"
        self.assertEqual(job.get_salary_display(), expected_display)

    def test_get_salary_display_max_only(self):
        """Test get_salary_display with maximum salary only."""
        job_data = self.job_data.copy()
        job_data['salary_min'] = None
        job = Job.objects.create(**job_data)
        expected_display = "Up to $120,000 yearly"
        self.assertEqual(job.get_salary_display(), expected_display)

    def test_get_salary_display_no_salary(self):
        """Test get_salary_display with no salary information."""
        job_data = self.job_data.copy()
        job_data['salary_min'] = None
        job_data['salary_max'] = None
        job = Job.objects.create(**job_data)
        expected_display = "Salary not specified"
        self.assertEqual(job.get_salary_display(), expected_display)

    def test_get_salary_display_different_currency(self):
        """Test get_salary_display with different currency."""
        job_data = self.job_data.copy()
        job_data['salary_currency'] = 'EUR'
        job = Job.objects.create(**job_data)
        expected_display = "€80,000 - €120,000 yearly"
        self.assertEqual(job.get_salary_display(), expected_display)

    def test_get_required_skills_list(self):
        """Test get_required_skills_list method."""
        job = Job.objects.create(**self.job_data)
        expected_skills = ['Python', 'Django', 'PostgreSQL']
        self.assertEqual(job.get_required_skills_list(), expected_skills)

    def test_get_preferred_skills_list(self):
        """Test get_preferred_skills_list method."""
        job = Job.objects.create(**self.job_data)
        expected_skills = ['React', 'Docker', 'AWS']
        self.assertEqual(job.get_preferred_skills_list(), expected_skills)

    def test_set_required_skills_list(self):
        """Test set_required_skills_list method."""
        job = Job.objects.create(**self.job_data)
        new_skills = ['Java', 'Spring', 'MySQL']
        job.set_required_skills_list(new_skills)
        self.assertEqual(job.required_skills, 'Java, Spring, MySQL')
        self.assertEqual(job.get_required_skills_list(), new_skills)

    def test_set_preferred_skills_list(self):
        """Test set_preferred_skills_list method."""
        job = Job.objects.create(**self.job_data)
        new_skills = ['Vue.js', 'Kubernetes', 'GCP']
        job.set_preferred_skills_list(new_skills)
        self.assertEqual(job.preferred_skills, 'Vue.js, Kubernetes, GCP')
        self.assertEqual(job.get_preferred_skills_list(), new_skills)

    def test_increment_views(self):
        """Test increment_views method."""
        job = Job.objects.create(**self.job_data)
        initial_views = job.views_count
        
        job.increment_views()
        job.refresh_from_db()
        
        self.assertEqual(job.views_count, initial_views + 1)

    def test_increment_applications(self):
        """Test increment_applications method."""
        job = Job.objects.create(**self.job_data)
        initial_applications = job.applications_count
        
        job.increment_applications()
        job.refresh_from_db()
        
        self.assertEqual(job.applications_count, initial_applications + 1)

    def test_is_application_deadline_passed_no_deadline(self):
        """Test is_application_deadline_passed with no deadline."""
        job = Job.objects.create(**self.job_data)
        self.assertFalse(job.is_application_deadline_passed())

    def test_is_application_deadline_passed_future_deadline(self):
        """Test is_application_deadline_passed with future deadline."""
        future_date = timezone.now() + timedelta(days=30)
        job_data = self.job_data.copy()
        job_data['application_deadline'] = future_date
        job = Job.objects.create(**job_data)
        self.assertFalse(job.is_application_deadline_passed())

    def test_is_application_deadline_passed_past_deadline(self):
        """Test is_application_deadline_passed with past deadline."""
        # Create job first, then update deadline to past using update() to bypass validation
        job = Job.objects.create(**self.job_data)
        past_date = timezone.now() - timedelta(days=1)
        Job.objects.filter(pk=job.pk).update(application_deadline=past_date)
        job.refresh_from_db()
        self.assertTrue(job.is_application_deadline_passed())

    def test_can_apply_active_job_no_deadline(self):
        """Test can_apply for active job with no deadline."""
        job = Job.objects.create(**self.job_data)
        self.assertTrue(job.can_apply())

    def test_can_apply_inactive_job(self):
        """Test can_apply for inactive job."""
        job_data = self.job_data.copy()
        job_data['is_active'] = False
        job = Job.objects.create(**job_data)
        self.assertFalse(job.can_apply())

    def test_can_apply_deadline_passed(self):
        """Test can_apply when deadline has passed."""
        job = Job.objects.create(**self.job_data)
        past_date = timezone.now() - timedelta(days=1)
        # Use update() to bypass validation
        Job.objects.filter(pk=job.pk).update(application_deadline=past_date)
        job.refresh_from_db()
        self.assertFalse(job.can_apply())

    def test_category_names_property(self):
        """Test category_names property."""
        job = Job.objects.create(**self.job_data)
        job.categories.add(self.category1, self.category2)
        
        expected_names = ['Software Development', 'Backend Development']
        self.assertEqual(sorted(job.category_names), sorted(expected_names))

    def test_days_since_posted_property(self):
        """Test days_since_posted property."""
        job = Job.objects.create(**self.job_data)
        # Should be 0 for newly created job
        self.assertEqual(job.days_since_posted, 0)

    def test_is_new_property(self):
        """Test is_new property."""
        job = Job.objects.create(**self.job_data)
        # Should be True for newly created job
        self.assertTrue(job.is_new)

    def test_is_urgent_property_no_deadline(self):
        """Test is_urgent property with no deadline."""
        job = Job.objects.create(**self.job_data)
        self.assertFalse(job.is_urgent)

    def test_is_urgent_property_far_deadline(self):
        """Test is_urgent property with deadline far in future."""
        future_date = timezone.now() + timedelta(days=30)
        job_data = self.job_data.copy()
        job_data['application_deadline'] = future_date
        job = Job.objects.create(**job_data)
        self.assertFalse(job.is_urgent)

    def test_is_urgent_property_near_deadline(self):
        """Test is_urgent property with deadline within 7 days."""
        near_future_date = timezone.now() + timedelta(days=5)
        job_data = self.job_data.copy()
        job_data['application_deadline'] = near_future_date
        job = Job.objects.create(**job_data)
        self.assertTrue(job.is_urgent)

    def test_job_relationships(self):
        """Test job model relationships."""
        job = Job.objects.create(**self.job_data)
        job.categories.add(self.category1, self.category2)
        
        # Test company relationship
        self.assertEqual(job.company, self.company)
        self.assertIn(job, self.company.jobs.all())
        
        # Test industry relationship
        self.assertEqual(job.industry, self.industry)
        self.assertIn(job, self.industry.jobs.all())
        
        # Test job_type relationship
        self.assertEqual(job.job_type, self.job_type)
        self.assertIn(job, self.job_type.jobs.all())
        
        # Test categories relationship
        self.assertIn(self.category1, job.categories.all())
        self.assertIn(self.category2, job.categories.all())
        self.assertIn(job, self.category1.jobs.all())
        self.assertIn(job, self.category2.jobs.all())
        
        # Test user relationship
        self.assertEqual(job.created_by, self.user)
        self.assertIn(job, self.user.created_jobs.all())

    def test_job_ordering(self):
        """Test job model ordering by created_at descending."""
        # Create jobs with slight time difference
        job1 = Job.objects.create(title='First Job', **{k: v for k, v in self.job_data.items() if k != 'title'})
        job2 = Job.objects.create(title='Second Job', **{k: v for k, v in self.job_data.items() if k != 'title'})
        job3 = Job.objects.create(title='Third Job', **{k: v for k, v in self.job_data.items() if k != 'title'})
        
        jobs = list(Job.objects.all())
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(jobs[0], job3)
        self.assertEqual(jobs[1], job2)
        self.assertEqual(jobs[2], job1)

    def test_job_indexes_exist(self):
        """Test that database indexes are properly defined."""
        # This test verifies that the Meta.indexes are defined
        # The actual index creation is tested during migrations
        job_meta = Job._meta
        index_fields = []
        for index in job_meta.indexes:
            index_fields.extend(index.fields)
        
        expected_fields = [
            'title', 'location', 'is_active', 'created_at',
            'company', 'industry', 'job_type'
        ]
        
        for field in expected_fields:
            self.assertIn(field, index_fields)

    def test_updated_by_field(self):
        """Test updated_by field functionality."""
        job = Job.objects.create(**self.job_data)
        self.assertIsNone(job.updated_by)
        
        # Create another user for updating
        update_user = User.objects.create_user(
            username='updateuser',
            email='update@example.com',
            password='updatepass123'
        )
        
        job.updated_by = update_user
        job.save()
        job.refresh_from_db()
        
        self.assertEqual(job.updated_by, update_user)
        self.assertIn(job, update_user.updated_jobs.all())


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .serializers import (
    JobSerializer, JobListSerializer, JobDetailSerializer,
    CompanySerializer, IndustrySerializer, JobTypeSerializer, CategorySerializer
)


class JobSerializerTest(APITestCase):
    """Test cases for Job serializers."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_admin=True
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Test Company',
            description='A test company',
            website='https://testcompany.com',
            email='contact@testcompany.com'
        )
        
        # Create test industry
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        
        # Create test job type
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            description='Full-time employment'
        )
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        self.category2 = Category.objects.create(
            name='Backend Development',
            description='Backend development jobs',
            parent=self.category1
        )
        
        # Create test job
        self.job = Job.objects.create(
            title='Senior Software Engineer',
            description='We are looking for a senior software engineer...',
            summary='Senior software engineer position',
            company=self.company,
            location='San Francisco, CA',
            salary_min=Decimal('80000.00'),
            salary_max=Decimal('120000.00'),
            salary_type='yearly',
            salary_currency='USD',
            job_type=self.job_type,
            industry=self.industry,
            experience_level='senior',
            required_skills='Python, Django, PostgreSQL',
            preferred_skills='React, Docker, AWS',
            created_by=self.user
        )
        self.job.categories.add(self.category1, self.category2)

    def test_company_serializer(self):
        """Test CompanySerializer serialization."""
        serializer = CompanySerializer(self.company)
        data = serializer.data
        
        self.assertEqual(data['id'], self.company.id)
        self.assertEqual(data['name'], 'Test Company')
        self.assertEqual(data['description'], 'A test company')
        self.assertEqual(data['website'], 'https://testcompany.com')
        self.assertEqual(data['email'], 'contact@testcompany.com')
        self.assertEqual(data['slug'], self.company.slug)
        self.assertIn('job_count', data)

    def test_industry_serializer(self):
        """Test IndustrySerializer serialization."""
        serializer = IndustrySerializer(self.industry)
        data = serializer.data
        
        self.assertEqual(data['id'], self.industry.id)
        self.assertEqual(data['name'], 'Technology')
        self.assertEqual(data['description'], 'Technology industry')
        self.assertEqual(data['slug'], self.industry.slug)
        self.assertIn('job_count', data)

    def test_job_type_serializer(self):
        """Test JobTypeSerializer serialization."""
        serializer = JobTypeSerializer(self.job_type)
        data = serializer.data
        
        self.assertEqual(data['id'], self.job_type.id)
        self.assertEqual(data['name'], 'Full-time')
        self.assertEqual(data['code'], 'full-time')
        self.assertEqual(data['description'], 'Full-time employment')
        self.assertEqual(data['slug'], self.job_type.slug)
        self.assertIn('job_count', data)

    def test_category_serializer(self):
        """Test CategorySerializer serialization."""
        serializer = CategorySerializer(self.category2)
        data = serializer.data
        
        self.assertEqual(data['id'], self.category2.id)
        self.assertEqual(data['name'], 'Backend Development')
        self.assertEqual(data['description'], 'Backend development jobs')
        self.assertEqual(data['slug'], self.category2.slug)
        self.assertEqual(data['parent'], self.category1.id)
        self.assertIn('job_count', data)
        self.assertIn('full_path', data)
        self.assertIn('level', data)

    def test_job_list_serializer(self):
        """Test JobListSerializer for optimized job listings."""
        serializer = JobListSerializer(self.job)
        data = serializer.data
        
        # Test basic fields
        self.assertEqual(data['id'], self.job.id)
        self.assertEqual(data['title'], 'Senior Software Engineer')
        self.assertEqual(data['summary'], 'Senior software engineer position')
        self.assertEqual(data['location'], 'San Francisco, CA')
        self.assertFalse(data['is_remote'])
        
        # Test company fields
        self.assertEqual(data['company_name'], 'Test Company')
        self.assertEqual(data['industry_name'], 'Technology')
        self.assertEqual(data['job_type_name'], 'Full-time')
        self.assertEqual(data['job_type_code'], 'full-time')
        
        # Test computed fields
        self.assertIn('salary_display', data)
        self.assertIn('days_since_posted', data)
        self.assertIn('is_new', data)
        self.assertIn('is_urgent', data)
        self.assertIn('can_apply', data)
        self.assertIn('category_names', data)
        self.assertIn('required_skills_list', data)
        
        # Test that category_names contains expected categories
        expected_categories = ['Software Development', 'Backend Development']
        self.assertEqual(sorted(data['category_names']), sorted(expected_categories))

    def test_job_serializer_read(self):
        """Test JobSerializer for reading job data."""
        serializer = JobSerializer(self.job)
        data = serializer.data
        
        # Test basic fields
        self.assertEqual(data['id'], self.job.id)
        self.assertEqual(data['title'], 'Senior Software Engineer')
        self.assertEqual(data['description'], 'We are looking for a senior software engineer...')
        self.assertEqual(data['location'], 'San Francisco, CA')
        
        # Test nested serializers
        self.assertIsInstance(data['company'], dict)
        self.assertEqual(data['company']['name'], 'Test Company')
        self.assertIsInstance(data['industry'], dict)
        self.assertEqual(data['industry']['name'], 'Technology')
        self.assertIsInstance(data['job_type'], dict)
        self.assertEqual(data['job_type']['name'], 'Full-time')
        self.assertIsInstance(data['categories'], list)
        self.assertEqual(len(data['categories']), 2)
        
        # Test salary fields
        self.assertEqual(data['salary_min'], '80000.00')
        self.assertEqual(data['salary_max'], '120000.00')
        self.assertEqual(data['salary_type'], 'yearly')
        self.assertEqual(data['salary_currency'], 'USD')
        
        # Test computed fields
        self.assertIn('salary_display', data)
        self.assertIn('days_since_posted', data)
        self.assertIn('is_new', data)
        self.assertIn('can_apply', data)

    def test_job_serializer_create_valid_data(self):
        """Test JobSerializer for creating a job with valid data."""
        job_data = {
            'title': 'Python Developer',
            'description': 'Looking for a Python developer...',
            'summary': 'Python developer position',
            'location': 'New York, NY',
            'is_remote': False,
            'salary_min': '70000.00',
            'salary_max': '90000.00',
            'salary_type': 'yearly',
            'salary_currency': 'USD',
            'experience_level': 'mid',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [self.category1.id, self.category2.id],
            'required_skills_list': ['Python', 'Flask', 'MySQL'],
            'preferred_skills_list': ['Docker', 'AWS'],
            'is_active': True
        }
        
        # Mock request context
        from unittest.mock import Mock
        request = Mock()
        request.user = self.admin_user
        
        serializer = JobSerializer(data=job_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        
        # Verify job was created correctly
        self.assertEqual(job.title, 'Python Developer')
        self.assertEqual(job.description, 'Looking for a Python developer...')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.industry, self.industry)
        self.assertEqual(job.job_type, self.job_type)
        self.assertEqual(job.created_by, self.admin_user)
        self.assertEqual(job.updated_by, self.admin_user)
        self.assertEqual(job.required_skills, 'Python, Flask, MySQL')
        self.assertEqual(job.preferred_skills, 'Docker, AWS')
        
        # Verify categories were set
        job_categories = list(job.categories.all())
        self.assertIn(self.category1, job_categories)
        self.assertIn(self.category2, job_categories)

    def test_job_serializer_create_minimal_data(self):
        """Test JobSerializer for creating a job with minimal required data."""
        job_data = {
            'title': 'Junior Developer',
            'description': 'Entry level developer position',
            'location': 'Remote',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        # Mock request context
        from unittest.mock import Mock
        request = Mock()
        request.user = self.admin_user
        
        serializer = JobSerializer(data=job_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        
        # Verify job was created with defaults
        self.assertEqual(job.title, 'Junior Developer')
        self.assertEqual(job.description, 'Entry level developer position')
        self.assertEqual(job.location, 'Remote')
        self.assertEqual(job.experience_level, 'mid')  # default
        self.assertEqual(job.salary_type, 'yearly')  # default
        self.assertTrue(job.is_active)  # default
        self.assertFalse(job.is_featured)  # default

    def test_job_serializer_validation_invalid_company(self):
        """Test JobSerializer validation with invalid company ID."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': 99999,  # Non-existent company
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_id', serializer.errors)

    def test_job_serializer_validation_invalid_industry(self):
        """Test JobSerializer validation with invalid industry ID."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': 99999,  # Non-existent industry
            'job_type_id': self.job_type.id
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('industry_id', serializer.errors)

    def test_job_serializer_validation_invalid_job_type(self):
        """Test JobSerializer validation with invalid job type ID."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': 99999  # Non-existent job type
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('job_type_id', serializer.errors)

    def test_job_serializer_validation_invalid_categories(self):
        """Test JobSerializer validation with invalid category IDs."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [99999, 99998]  # Non-existent categories
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category_ids', serializer.errors)

    def test_job_serializer_validation_duplicate_categories(self):
        """Test JobSerializer validation with duplicate category IDs."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [self.category1.id, self.category1.id]  # Duplicate
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category_ids', serializer.errors)

    def test_job_serializer_validation_salary_range(self):
        """Test JobSerializer validation for salary range."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'salary_min': '100000.00',
            'salary_max': '80000.00'  # Max less than min
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('salary_min', serializer.errors)

    def test_job_serializer_validation_past_application_deadline(self):
        """Test JobSerializer validation for past application deadline."""
        past_date = timezone.now() - timedelta(days=1)
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'application_deadline': past_date.isoformat()
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('application_deadline', serializer.errors)

    def test_job_serializer_validation_skills_list_too_long(self):
        """Test JobSerializer validation for skills list exceeding maximum."""
        long_skills_list = [f'Skill{i}' for i in range(25)]  # More than 20 skills
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'required_skills_list': long_skills_list
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('required_skills_list', serializer.errors)

    def test_job_serializer_validation_skills_list_duplicates(self):
        """Test JobSerializer validation removes duplicate skills."""
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'required_skills_list': ['Python', 'Django', 'Python', 'Flask']  # Duplicate Python
        }
        
        # Mock request context
        from unittest.mock import Mock
        request = Mock()
        request.user = self.admin_user
        
        serializer = JobSerializer(data=job_data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        
        # Verify duplicates were removed
        skills_list = job.get_required_skills_list()
        self.assertEqual(len(skills_list), 3)  # Python should appear only once
        self.assertIn('Python', skills_list)
        self.assertIn('Django', skills_list)
        self.assertIn('Flask', skills_list)

    def test_job_serializer_update(self):
        """Test JobSerializer for updating an existing job."""
        update_data = {
            'title': 'Updated Senior Software Engineer',
            'description': 'Updated job description',
            'salary_min': '90000.00',
            'salary_max': '130000.00',
            'required_skills_list': ['Python', 'Django', 'Redis'],
            'category_ids': [self.category1.id]  # Remove one category
        }
        
        # Mock request context
        from unittest.mock import Mock
        request = Mock()
        request.user = self.admin_user
        
        serializer = JobSerializer(
            self.job, 
            data=update_data, 
            partial=True, 
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_job = serializer.save()
        
        # Verify updates
        self.assertEqual(updated_job.title, 'Updated Senior Software Engineer')
        self.assertEqual(updated_job.description, 'Updated job description')
        self.assertEqual(updated_job.salary_min, Decimal('90000.00'))
        self.assertEqual(updated_job.salary_max, Decimal('130000.00'))
        self.assertEqual(updated_job.required_skills, 'Python, Django, Redis')
        self.assertEqual(updated_job.updated_by, self.admin_user)
        
        # Verify categories were updated
        job_categories = list(updated_job.categories.all())
        self.assertEqual(len(job_categories), 1)
        self.assertIn(self.category1, job_categories)
        self.assertNotIn(self.category2, job_categories)

    def test_job_detail_serializer(self):
        """Test JobDetailSerializer includes additional fields."""
        serializer = JobDetailSerializer(self.job)
        data = serializer.data
        
        # Test that it includes all JobSerializer fields
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('company', data)
        
        # Test additional fields specific to detail view
        self.assertIn('required_skills_list', data)
        self.assertIn('preferred_skills_list', data)
        self.assertIn('is_application_deadline_passed', data)
        
        # Verify skills lists are properly formatted
        expected_required_skills = ['Python', 'Django', 'PostgreSQL']
        expected_preferred_skills = ['React', 'Docker', 'AWS']
        self.assertEqual(data['required_skills_list'], expected_required_skills)
        self.assertEqual(data['preferred_skills_list'], expected_preferred_skills)

    def test_job_serializer_inactive_company_validation(self):
        """Test JobSerializer validation with inactive company."""
        # Make company inactive
        self.company.is_active = False
        self.company.save()
        
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_id', serializer.errors)
        self.assertIn('not active', str(serializer.errors['company_id'][0]))

    def test_job_serializer_inactive_industry_validation(self):
        """Test JobSerializer validation with inactive industry."""
        # Make industry inactive
        self.industry.is_active = False
        self.industry.save()
        
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('industry_id', serializer.errors)
        self.assertIn('not active', str(serializer.errors['industry_id'][0]))

    def test_job_serializer_inactive_job_type_validation(self):
        """Test JobSerializer validation with inactive job type."""
        # Make job type inactive
        self.job_type.is_active = False
        self.job_type.save()
        
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('job_type_id', serializer.errors)
        self.assertIn('not active', str(serializer.errors['job_type_id'][0]))

    def test_job_serializer_inactive_categories_validation(self):
        """Test JobSerializer validation with inactive categories."""
        # Make category inactive
        self.category1.is_active = False
        self.category1.save()
        
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [self.category1.id, self.category2.id]
        }
        
        serializer = JobSerializer(data=job_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('category_ids', serializer.errors)
        self.assertIn('not active', str(serializer.errors['category_ids'][0]))


from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch


class JobAPITest(APITestCase):
    """Test cases for Job API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_admin=True
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Test Company',
            description='A test company',
            website='https://testcompany.com'
        )
        
        # Create test industry
        self.industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        
        # Create test job type
        self.job_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            description='Full-time employment'
        )
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        self.category2 = Category.objects.create(
            name='Backend Development',
            description='Backend development jobs',
            parent=self.category1
        )
        
        # Create test jobs
        self.job1 = Job.objects.create(
            title='Senior Software Engineer',
            description='We are looking for a senior software engineer...',
            summary='Senior software engineer position',
            company=self.company,
            location='San Francisco, CA',
            salary_min=Decimal('80000.00'),
            salary_max=Decimal('120000.00'),
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.admin_user
        )
        self.job1.categories.add(self.category1, self.category2)
        
        self.job2 = Job.objects.create(
            title='Junior Developer',
            description='Entry level developer position',
            company=self.company,
            location='Remote',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.regular_user
        )
        
        # API client
        self.client = APIClient()

    def test_job_list_unauthenticated(self):
        """Test that unauthenticated users cannot access job list."""
        url = reverse('jobs:job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_job_list_authenticated(self):
        """Test job list endpoint for authenticated users."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
        # Check that jobs are ordered by created_at descending
        jobs = response.data['results']
        self.assertEqual(jobs[0]['title'], 'Junior Developer')  # Created second
        self.assertEqual(jobs[1]['title'], 'Senior Software Engineer')  # Created first

    def test_job_list_pagination(self):
        """Test job list pagination."""
        # Create more jobs to test pagination
        for i in range(25):
            Job.objects.create(
                title=f'Test Job {i}',
                description=f'Test job description {i}',
                company=self.company,
                location='Test Location',
                job_type=self.job_type,
                industry=self.industry,
                created_by=self.admin_user
            )
        
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 20)  # PAGE_SIZE = 20

    def test_job_list_filtering_by_location(self):
        """Test job list filtering by location."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        # Filter by exact location
        response = self.client.get(url, {'location': 'Remote'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Junior Developer')
        
        # Filter by location containing text
        response = self.client.get(url, {'location__icontains': 'San Francisco'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Software Engineer')

    def test_job_list_filtering_by_salary(self):
        """Test job list filtering by salary range."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        # Filter by minimum salary
        response = self.client.get(url, {'salary_min__gte': '70000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Software Engineer')

    def test_job_list_search(self):
        """Test job list search functionality."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        # Search by title
        response = self.client.get(url, {'search': 'Senior'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Software Engineer')
        
        # Search by company name
        response = self.client.get(url, {'search': 'Test Company'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_job_list_ordering(self):
        """Test job list ordering."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        # Order by title ascending
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jobs = response.data['results']
        self.assertEqual(jobs[0]['title'], 'Junior Developer')
        self.assertEqual(jobs[1]['title'], 'Senior Software Engineer')
        
        # Order by title descending
        response = self.client.get(url, {'ordering': '-title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jobs = response.data['results']
        self.assertEqual(jobs[0]['title'], 'Senior Software Engineer')
        self.assertEqual(jobs[1]['title'], 'Junior Developer')

    def test_job_detail_authenticated(self):
        """Test job detail endpoint for authenticated users."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        # Get initial view count
        initial_views = self.job1.views_count
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response data
        self.assertEqual(response.data['id'], self.job1.id)
        self.assertEqual(response.data['title'], 'Senior Software Engineer')
        self.assertIn('company', response.data)
        self.assertIn('industry', response.data)
        self.assertIn('job_type', response.data)
        self.assertIn('categories', response.data)
        
        # Check that view count was incremented
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.views_count, initial_views + 1)

    def test_job_create_admin_user(self):
        """Test job creation by admin user."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-list')
        
        job_data = {
            'title': 'Python Developer',
            'description': 'Looking for a Python developer...',
            'summary': 'Python developer position',
            'location': 'New York, NY',
            'salary_min': '70000.00',
            'salary_max': '90000.00',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [self.category1.id],
            'required_skills_list': ['Python', 'Django'],
            'is_active': True
        }
        
        response = self.client.post(url, job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that job was created
        self.assertTrue(Job.objects.filter(title='Python Developer').exists())
        created_job = Job.objects.get(title='Python Developer')
        self.assertEqual(created_job.created_by, self.admin_user)
        self.assertEqual(created_job.updated_by, self.admin_user)
        self.assertEqual(created_job.required_skills, 'Python, Django')

    def test_job_create_regular_user_forbidden(self):
        """Test that regular users cannot create jobs."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        job_data = {
            'title': 'Test Job',
            'description': 'Test description',
            'location': 'Test Location',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id
        }
        
        response = self.client.post(url, job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only administrators can create job postings', response.data['error'])

    def test_job_create_validation_errors(self):
        """Test job creation with validation errors."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-list')
        
        # Missing required fields
        job_data = {
            'title': 'Test Job'
            # Missing required fields
        }
        
        response = self.client.post(url, job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)
        self.assertIn('location', response.data)
        self.assertIn('company_id', response.data)

    def test_job_update_by_admin(self):
        """Test job update by admin user."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        update_data = {
            'title': 'Updated Senior Software Engineer',
            'salary_min': '90000.00'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that job was updated
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.title, 'Updated Senior Software Engineer')
        self.assertEqual(self.job1.salary_min, Decimal('90000.00'))
        self.assertEqual(self.job1.updated_by, self.admin_user)

    def test_job_update_by_creator(self):
        """Test job update by job creator."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job2.pk})
        
        update_data = {
            'title': 'Updated Junior Developer',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that job was updated
        self.job2.refresh_from_db()
        self.assertEqual(self.job2.title, 'Updated Junior Developer')
        self.assertEqual(self.job2.description, 'Updated description')

    def test_job_update_by_unauthorized_user(self):
        """Test that unauthorized users cannot update jobs."""
        # Create another regular user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        update_data = {'title': 'Unauthorized Update'}
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # The permission class returns a standard DRF permission denied response
        self.assertIn('detail', response.data)

    def test_job_delete_by_admin(self):
        """Test job deletion (soft delete) by admin user."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that job was soft deleted
        self.job1.refresh_from_db()
        self.assertFalse(self.job1.is_active)
        self.assertEqual(self.job1.updated_by, self.admin_user)

    def test_job_delete_by_creator(self):
        """Test job deletion by job creator."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job2.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check that job was soft deleted
        self.job2.refresh_from_db()
        self.assertFalse(self.job2.is_active)

    def test_job_delete_by_unauthorized_user(self):
        """Test that unauthorized users cannot delete jobs."""
        # Create another regular user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=other_user)
        url = reverse('jobs:job-detail', kwargs={'pk': self.job1.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # The permission class returns a standard DRF permission denied response
        self.assertIn('detail', response.data)

    def test_job_toggle_featured_admin_only(self):
        """Test toggle featured action (admin only)."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-toggle-featured', kwargs={'pk': self.job1.pk})
        
        # Initially not featured
        self.assertFalse(self.job1.is_featured)
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_featured'])
        
        # Check database
        self.job1.refresh_from_db()
        self.assertTrue(self.job1.is_featured)
        
        # Toggle again
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_featured'])

    def test_job_toggle_featured_regular_user_forbidden(self):
        """Test that regular users cannot toggle featured status."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-toggle-featured', kwargs={'pk': self.job1.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Only administrators can feature jobs', response.data['error'])

    def test_job_reactivate_by_admin(self):
        """Test job reactivation by admin."""
        # First deactivate the job
        self.job1.is_active = False
        self.job1.save()
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-reactivate', kwargs={'pk': self.job1.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])
        
        # Check database
        self.job1.refresh_from_db()
        self.assertTrue(self.job1.is_active)

    def test_job_reactivate_already_active(self):
        """Test reactivating an already active job."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-reactivate', kwargs={'pk': self.job1.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Job is already active', response.data['error'])

    def test_admin_can_see_inactive_jobs(self):
        """Test that admins can see inactive jobs with query parameter."""
        # Deactivate a job
        self.job1.is_active = False
        self.job1.save()
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('jobs:job-list')
        
        # Without include_inactive parameter
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)  # Only active job
        
        # With include_inactive parameter
        response = self.client.get(url, {'include_inactive': 'true'})
        self.assertEqual(len(response.data['results']), 2)  # Both jobs

    def test_regular_user_cannot_see_inactive_jobs(self):
        """Test that regular users cannot see inactive jobs even with parameter."""
        # Deactivate a job
        self.job1.is_active = False
        self.job1.save()
        
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('jobs:job-list')
        
        # With include_inactive parameter (should be ignored)
        response = self.client.get(url, {'include_inactive': 'true'})
        self.assertEqual(len(response.data['results']), 1)  # Only active job


class CompanyAPITest(APITestCase):
    """Test cases for Company API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.company1 = Company.objects.create(
            name='Tech Company',
            description='A technology company'
        )
        self.company2 = Company.objects.create(
            name='Finance Corp',
            description='A finance company'
        )
        self.client = APIClient()

    def test_company_list_public_access(self):
        """Test that company list is publicly accessible."""
        url = reverse('jobs:company-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_company_detail_public_access(self):
        """Test that company detail is publicly accessible."""
        url = reverse('jobs:company-detail', kwargs={'pk': self.company1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tech Company')

    def test_company_search(self):
        """Test company search functionality."""
        url = reverse('jobs:company-list')
        response = self.client.get(url, {'search': 'Tech'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Tech Company')


class CategoryAPITest(APITestCase):
    """Test cases for Category API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.parent_category = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        self.child_category = Category.objects.create(
            name='Backend Development',
            description='Backend development jobs',
            parent=self.parent_category
        )
        
        # Create test data for jobs endpoint
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.company = Company.objects.create(name='Test Company')
        self.industry = Industry.objects.create(name='Technology')
        self.job_type = JobType.objects.create(name='Full-time', code='full-time')
        
        self.job = Job.objects.create(
            title='Test Job',
            description='Test description',
            company=self.company,
            location='Test Location',
            job_type=self.job_type,
            industry=self.industry,
            created_by=self.user
        )
        self.job.categories.add(self.child_category)
        
        self.client = APIClient()

    def test_category_list_public_access(self):
        """Test that category list is publicly accessible."""
        url = reverse('jobs:category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_category_detail_public_access(self):
        """Test that category detail is publicly accessible."""
        url = reverse('jobs:category-detail', kwargs={'pk': self.parent_category.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Software Development')

    def test_category_jobs_endpoint(self):
        """Test category jobs endpoint."""
        url = reverse('jobs:category-jobs', kwargs={'pk': self.parent_category.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include jobs from child categories too
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Job')

    def test_category_filtering_by_parent(self):
        """Test category filtering by parent."""
        url = reverse('jobs:category-list')
        response = self.client.get(url, {'parent': self.parent_category.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Backend Development')


class JobFilteringAndSearchTest(APITestCase):
    """Test cases for advanced job filtering and search functionality."""

    def setUp(self):
        """Set up test data for filtering and search tests."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test companies
        self.company1 = Company.objects.create(
            name='Tech Startup',
            description='A technology startup',
            founded_year=2020,
            employee_count='10-50'
        )
        self.company2 = Company.objects.create(
            name='Finance Corp',
            description='A finance corporation',
            founded_year=2010,
            employee_count='500+'
        )
        
        # Create test industries
        self.tech_industry = Industry.objects.create(
            name='Technology',
            description='Technology industry'
        )
        self.finance_industry = Industry.objects.create(
            name='Finance',
            description='Finance industry'
        )
        
        # Create test job types
        self.fulltime_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            description='Full-time employment'
        )
        self.contract_type = JobType.objects.create(
            name='Contract',
            code='contract',
            description='Contract employment'
        )
        
        # Create test categories
        self.dev_category = Category.objects.create(
            name='Software Development',
            description='Software development jobs'
        )
        self.backend_category = Category.objects.create(
            name='Backend Development',
            description='Backend development jobs',
            parent=self.dev_category
        )
        self.frontend_category = Category.objects.create(
            name='Frontend Development',
            description='Frontend development jobs',
            parent=self.dev_category
        )
        
        # Create test jobs with different attributes
        self.job1 = Job.objects.create(
            title='Senior Python Developer',
            description='Looking for a senior Python developer with Django experience',
            summary='Senior Python developer position',
            company=self.company1,
            location='San Francisco, CA',
            is_remote=False,
            salary_min=Decimal('90000.00'),
            salary_max=Decimal('130000.00'),
            salary_type='yearly',
            experience_level='senior',
            job_type=self.fulltime_type,
            industry=self.tech_industry,
            required_skills='Python, Django, PostgreSQL',
            preferred_skills='React, Docker, AWS',
            is_featured=True,
            created_by=self.user
        )
        self.job1.categories.add(self.backend_category)
        
        self.job2 = Job.objects.create(
            title='Frontend React Developer',
            description='React developer needed for modern web applications',
            summary='React developer position',
            company=self.company1,
            location='Remote',
            is_remote=True,
            salary_min=Decimal('70000.00'),
            salary_max=Decimal('100000.00'),
            salary_type='yearly',
            experience_level='mid',
            job_type=self.fulltime_type,
            industry=self.tech_industry,
            required_skills='JavaScript, React, CSS',
            preferred_skills='TypeScript, Node.js',
            created_by=self.user
        )
        self.job2.categories.add(self.frontend_category)
        
        self.job3 = Job.objects.create(
            title='Financial Analyst',
            description='Financial analyst position for investment analysis',
            summary='Financial analyst role',
            company=self.company2,
            location='New York, NY',
            is_remote=False,
            salary_min=Decimal('60000.00'),
            salary_max=Decimal('80000.00'),
            salary_type='yearly',
            experience_level='entry',
            job_type=self.contract_type,
            industry=self.finance_industry,
            required_skills='Excel, Financial Modeling',
            preferred_skills='Python, SQL',
            created_by=self.user
        )
        
        self.job4 = Job.objects.create(
            title='Junior Python Developer',
            description='Entry level Python developer position',
            summary='Junior Python developer',
            company=self.company2,
            location='Austin, TX',
            is_remote=False,
            salary_min=Decimal('50000.00'),
            salary_max=Decimal('70000.00'),
            salary_type='yearly',
            experience_level='junior',
            job_type=self.fulltime_type,
            industry=self.tech_industry,
            required_skills='Python, Git',
            preferred_skills='Django, Flask',
            created_by=self.user
        )
        self.job4.categories.add(self.backend_category)
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_filter_by_location_exact(self):
        """Test filtering jobs by exact location."""
        url = reverse('jobs:job-list')
        response = self.client.get(url, {'location_exact': 'Remote'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Frontend React Developer')

    def test_filter_by_location_contains(self):
        """Test filtering jobs by location containing text."""
        url = reverse('jobs:job-list')
        response = self.client.get(url, {'location': 'San Francisco'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_filter_by_remote_work(self):
        """Test filtering jobs by remote work option."""
        url = reverse('jobs:job-list')
        
        # Filter for remote jobs
        response = self.client.get(url, {'is_remote': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Frontend React Developer')
        
        # Filter for non-remote jobs
        response = self.client.get(url, {'is_remote': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_by_salary_range(self):
        """Test filtering jobs by salary range."""
        url = reverse('jobs:job-list')
        
        # Filter by minimum salary
        response = self.client.get(url, {'salary_min_gte': '80000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
        
        # Filter by maximum salary
        response = self.client.get(url, {'salary_max_lte': '80000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Financial Analyst and Junior Python Developer

    def test_filter_by_experience_level(self):
        """Test filtering jobs by experience level."""
        url = reverse('jobs:job-list')
        
        # Filter for senior level jobs
        response = self.client.get(url, {'experience_level': 'senior'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
        
        # Filter for multiple experience levels
        response = self.client.get(url, {'experience_levels': ['junior', 'mid']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_company(self):
        """Test filtering jobs by company."""
        url = reverse('jobs:job-list')
        
        response = self.client.get(url, {'company': self.company1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter by company name
        response = self.client.get(url, {'company_name': 'Tech'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_industry_and_job_type(self):
        """Test filtering jobs by industry and job type."""
        url = reverse('jobs:job-list')
        
        # Filter by industry
        response = self.client.get(url, {'industry': self.tech_industry.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Filter by job type
        response = self.client.get(url, {'job_type': self.contract_type.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Financial Analyst')

    def test_filter_by_categories(self):
        """Test filtering jobs by categories."""
        url = reverse('jobs:job-list')
        
        # Filter by single category
        response = self.client.get(url, {'categories': self.backend_category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter by multiple categories (OR logic)
        response = self.client.get(url, {
            'categories': [self.backend_category.id, self.frontend_category.id]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_filter_by_category_slug(self):
        """Test filtering jobs by category slug."""
        url = reverse('jobs:job-list')
        
        response = self.client.get(url, {'category_slug': self.backend_category.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_featured_status(self):
        """Test filtering jobs by featured status."""
        url = reverse('jobs:job-list')
        
        response = self.client.get(url, {'is_featured': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_filter_by_skills(self):
        """Test filtering jobs by required and preferred skills."""
        url = reverse('jobs:job-list')
        
        # Filter by required skills
        response = self.client.get(url, {'required_skills': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter by preferred skills
        response = self.client.get(url, {'preferred_skills': 'Docker'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_advanced_search_functionality(self):
        """Test advanced search across multiple fields."""
        url = reverse('jobs:job-list')
        
        # Search by title
        response = self.client.get(url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Search by company name
        response = self.client.get(url, {'search': 'Tech Startup'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Search by description
        response = self.client.get(url, {'search': 'Django'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_combined_filtering(self):
        """Test combining multiple filters."""
        url = reverse('jobs:job-list')
        
        # Combine industry, experience level, and salary filters
        response = self.client.get(url, {
            'industry': self.tech_industry.id,
            'experience_level': 'senior',
            'salary_min_gte': '80000'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_ordering_functionality(self):
        """Test job ordering options."""
        url = reverse('jobs:job-list')
        
        # Order by title ascending
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [job['title'] for job in response.data['results']]
        self.assertEqual(titles, sorted(titles))
        
        # Order by salary descending
        response = self.client.get(url, {'ordering': '-salary_max'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_recent_jobs_filter(self):
        """Test filtering for recently posted jobs."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create an old job
        old_job = Job.objects.create(
            title='Old Job',
            description='An old job posting',
            company=self.company1,
            location='Test Location',
            job_type=self.fulltime_type,
            industry=self.tech_industry,
            created_by=self.user
        )
        # Manually set created_at to 10 days ago
        old_date = timezone.now() - timedelta(days=10)
        Job.objects.filter(id=old_job.id).update(created_at=old_date)
        
        url = reverse('jobs:job-list')
        
        # Filter for jobs posted in last 7 days
        response = self.client.get(url, {'posted_days_ago': '7'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not include the old job
        titles = [job['title'] for job in response.data['results']]
        self.assertNotIn('Old Job', titles)

    def test_salary_range_filtering_edge_cases(self):
        """Test salary range filtering with edge cases."""
        url = reverse('jobs:job-list')
        
        # Test salary_range_min filter
        response = self.client.get(url, {'salary_range_min': '75000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include jobs where min salary >= 75000 or max salary >= 75000
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # Test salary_range_max filter
        response = self.client.get(url, {'salary_range_max': '75000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include jobs where max salary <= 75000 or min salary <= 75000
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_category_hierarchy_filtering(self):
        """Test filtering by category hierarchy."""
        url = reverse('jobs:job-list')
        
        # Filter by parent category should include jobs from child categories
        response = self.client.get(url, {'category_hierarchy': self.dev_category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include jobs from both backend and frontend categories
        self.assertEqual(len(response.data['results']), 3)

    def test_location_based_filtering(self):
        """Test location-based filtering."""
        url = reverse('jobs:job-list')
        
        # Test near_location filter
        response = self.client.get(url, {'near_location': 'San Francisco'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')

    def test_custom_action_endpoints(self):
        """Test custom action endpoints for jobs."""
        # Test featured jobs endpoint
        featured_url = reverse('jobs:job-featured')
        response = self.client.get(featured_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Senior Python Developer')
        
        # Test recent jobs endpoint
        recent_url = reverse('jobs:job-recent')
        response = self.client.get(recent_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 4)
        
        # Test recent jobs with custom days parameter
        response = self.client.get(recent_url, {'days': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test popular jobs endpoint
        popular_url = reverse('jobs:job-popular')
        response = self.client.get(popular_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test similar jobs endpoint
        similar_url = reverse('jobs:job-similar')
        response = self.client.get(similar_url, {'job_id': self.job1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find similar jobs based on industry, job_type, or categories
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # Test similar jobs with invalid job_id
        response = self.client.get(similar_url, {'job_id': 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test similar jobs without job_id parameter
        response = self.client.get(similar_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_endpoint(self):
        """Test the dedicated search endpoint."""
        search_url = reverse('jobs:job-search')
        
        # Test search with query parameter
        response = self.client.get(search_url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test search with additional filters
        response = self.client.get(search_url, {
            'search': 'Python',
            'experience_level': 'senior'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_validation_and_error_handling(self):
        """Test filter validation and error handling."""
        url = reverse('jobs:job-list')
        
        # Test with invalid company ID
        response = self.client.get(url, {'company': 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
        # Test with invalid industry ID
        response = self.client.get(url, {'industry': 99999})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
        # Test with invalid experience level
        response = self.client.get(url, {'experience_level': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)