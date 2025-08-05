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
        """Test job_count property (will be 0 until Job model is implemented)."""
        company = Company.objects.create(name='Test Company')
        # Since Job model isn't implemented yet, this should return 0
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
