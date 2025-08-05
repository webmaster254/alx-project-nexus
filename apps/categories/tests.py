from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from .models import Industry, JobType


class IndustryModelTest(TestCase):
    """Test cases for the Industry model."""

    def setUp(self):
        """Set up test data."""
        self.industry_data = {
            'name': 'Technology',
            'description': 'Software development, IT services, and technology companies'
        }

    def test_create_industry(self):
        """Test creating an industry with all fields."""
        industry = Industry.objects.create(**self.industry_data)
        
        self.assertEqual(industry.name, 'Technology')
        self.assertEqual(industry.description, 'Software development, IT services, and technology companies')
        self.assertTrue(industry.is_active)
        self.assertIsNotNone(industry.created_at)
        self.assertIsNotNone(industry.updated_at)

    def test_create_industry_minimal(self):
        """Test creating an industry with only required fields."""
        industry = Industry.objects.create(name='Healthcare')
        
        self.assertEqual(industry.name, 'Healthcare')
        self.assertEqual(industry.description, '')
        self.assertTrue(industry.is_active)

    def test_industry_name_unique_constraint(self):
        """Test that industry name must be unique."""
        Industry.objects.create(name='Finance')
        
        with self.assertRaises(IntegrityError):
            Industry.objects.create(name='Finance')

    def test_industry_name_max_length(self):
        """Test industry name max length validation."""
        long_name = 'A' * 101  # Exceeds max_length of 100
        industry = Industry(name=long_name)
        
        with self.assertRaises(ValidationError):
            industry.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from industry name."""
        industry = Industry.objects.create(name='Information Technology')
        expected_slug = slugify('Information Technology')
        self.assertEqual(industry.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        Industry.objects.create(name='Technology', slug='tech')
        
        with self.assertRaises(IntegrityError):
            Industry.objects.create(name='Tech Industry', slug='tech')

    def test_custom_slug(self):
        """Test creating industry with custom slug."""
        industry = Industry.objects.create(
            name='Technology',
            slug='custom-tech-slug'
        )
        self.assertEqual(industry.slug, 'custom-tech-slug')

    def test_str_representation(self):
        """Test string representation of industry."""
        industry = Industry.objects.create(name='Technology')
        self.assertEqual(str(industry), 'Technology')

    def test_job_count_property(self):
        """Test job_count property (will be 0 until Job model is implemented)."""
        industry = Industry.objects.create(name='Technology')
        # Since Job model isn't implemented yet, this should return 0
        self.assertEqual(industry.job_count, 0)

    def test_is_active_field(self):
        """Test is_active field functionality."""
        industry = Industry.objects.create(name='Technology')
        self.assertTrue(industry.is_active)
        
        industry.is_active = False
        industry.save()
        industry.refresh_from_db()
        self.assertFalse(industry.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        Industry.objects.create(name='Zebra Industry')
        Industry.objects.create(name='Alpha Industry')
        Industry.objects.create(name='Beta Industry')
        
        industries = list(Industry.objects.all())
        industry_names = [industry.name for industry in industries]
        
        self.assertEqual(industry_names, ['Alpha Industry', 'Beta Industry', 'Zebra Industry'])


class JobTypeModelTest(TestCase):
    """Test cases for the JobType model."""

    def setUp(self):
        """Set up test data."""
        self.job_type_data = {
            'name': 'Full-time',
            'code': 'full-time',
            'description': 'Full-time employment with standard working hours'
        }

    def test_create_job_type(self):
        """Test creating a job type with all fields."""
        job_type = JobType.objects.create(**self.job_type_data)
        
        self.assertEqual(job_type.name, 'Full-time')
        self.assertEqual(job_type.code, 'full-time')
        self.assertEqual(job_type.description, 'Full-time employment with standard working hours')
        self.assertTrue(job_type.is_active)
        self.assertIsNotNone(job_type.created_at)
        self.assertIsNotNone(job_type.updated_at)

    def test_create_job_type_minimal(self):
        """Test creating a job type with only required fields."""
        job_type = JobType.objects.create(name='Part-time', code='part-time')
        
        self.assertEqual(job_type.name, 'Part-time')
        self.assertEqual(job_type.code, 'part-time')
        self.assertEqual(job_type.description, '')
        self.assertTrue(job_type.is_active)

    def test_job_type_name_unique_constraint(self):
        """Test that job type name must be unique."""
        JobType.objects.create(name='Contract', code='contract')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Contract', code='contract-2')

    def test_job_type_code_unique_constraint(self):
        """Test that job type code must be unique."""
        JobType.objects.create(name='Remote Work', code='remote')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Remote Position', code='remote')

    def test_job_type_name_max_length(self):
        """Test job type name max length validation."""
        long_name = 'A' * 51  # Exceeds max_length of 50
        job_type = JobType(name=long_name, code='test')
        
        with self.assertRaises(ValidationError):
            job_type.full_clean()

    def test_job_type_code_max_length(self):
        """Test job type code max length validation."""
        long_code = 'a' * 21  # Exceeds max_length of 20
        job_type = JobType(name='Test Type', code=long_code)
        
        with self.assertRaises(ValidationError):
            job_type.full_clean()

    def test_employment_type_choices(self):
        """Test that code field accepts valid employment type choices."""
        valid_codes = [
            'full-time', 'part-time', 'contract', 'temporary',
            'internship', 'freelance', 'remote', 'hybrid'
        ]
        
        for code in valid_codes:
            job_type_data = self.job_type_data.copy()
            job_type_data['code'] = code
            job_type_data['name'] = f'Test {code}'
            job_type = JobType(**job_type_data)
            try:
                job_type.full_clean()
            except ValidationError:
                self.fail(f"Valid employment type code {code} failed validation")

    def test_invalid_employment_type_choice(self):
        """Test that code field rejects invalid employment type choices."""
        invalid_codes = ['invalid-type', 'unknown', 'custom-type']
        
        for code in invalid_codes:
            job_type_data = self.job_type_data.copy()
            job_type_data['code'] = code
            job_type = JobType(**job_type_data)
            with self.assertRaises(ValidationError):
                job_type.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from job type name."""
        job_type = JobType.objects.create(name='Full-time Position', code='full-time')
        expected_slug = slugify('Full-time Position')
        self.assertEqual(job_type.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        JobType.objects.create(name='Full-time', code='full-time', slug='fulltime')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Fulltime', code='part-time', slug='fulltime')

    def test_custom_slug(self):
        """Test creating job type with custom slug."""
        job_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            slug='custom-fulltime-slug'
        )
        self.assertEqual(job_type.slug, 'custom-fulltime-slug')

    def test_str_representation(self):
        """Test string representation of job type."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        self.assertEqual(str(job_type), 'Full-time')

    def test_job_count_property(self):
        """Test job_count property (will be 0 until Job model is implemented)."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        # Since Job model isn't implemented yet, this should return 0
        self.assertEqual(job_type.job_count, 0)

    def test_is_active_field(self):
        """Test is_active field functionality."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        self.assertTrue(job_type.is_active)
        
        job_type.is_active = False
        job_type.save()
        job_type.refresh_from_db()
        self.assertFalse(job_type.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        JobType.objects.create(name='Zebra Type', code='zebra')
        JobType.objects.create(name='Alpha Type', code='alpha')
        JobType.objects.create(name='Beta Type', code='beta')
        
        job_types = list(JobType.objects.all())
        job_type_names = [job_type.name for job_type in job_types]
        
        self.assertEqual(job_type_names, ['Alpha Type', 'Beta Type', 'Zebra Type'])

    def test_employment_types_constant(self):
        """Test that EMPLOYMENT_TYPES constant contains expected values."""
        expected_types = [
            ('full-time', 'Full-time'),
            ('part-time', 'Part-time'),
            ('contract', 'Contract'),
            ('temporary', 'Temporary'),
            ('internship', 'Internship'),
            ('freelance', 'Freelance'),
            ('remote', 'Remote'),
            ('hybrid', 'Hybrid'),
        ]
        
        self.assertEqual(JobType.EMPLOYMENT_TYPES, expected_types)
