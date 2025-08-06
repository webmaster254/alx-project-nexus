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